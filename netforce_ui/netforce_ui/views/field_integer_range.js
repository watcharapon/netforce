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

var FieldIntegerRange=NFView.extend({
    _name: "field_integer_range",
    className: "form-group nf-field",
    events: {
        "change input": "onchange",
        "blur input": "blur"
    },

    initialize: function(options) {
        log("field_integer_range init",this);
        NFView.prototype.initialize.call(this,options);
        var name=this.options.name;
        var model=this.context.model;
        model.on("change:"+name,this.render,this);
        model.on("error",this.render,this);
        if (this.options.inner) {
            this.template=this.options.inner;
        }
    },

    render: function() {
        log("field_integer_range render",this.options.name);
        var that=this;
        if (this.options.perm) {
            this.$el.hide();
            if (check_other_permission(this.options.perm)) {
                this.$el.show();
            }
        }
        var name=this.options.name;
        var model=this.context.model;
        this.data.value=model.get(name);
        var field=model.get_field(name);
        this.data.string=field.string;
        this.data.readonly=field.readonly||this.options.readonly||this.context.readonly;
        NFView.prototype.render.call(this);
        if (this.options.invisible) {
            this.$el.hide();
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
        this.$el.find("input").width(70);
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
    },

    onchange: function() {
        var val=$(this.$el.find("input")[0]).val();
        if (val) {
            val_from=parseFloat(val);
        } else {
            val_from=null;
        }
        var val=$(this.$el.find("input")[1]).val();
        if (val) {
            val_to=parseFloat(val);
        } else {
            val_to=null;
        }
        log("change",[val_from,val_to])
        var name=this.options.name;
        var model=this.context.model;
        model.set(name,[val_from,val_to],{silent:true});
    },

    focus: function() {
        this.$el.find("input").focus();
    },

    blur: function() {
        this.trigger("blur");
    }
});

FieldIntegerRange.register();
