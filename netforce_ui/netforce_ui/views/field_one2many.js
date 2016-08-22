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

var FieldOne2Many=NFView.extend({
    _name: "field_one2many",

    initialize: function(options) {
        NFView.prototype.initialize.call(this,options);
        this.listen_attrs();
    },

    render: function() {
        //log("field_one2many.render",this);
        if (this.options.invisible) return;
        var model=this.context.model;
        var name=this.options.name;
        var field=model.get_field(name);
        this.data.string=field.string;
        var relation=field.relation;
        var ctx=_.clone(this.context);
        ctx.parent_id=model.id;
        var attrs=this.eval_attrs();
        if (attrs.readonly) ctx.readonly=true;
        if (attrs.noadd) ctx.noadd=true;
        if (attrs.invisible) {
            this.$el.hide();
        } else {
            this.$el.show();
        }
        var view_opts={
            "model": relation,
            "template": this.options.inner||this.options.template,
            "field_names": this.options.field_names,
            "context": ctx,
            "limit": 10000 // XXX
        };
        var val=model.get(name);
        log("o2m val",name,val);
        if (_.isArray(val) && val.length>0) {
            if (_.isNumber(val[0])) {
                view_opts.condition=[["id","in",val]];
            } else {
                view_opts.data=val;
            }
        } else if (val instanceof NFCollection) {
            view_opts.data=val.toJSON();
        } else {
            var vals=[];
            if (this.options.count) {
                for (var i=0; i<parseInt(this.options.count); i++) {
                    vals.push({});
                }
            }
            view_opts.data=vals;
        }
        var view_cls=get_view_cls("collection_view");
        var view=view_cls.make_view(view_opts);
        model.set(name,view.collection);
        view.collection.parent_model=model;
        view.collection.parent_field=name;
        var tag=view.tagName;
        this.data.content='<'+tag+' id="'+view.cid+'" class="view"></'+tag+'>';
        //log("xxx",this.data.content);
        return NFView.prototype.render.call(this);
    },

    eval_attrs: function() {
        var str=this.options.attrs;
        //log("eval_attrs",this,str);
        if (!str) return {};
        var expr=JSON.parse(str);
        var model=this.context.model;
        var attrs={};
        for (var attr in expr) {
            var conds=expr[attr];
            var attr_val=true;
            for (var i in conds) {
                var clause=conds[i];
                var n=clause[0];
                var op=clause[1];
                var cons=clause[2];
                var v=model.get(n);
                var clause_v;
                if (op=="=") {
                    clause_v=v==cons;
                } else if (op=="!=") {
                    clause_v=v!=cons;
                } else if (op=="in") {
                    clause_v=_.contains(cons,v);
                } else {
                    throw "Invalid operator: "+op;
                }
                if (!clause_v) {
                    attr_val=false;
                    break;
                }
            }
            attrs[attr]=attr_val;
        }
        //log("==>",attrs);
        return attrs;
    },

    listen_attrs: function() {
        var str=this.options.attrs;
        //log("listen_attrs",this,str);
        if (!str) return;
        var expr=JSON.parse(str);
        var attrs={};
        var depends=[];
        for (var attr in expr) {
            var conds=expr[attr];
            for (var i in conds) {
                var clause=conds[i];
                var n=clause[0];
                depends.push(n);
            }
        }
        //log("==> depends",depends);
        var model=this.context.model;
        for (var i in depends) {
            var n=depends[i];
            //log("...listen "+n);
            model.on("change:"+n,this.render,this);
        }
    }
});

FieldOne2Many.register();
