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

var FieldInteger=NFView.extend({
    _name: "field_integer",
    className: "form-group nf-field",
    events: {
        "change input": "onchange",
        "blur input": "blur",
        "keydown input": "keydown"
    },

    initialize: function(options) {
        NFView.prototype.initialize.call(this,options);
        var name=this.options.name;
        var model=this.context.model;
        model.on("change:"+name,this.render,this);
        if (this.options.inner) {
            this.template=this.options.inner;
        }
        this.listen_attrs();
    },

    render: function() {
        log("field_integer render",this.options.name);
        var name=this.options.name;
        this.$el.addClass("field-"+name);
        var model=this.context.model;
        this.data.value=model.get(name);
        var field=model.get_field(name);
        this.data.string=this.options.string||field.string;
        this.data.readonly=field.readonly||this.options.readonly||this.context.readonly;
        this.data.placeholder=this.options.placeholder;
        var attrs=this.eval_attrs();
        if (attrs.readonly!==undefined) {
            this.data.readonly=attrs.readonly;
        }
        var form_layout=this.options.form_layout||"stacked";
        this.data.horizontal=form_layout=="horizontal";
        var perms=get_field_permissions(model.name,name);
        NFView.prototype.render.call(this);
        if (this.options.invisible || attrs.invisible || !perms.perm_read) {
            this.$el.hide();
        } else {
            this.$el.show();
        }
        if (this.options.span) {
            this.$el.addClass("col-sm-"+this.options.span);
        }
        if (this.options.offset) {
            this.$el.addClass("offset"+this.options.offset);
        }
        if (this.options.width) {
            this.$el.find("input").width(this.options.width-8);
            this.$el.width(this.options.width);
        }
        if (this.options.nomargin) {
            this.$el.find("input").css({margin:"0"});
            this.$el.css({margin:"0"});
        }
        this.$el.find("a.help").tooltip();
        var required=false;
        if (field.required!=null) required=field.required;
        if (this.options.required!=null) required=this.options.required;
        if (attrs.required!=null) required=attrs.required;
        if (required && !this.data.readonly) {
            this.$el.addClass("nf-required-field");
        }
        if (required) {
            model.set_required(name);
        } else {
            model.set_not_required(name);
        }
    },

    onchange: function() {
        var val=this.$el.find("input").val();
        if (val) {
            val=parseInt(val);
        }
        var name=this.options.name;
        var model=this.context.model;
        model.set(name,val);
        var form=this.context.form;
        if (this.options.onchange) {
            var path=model.get_path(name);
            form.do_onchange(this.options.onchange,path);
        }
    },

    focus: function() {
        this.$el.find("input").focus();
    },

    blur: function() {
        this.trigger("blur");
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

    keydown: function (e) {
        if (e.keyCode==9||e.keyCode==13) {
            e.preventDefault();
            if (e.shiftKey) {
                this.trigger("focus_prev");
                if (!this.options.disable_focus_change) {
                    focus_prev();
                }
            } else {
                this.trigger("focus_next");
                if (!this.options.disable_focus_change) {
                    focus_next();
                }
            }
        } else if (e.keyCode==40) {
            this.trigger("focus_down");
        } else if (e.keyCode==38) {
            this.trigger("focus_up");
        }
    }
});

FieldInteger.register();
