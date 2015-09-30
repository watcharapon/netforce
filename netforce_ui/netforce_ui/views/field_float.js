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

var FieldFloat=NFView.extend({
    _name: "field_float",
    className: "form-group nf-field",
    events: {
        "change input": "onchange",
        "blur input": "blur",
        "keydown input": "keydown",
        "focus input": "on_focus"
    },

    initialize: function(options) {
        NFView.prototype.initialize.call(this,options);
        var name=this.options.name;
        var model=this.context.model;
        model.on("change:"+name,this.render,this);
        model.on("error",this.render,this);
        this.listen_attrs();
        if (this.options.inner) {
            this.template=this.options.inner;
        }
    },

    render: function() {
        log("field_float.render",this);
        var name=this.options.name;
        this.$el.addClass("field-"+name);
        var model=this.context.model;
        this.data.value=model.get(name);
        var field=model.get_field(name);
        this.data.string=this.options.string||field.string;
        this.data.readonly=field.readonly||this.options.readonly||this.context.readonly;
        var attrs=this.eval_attrs();
        if (attrs.readonly!==undefined) {
            this.data.readonly=attrs.readonly;
        }
        var perms=get_field_permissions(model.name,name);
        if (!perms.perm_write) {
            this.data.readonly=true;
        }
        var has_focus=this.$el.find("input").is(":focus");
        this.disable_blur=true; // avoir blur in sheet when rerender due to onchange
        var form_layout=this.options.form_layout||"stacked";
        this.data.horizontal=form_layout=="horizontal";
        var pkg=this.options.pkg||field.pkg;
        if (!check_package(pkg)) {
            this.data.disabled=true;
        }
        NFView.prototype.render.call(this);
        this.disable_blur=false;
        if (has_focus) this.focus();
        if (this.options.invisible || attrs.invisible || !perms.perm_read) {
            this.$el.hide();
        } else {
            this.$el.show();
        }
        if (field.required && !this.data.readonly) {
            this.$el.addClass("nf-required-field");
        }
        if (field.required) {
            model.set_required(name);
        }
        var err=model.get_field_error(name);
        if (err) {
            this.$el.addClass("error");
        } else {
            this.$el.removeClass("error");
        }
        if (this.options.span && !this.options.span_input_only) { // XXX
            this.$el.addClass("col-sm-"+this.options.span);
        }
        if (this.options.offset) {
            this.$el.addClass("offset"+this.options.offset);
        }
        if (this.options.width) {
            this.$el.find("input").css("width",this.options.width+"px");
            this.$el.css("width",this.options.width+"px");
        }
        if (this.options.nomargin) {
            this.$el.find("input").css({margin:"0"});
            this.$el.css({margin:"0"});
        }
        this.$el.find("a.help").tooltip();
    },

    onchange: function() {
        var val=this.$el.find("input").val();
        if (val) {
            val=parseFloat(val.replace(/,/g,""));
        } else {
            val=null;
        }
        var name=this.options.name;
        var model=this.context.model;
        model.set(name,val,{silent:true});
        var form=this.context.form;
        if (this.options.onchange) {
            var path=model.get_path(name);
            form.do_onchange(this.options.onchange,path);
        }
    },

    eval_attrs: function() {
        var str=this.options.attrs;
        log("field_float.eval_attrs",this,str);
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
        log("==>",attrs);
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
    },

    focus: function() {
        log("field_float.focus",this);
        this.$el.find("input").focus();
    },

    on_focus: function(e) {
        log("field_float.on_focus",this);
        register_focus(e.target);
    },

    blur: function() {
        if (this.disable_blur) return;
        this.trigger("blur");
    },

    keydown: function (e) {
        if (e.keyCode==13 && this.options.submit_form) return;
        if (e.keyCode==13 && this.options.method) {
            e.preventDefault();
            this.onchange();
            var model=this.context.model;
            var name=this.options.name;
            var val=model.get(name);
            if (val) {
                this.call_method();
            }
            return;
        }
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
    },

    call_method: function() {
        console.log("call_method");
        var model=this.context.model;
        var method=this.options.method;
        if (!model.check_required()) {
            set_flash("error","Some required fields are missing");
            render_flash();
            return;
        }
        model.save({},{
            context: {}, // XXX
            success: function() {
                rpc_execute(model.name,method,[[model.id]],{},function(err,data) {
                    if (err) {
                        set_flash("error",err.message);
                        model.trigger("reload");
                        return;
                    }
                    if (data && data.flash) {
                        set_flash(data.flash);
                    }
                    var opts={};
                    if (data && data.focus_field) {
                        opts.focus_field=data.focus_field;
                    }
                    model.trigger("reload",opts);
                });
            },
            error: function(model,err) {
                set_flash("error",err.message);
                render_flash();
            }
        });
    }
});

FieldFloat.register();
