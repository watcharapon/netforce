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

var PopupView=NFView.extend({
    _name: "popup_view",

    initialize: function(options) {
        log("popup_view.initialize",this);
        var that=this;
        NFView.prototype.initialize.call(this,options);
        if (this.options.form_layout) {
            var layout=this.options.form_layout;
        } else {
            if (this.options.view_xml) {
                var form_view=get_xml_layout({name:this.options.view_xml});
            } else {
                var form_view=get_xml_layout({model:this.options.model,type:"form"});
            }
            var layout=form_view.layout;
        }
        if (_.isString(layout)) {
            var doc=$.parseXML(layout);
            this.$form=$(doc).children();
        } else {
            this.$form=layout;
        }
        this.active_id=parseInt(this.options.active_id);
        if (!this.active_id) throw "Missing active_id"; 
    },

    render: function() {
        log("popup_view.render",this);
        var that=this;
        var model_name=this.options.model;
        var field_names=[];
        var model_cls=get_model_cls(model_name);
        this.$form.find("field").each(function() {
            var name=$(this).attr("name");
            field_names.push(name);
        });
        this.field_names=field_names;
        var title_field=this.$form.attr("title_field");
        if (title_field) {
            this.field_names.push(title_field);
        }
        var breads=[];
        this.$form.find("bread").children().each(function() {
            breads.push({
                string: $(this).attr("string"),
                action: $(this).attr("action")
            });
        });
        this.data.breads=breads;
        rpc_execute(model_name,"read",[[this.active_id]],{field_names:field_names},function(err,data) {
            that.model=new NFModel(data[0],{name:model_name});
            that.data.context.data=data[0];
            that.data.context.model=that.model;
            if (title_field) {
                that.data.title=that.model.get(title_field);
            } else {
                that.data.title=that.$form.attr("title")||that.options.string;
            }
            that.data.render_form_body=function(ctx) { return that.render_form_body.call(that,ctx); };
            NFView.prototype.render.call(that);
        });
        return this;
    },

    render_form_body: function(context,$form) {
        log("popup_view.render_form_body",this,context,$form);
        var that=this;
        if (!$form) {
            var layout=this.form_layout;
            var doc=$.parseXML(layout);
            $form=$(doc).children();
        }
        var body=$("<div/>");
        var row=$('<div class="row"/>');
        body.append(row);
        var line_cols=0;
        $form.children().each(function() {
            var $el=$(this);
            var tag=$el.prop("tagName");
            if (tag=="field") {
                var name=$el.attr("name");
                var field=get_field(that.options.model,name);
                if (field.type=="one2many") {
                    default_span=12;
                } else {
                    default_span=5;
                }
                var span=$el.attr("span");
                if (span) span=parseInt(span);
                else span=default_span;
                if (line_cols+span>11) {
                    line_cols=0;
                    row=$('<div class="row"/>');
                    body.append(row);
                }
                var cell=$('<div/>');
                if (span!=12) { // XXX
                    cell.addClass("col-sm-"+span);
                } else {
                    cell.css({marginLeft:"30px"});
                }
                if (!$el.attr("nolabel")) { // XXX
                    cell.addClass("form-horizontal");
                }
                if ($el.attr("offset")) {
                    cell.addClass("offset"+$el.attr("offset"));
                }
                row.append(cell);
                var opts={
                    name: name,
                    readonly: $el.attr("readonly"),
                    required: $el.attr("required"),
                    nolabel: $el.attr("nolabel"),
                    invisible: $el.attr("invisible"),
                    onchange: $el.attr("onchange"),
                    count: $el.attr("count")||1,
                    password: $el.attr("password"),
                    size: $el.attr("size"),
                    selection: $el.attr("selection"),
                    attrs: $el.attr("attrs"),
                    width: $el.attr("width"),
                    height: $el.attr("height"),
                    condition: $el.attr("condition"),
                    perm: $el.attr("perm"),
                    link: $el.attr("link"),
                    view: $el.attr("view"),
                    context: context
                };
                if ($el.find("list").length>0) {
                    opts.inner=function(params) { 
                        var $list=$el.find("list");
                        var sub_fields=[];
                        $list.children().each(function() {
                            var $el2=$(this);
                            sub_fields.push({
                                name: $el2.attr("name"),
                                condition: $el2.attr("condition"),
                                onchange: $el2.attr("onchange")
                            });
                        });
                        var opts2={
                            fields: sub_fields,
                            context: params.context
                        }
                        var view=Sheet.make_view(opts2);
                        html="<div id=\""+view.cid+"\" class=\"view\"></div>";
                        return html;
                    };
                    opts.field_names=[];
                    $el.find("list").find("field").each(function() {
                        var $el2=$(this);
                        opts.field_names.push($el2.attr("name"));
                    });
                }
                var view=Field.make_view(opts);
                cell.append("<div id=\""+view.cid+"\" class=\"view\"></div>");
                line_cols+=span;
            } else if (tag=="separator") {
                var span=$el.attr("span")
                if (span) cols=parseInt(span);
                else span=12;
                var cell=$('<div/>');
                if (span!=12) { // XXX
                    cell.addClass("col-sm-"+span);
                } else {
                    cell.css({marginLeft:"30px"});
                }
                row.append(cell);
                var opts={
                    string: $el.attr("string")
                };
                var view=Separator.make_view(opts);
                cell.append("<div id=\""+view.cid+"\" class=\"view\"></div>");
                line_cols+=span;
            } else if (tag=="newline") {
                line_cols+=12;
            } else if (tag=="tabs") {
                var span=$el.attr("span")
                if (span) cols=parseInt(span);
                else span=12;
                var cell=$('<div/>');
                if (span!=12) { // XXX
                    cell.addClass("col-sm-"+span);
                } else {
                    cell.css({marginLeft:"30px"});
                }
                row.append(cell);
                var opts={
                    tabs_layout: $el,
                    context: context
                };
                var view=TabsView.make_view(opts);
                cell.append("<div id=\""+view.cid+"\" class=\"view\"></div>");
                line_cols+=span;
            }
        });
        return body.html();
    },

    render_form_foot_popup: function(context) {
        log("popup_view.render_form_foot_popup",this,context);
        var layout=this.form_layout;
        var doc=$.parseXML(layout);
        var that=this;
        var foot=$("<div/>");
        $(doc).find("foot").children().each(function() {
            var $el=$(this);
            var tag=$el.prop("tagName");
            if (tag=="button") {
                var opts={
                    string: $el.attr("string"),
                    method: $el.attr("method"),
                    size: $el.attr("size"),
                    type: $el.attr("type"),
                    next: $el.attr("next"),
                    icon: $el.attr("icon"),
                    states: $el.attr("states"),
                    context: context
                };
                var view=Button.make_view(opts);
                foot.append("<div id=\""+view.cid+"\" class=\"view\"></div>");
            }
        });
        if (!$(doc).find("foot").attr("replace")) {
            var opts={
                string: "Cancel",
                action: "_close",
                context: context
            };
            var view=Button.make_view(opts);
            foot.append("<div id=\""+view.cid+"\" class=\"view\"></div>");
        }
        return foot.html();
    }
});

PopupView.register();
