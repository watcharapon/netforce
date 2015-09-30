/*
 * Copyright (c) 2012-2015 Netforce Co. Ltd.
 * 
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 * 
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 * 
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
 * EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
 * MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
 * IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
 * DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
 * OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
 * OR OTHER DEALINGS IN THE SOFTWARE.
 */

var ReportList=NFView.extend({
    _name: "report_list",
    events: {
        "click .drill-down": "drill_down"
    },

    render: function() {
        log("report_list render",this);
        var content=this.options.inner({context: this.context});
        var xml="<root>"+content+"</root>";
        var doc=$.parseXML(xml);
        var cols=[];
        var that=this;
        $(doc).find("root").children().each(function() {
            var $el=$(this);
            var tag=$el.prop("tagName");
            if (tag=="field") {
                var name=$el.attr("name");
                if (that.options.group && that.options.group==name) return;
                cols.push({
                    name: name,
                    group_operator: $el.attr("group_operator")
                });
            }
        });
        this.data.cols=cols;
        var collection=this.context.collection;
        if (!collection) {
            NFView.prototype.render.call(this);
            return;
        }
        var group_field=this.options.group_field || this.context.group_field;
        var subgroup_field=this.options.subgroup_field || this.context.subgroup_field;
        var view_type=this.options.view_type || this.context.view_type || "list";
        log("view_type",view_type);
        var hide_details=this.options.hide_details || this.context.hide_details;
        this.data.group_field=group_field;
        this.data.subgroup_field=subgroup_field;
        this.data.view_type=view_type;
        this.data.hide_details=hide_details;
        if (view_type=="list") {
            if (group_field) {
                var group_vals={};
                var groups=[];
                var subgroup_vals;
                collection.each(function(model) {
                    var record={};
                    var group_val=model.get(group_field);
                    var group=group_vals[group_val];
                    if (!group) {
                        var vals={};
                        vals[group_field]=group_val;
                        var group_model=new NFModel(vals,{name:model.name});
                        _.each(cols,function(col) {
                            if (col.group_operator) group_model.set(col.name,0);
                        });
                        group={
                            model: group_model
                        }
                        if (subgroup_field) {
                            group.subgroups=[];
                        } else {
                            group.records=[];
                        }
                        group_vals[group_val]=group;
                        groups.push(group);
                        subgroup_vals={};
                    }
                    if (subgroup_field) {
                        var subgroup_val=model.get(subgroup_field);
                        var subgroup=subgroup_vals[subgroup_val];
                        if (!subgroup) {
                            var vals={};
                            vals[subgroup_field]=subgroup_val;
                            var subgroup_model=new NFModel(vals,{name:model.name});
                            _.each(cols,function(col) {
                                if (col.group_operator) subgroup_model.set(col.name,0);
                            });
                            subgroup={
                                model: subgroup_model,
                                records: []
                            }
                            subgroup_vals[subgroup_val]=subgroup;
                            group.subgroups.push(subgroup);
                        }
                    }
                    var record={
                        model: model
                    };
                    if (!that.context.hide_details) {
                        if (subgroup_field) {
                            subgroup.records.push(record);
                        } else {
                            group.records.push(record);
                        }
                    }
                    _.each(cols,function(col) {
                        if (col.group_operator=="sum") {
                            var v=group.model.get(col.name);
                            v+=model.get(col.name);
                            group.model.set(col.name,v);
                            if (subgroup_field) {
                                var v=subgroup.model.get(col.name);
                                v+=model.get(col.name);
                                subgroup.model.set(col.name,v);
                            }
                        }
                    });
                });
                log("groups",groups);
                this.data.groups=groups;
            } else {
                var records=[];
                collection.each(function(model) {
                    var record={};
                    record.model=model;
                    records.push(record);
                });
                this.data.records=records;
            }
        } else if (view_type=="crosstab") {
            var agg_fields=[];
            _.each(cols,function(col) {
                if (col.group_operator) {
                    agg_fields.push({
                        name: col.name,
                        group_operator: col.group_operator
                    });
                }
            });
            log("agg_fields",agg_fields);
            var totals=new NFModel({},{name:collection.name});
            _.each(agg_fields,function(f) {
                totals.set(f.name,0);
            });
            this.data.agg_fields=agg_fields;
            var all_subgroup_vals={};
            var all_subgroups=[];
            collection.each(function(model) {
                var subgroup_val=model.get(subgroup_field);
                var subgroup=all_subgroup_vals[subgroup_val];
                if (!subgroup) {
                    var vals={};
                    vals[subgroup_field]=subgroup_val;
                    var subgroup_model=new NFModel(vals,{name:model.name});
                    _.each(agg_fields,function(f) {
                        subgroup_model.set(f.name,0);
                    });
                    subgroup={
                        model: subgroup_model,
                        subgroup_val: subgroup_val
                    }
                    all_subgroups.push(subgroup);
                    all_subgroup_vals[subgroup_val]=subgroup;
                }
            });
            log("all_subgroups",all_subgroups);
            this.data.all_subgroups=all_subgroups;
            var group_vals={};
            var groups=[];
            collection.each(function(model) {
                var group_val=model.get(group_field);
                var subgroup_val=model.get(subgroup_field);
                var group=group_vals[group_val];
                if (!group) {
                    var vals={};
                    vals[group_field]=group_val;
                    var group_model=new NFModel(vals,{name:model.name});
                    _.each(agg_fields,function(f) {
                        group_model.set(f.name,0);
                    });
                    group={
                        model: group_model,
                        subgroups: [],
                        records: []
                    }
                    subgroup_vals={};
                    _.each(all_subgroups,function(s) {
                        var vals={};
                        var subgroup_val=s.model.get(subgroup_field);
                        vals[subgroup_field]=subgroup_val;
                        var subgroup_model=new NFModel(vals,{name:model.name});
                        _.each(agg_fields,function(f) {
                            subgroup_model.set(f.name,0);
                        });
                        subgroup={
                            model: subgroup_model
                        }
                        group.subgroups.push(subgroup);
                        subgroup_vals[subgroup_val]=subgroup;
                    });
                    group_vals[group_val]=group;
                    groups.push(group);
                }
                var record={
                    model: model,
                    subgroup_val: subgroup_val
                };
                if (!that.context.hide_details) {
                    group.records.push(record);
                }
                _.each(agg_fields,function(f) {
                    var agg_model=group_vals[group_val].model;
                    agg_model.set(f.name,agg_model.get(f.name)+model.get(f.name));
                    var agg_model=subgroup_vals[subgroup_val].model;
                    agg_model.set(f.name,agg_model.get(f.name)+model.get(f.name));
                    var agg_model=all_subgroup_vals[subgroup_val].model;
                    agg_model.set(f.name,agg_model.get(f.name)+model.get(f.name));
                    totals.set(f.name,totals.get(f.name)+model.get(f.name));
                });
            });
            log("groups",groups);
            this.data.groups=groups;
            this.data.all_subgroups=all_subgroups;
            this.data.totals=totals;
            log("totals",totals);
        }
        NFView.prototype.render.call(this);
    },

    drill_down: function(e) {
        log("drill_down",this);
        var group_ids=[];
        this.$el.find("input:checked").each(function () {
            var group_id=$(this).data("groupId");
            group_ids.push(group_id);
        });
        log("group_ids",group_ids);
        var collection=this.context.collection;
        var model_cls=get_model(collection.name);
        var group_field=this.data.group_field;
        var group_vals=[];
        _.each(this.data.groups,function(g) {
            if (_.contains(group_ids,g.model.cid)) {
                var v=g.model.get(group_field);
                var f=model_cls.fields[group_field];
                if (f.type=="many2one") {
                    v=v[0];
                }
                group_vals.push(v);
            }
        });
        console.log("group_vals",group_vals);
        var model=this.context._action_view.context.model; // XXX
        console.log("model",model);
        model.save({},{
            success: function() {
                var ctx={
                    group_field: group_field,
                    group_vals: group_vals
                }
                rpc_execute(model.name,"drill_down",[],{context:ctx},function(err,data) {
                    if (err) {
                        set_flash("error",err.message);
                        return;
                    }
                    var next=data.next;
                    if (_.isString(next)) {
                        var action={name:next};
                    } else {
                        var action=next;
                    }
                    exec_action(action);
                });
            },
            error: function(model,err) {
                set_flash("error",err.message);
            }
        });
    }
});

ReportList.register();
