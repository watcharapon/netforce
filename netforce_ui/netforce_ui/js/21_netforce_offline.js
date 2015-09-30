var nf_offline_db_version=3;
var nf_db=null;

function nf_open_db(cb) {
    log("nf_open_db");
    if (!window.indexedDB) return;
    var ctx=get_global_context();
    if (!ctx.dbname) return;
    var req=window.indexedDB.open(ctx.dbname,nf_offline_db_version);
    req.onerror=function(e) {
        log("Failed to open db");
        if (cb) cb("error");
    };
    req.onsuccess=function(e) {
        log("Open db success");
        nf_db=e.target.result;
        if (cb) cb(null);
    };
    req.onupgradeneeded=function(e) {
        nf_db=e.target.result;
        nf_upgrade_db();
    };
}

function nf_upgrade_db() {
    log("nf_upgrade_db");
    _.each(nf_models,function(m,model_name) {
        if (!m.offline) return;
        if (!nf_db.objectStoreNames.contains(model_name)) {
            log("create object store",model_name);
            nf_db.createObjectStore(model_name,{autoIncrement:true});
        }
    });
}

function nf_execute_local(model,method,args,opts,cb) {
    log("nf_execute_local",model,method,args,opts);
    var all_stores=[];
    _.each(nf_db.objectStoreNames,function(n) {
        all_stores.push(n);
    });
    nf_trans=nf_db.transaction(all_stores,"readwrite");
    if (!nf_trans) {
        cb("Failed to start transaction");
        return;
    }
    m=new NFModelLocal();
    m.name=model;
    f=m[method];
    if (!f) {
        cb("Method not found: "+method+" of "+model);
        return;
    }
    var f_args=_.clone(args);
    f_args.push(opts);
    f_args.push(function(err,data) {
        if (err) {
            log("nf_execute_local ERROR",err);
        } else {
            log("nf_execute_local OK",data);
        }
        if (cb) cb(err,data);
    });
    f.apply(m,f_args);
}

NFModelLocal=function() {
}

_.extend(NFModelLocal.prototype,{
    create: function(vals,opts,cb) {
        log("NFModelLocal.create",vals,opts,cb);
        if (!opts) opts={};
        var store=nf_trans.objectStore(this.name);
        var req=store.add(vals);
        req.onsuccess=function(e) {
            var new_id=e.target.result;
            cb(null,new_id);
        };
        req.onerror=function(e) {
            cb("error: "+e.target.errorCode);
        };
    },

    write: function(ids,vals,opts,cb) {
        log("NFModelLocal.write",ids,vals);
        if (!opts) opts={};
        var store=nf_trans.objectStore(this.name);
        var tasks=[];
        _.each(ids,function(id) {
            tasks.push(function(cb) {
                var req=store.get(id);
                req.onsuccess=function(e) {
                    var old_vals=e.target.result;
                    var new_vals=_.extend({},old_vals,vals);
                    var req=store.put(new_vals,id);
                    req.onsuccess=function(e) {
                        cb(null);
                    };
                    req.on_error=function(e) {
                        cb("error: "+e.target.errorCode);
                    };
                };
                req.onerror=function(e) {
                    cb("error: "+e.target.errorCode);
                };
            });
        });
        async.parallel(tasks,function(err) {
            cb(err);
        });
    },

    read: function(ids,opts,cb) {
        log("NFModelLocal.read",ids,opts,cb);
        if (!opts) opts={};
        var field_names=opts.field_names;
        var that=this;
        var store=nf_trans.objectStore(this.name);
        var tasks=[];
        var id_vals={};
        _.each(ids,function(id) {
            tasks.push(function(cb) {
                var req=store.get(id);
                req.onsuccess=function(e) {
                    var all_vals=e.target.result;
                    if (!all_vals) {
                         cb("Invalid read data: "+that.name+","+id);
                         return;
                    }
                    var vals={id: id};
                    _.each(field_names,function(n) {
                        vals[n]=all_vals[n];
                    });
                    id_vals[id]=vals;
                    cb(null);
                };
                req.onerror=function(e) {
                    cb("error: "+e.target.errorCode);
                };
            });
        });
        async.parallel(tasks,function(err) {
            if (err) {
                cb(err);
                return;
            }
            var res=[];
            _.each(ids,function(id) {
                res.push(id_vals[id]);
            });
            cb(null,res);
        });
    },

    search: function(condition,opts,cb) {
        log("NFModelLocal.search",condition,opts,cb);
        if (!opts) opts={};
        var that=this;
        var store=nf_trans.objectStore(this.name);
        var req=store.openCursor();
        var ids=[];
        req.onsuccess=function(e) {
            var cr=e.target.result;
            if (!cr) {
                if (opts.count) {
                    cb(null,[ids,ids.length]); // XXX
                } else {
                    cb(null,ids);
                }
                return;
            }
            var vals=cr.value;
            if (that._check_condition(vals,condition)) {
                ids.push(cr.key);
            }
            cr["continue"]();
        };
        req.onerror=function(e) {
            cb("error: "+e.target.errorCode);
        };
    },

    _check_condition: function(vals,condition) {
        return _.every(condition,function(clause) {
            var field=clause[0];
            var op=clause[1];
            var op_val=clause[2];
            var val=vals[field];
            if (op=="=") {
                return val==op_val;
            } else if (op=="!=") {
                return val!=op_val;
            } else if (op=="in") {
                return _.contains(op_val,val);
            } else if (op=="not in") {
                return !_.contains(op_val,val);
            } else if (op=="<=") {
                return val<=op_val;
            } else if (op==">=") {
                return val>=op_val;
            } else if (op=="<") {
                return val<op_val;
            } else if (op==">") {
                return val>op_val;
            } else {
                throw "Invalid condition: "+condition;
            }
        });
    },

    search_read: function(condition,opts,cb) {
        log("NFModelLocal.search_read",condition,opts,cb);
        var that=this;
        this.search(condition,opts,function(err,data) {
            if (opts.count) {
                ids=data[0];
            } else {
                ids=data;
            }
            that.read(ids,opts,function(err,data2) {
                if (opts.count) {
                    var res=[data2,opts.count];
                } else {
                    var res=data2;
                }
                cb(null,res);
            });
        });
    },

    default_get: function(opts,cb) {
        var vals={};
        cb(null,vals);
    }
});

NFModelLocal.prototype["delete"]=function(ids,opts,cb) {
    log("NFModelLocal.delete",ids,opts,cb);
    if (!opts) opts={};
    var store=nf_trans.objectStore(this.name);
    var tasks=[];
    _.each(ids,function(id) {
        tasks.push(function(cb) {
            var req=store["delete"](id);
            req.onsuccess=function(e) {
                cb(null);
            };
            req.onerror=function(e) {
                cb("error: "+e.target.errorCode);
            };
        });
    });
    async.parallel(tasks,function(err) {
        cb(err);
    });
};
