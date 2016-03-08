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

var Form=NFView.extend({
    _name: "form",
    className: "view-form",
    events: {
        "submit form": "submit"
    },

    initialize: function(options) {
        NFView.prototype.initialize.call(this,options);
        this.field_attrs={};
    },

    render: function() {
        var ctx=_.clone(this.data.context);
        var model=this.context.model;
        this.$el.data({active_id: model.id}); // XXX
        ctx.form=this;
        if (this.options.readonly) {
            ctx.readonly=true;
        }
        var data={
            context: ctx
        };
        this.data.content=this.options.inner(data);
        NFView.prototype.render.call(this);
        if (this.options.border) {
            this.$el.find("form").css({"border": "1px solid #ccc", "box-shadow": "0px 5px 10px -5px #666"});
        }
    },

    do_onchange: function(method,path) {
        log("form do_onchange",method,path);
        if (method=="_refresh") {
            this.data.context.data=this.data.context.model.toJSON(); // XXX
            this.render(); // XXX
        } else {
            var model=this.context.model;
            var vals=model.get_vals();
            if (model.id) vals.id=model.id;
            var ctx={
                "data": vals,
                "path": path
            }
            var that=this;
            rpc_execute(model.name,"call_onchange",[method],{context: ctx},function(err,res) {
                var data, field_attrs, alert_msg;
                if (res.data || res.field_attrs || res.alert) {
                    data=res.data;
                    field_attrs=res.field_attrs;
                    alert_msg=res.alert;
                } else {
                    data=res;
                }
                if (_.has(data,"id")) {
                    delete data.id;
                }
                if (field_attrs) {
                    that.set_field_attrs(field_attrs);
                }
                if (data) {
                    model.set_vals(data);
                }
                if (alert_msg) {
                    alert(alert_msg);
                }
            });
        }
    },

    do_onfocus: function(method,path) {
        log("form do_onfocus",method,path);
        var model=this.context.model;
        var vals=model.get_vals();
        var ctx={
            "data": vals,
            "path": path
        }
        var that=this;
        rpc_execute(model.name,method,[],{context: ctx},function(err,data) {
            model.set_vals(data);
        });
    },

    set_field_attrs: function(field_attrs) {
        log("form set_field_attrs",field_attrs);
        for (p in field_attrs) {
            var attrs=field_attrs[p];
            if (!this.field_attrs[p]) {
                this.field_attrs[p]={};
            }
            if (!attrs) {
                delete this.field_attrs[p];
            } else {
                _.extend(this.field_attrs[p],attrs);
            }
        }
        log("new field_attrs",this.field_attrs);
    },

    get_field_attrs: function(path) {
        log("form get_field_attrs",path);
        var attrs=this.field_attrs[path];
        log("attrs",attrs);
        return attrs;
    },

    submit: function() { // XXX: not used?
        log("form submit",this);
    }
});

Form.register();
