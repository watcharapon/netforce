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

var FieldDateRange=NFView.extend({
    _name: "field_date_range",
    className: "form-group nf-field",
    events: {
        "change input": "onchange",
        "changeDate input": "onchange",
        "blur input": "blur"
    },

    initialize: function(options) {
        NFView.prototype.initialize.call(this,options);
        var name=this.options.name;
        var model=this.context.model;
        model.on("change:"+name,this.render,this);
        model.on("error",this.render,this);
    },

    render: function() {
        log("field_date_range render",this);
        var name=this.options.name;
        var model=this.context.model;
        var val=model.get(name);
        if (val) val=_.clone(val);
        if (val && val[0]) val[0]=format_date(val[0]);
        if (val && val[1]) val[1]=format_date(val[1]);
        this.data.value=val;
        var field=model.get_field(name);
        this.data.string=field.string;
        this.data.readonly=field.readonly||this.options.readonly||this.context.readonly;
        var form_layout=this.options.form_layout||"stacked";
        this.data.horizontal=this.options.form_layout=="horizontal";
        NFView.prototype.render.call(this);
        if (ui_params_db.date_format) {
            var format2=ui_params_db.date_format;
        } else {
            var format2="YYYY-MM-DD";
        }
        var opts={
            format:format2,
            pickTime: false,
            use_buddhist_date:ui_params_db.use_buddhist_date
        };
        this.$el.find("input.date-from").datetimepicker(opts);
        this.$el.find("input.date-to").datetimepicker(opts);
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
        if (this.options.invisible) {
            this.$el.hide();
        }
        if (this.options.span && !this.options.span_input_only) { // XXX
            this.$el.addClass("col-sm-"+this.options.span);
        }
        this.$el.find("input").width(70);
        if (this.options.width) {
            this.$el.find("input").width(this.options.width-8);
            this.$el.width(this.options.width);
        }
        if (this.options.nomargin) {
            this.$el.find("input").css({margin:"0"});
            this.$el.css({margin:"0"});
        }
        return this;
    },

    onchange: function() {
        //log("change date");
        var val_from=$(this.$el.find("input")[0]).val();
        if (!val_from) {
            val_from=null;
        }
        val_from=parse_date(val_from);
        var val_to=$(this.$el.find("input")[1]).val();
        if (!val_to) {
            val_to=null;
        }
        val_to=parse_date(val_to);
        log("field_date_range.change",[val_from,val_to])
        var name=this.options.name;
        var model=this.context.model;
        model.set(name,[val_from,val_to],{silent:true});
    },

    blur: function() {
        log("field_date_range.blur",this);
        this.$el.find("input.date-from").datetimepicker("hide");
        this.$el.find("input.date-to").datetimepicker("hide");
    }
});

FieldDateRange.register();
