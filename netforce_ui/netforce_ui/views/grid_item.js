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

var GridItem=NFView.extend({
    _name: "grid_item",
    events: {
        "click .title-link": "click_title",
        "click .nf-select-item": "select_item"
    },

    initialize: function(options) {
        //log("grid_item.initialize",this);
        var that=this;
        NFView.prototype.initialize.call(this,options);
        if (this.options.grid_layout) {
            var layout=this.options.grid_layout;
        } else {
            if (this.options.view_xml) {
                var grid_view=get_xml_layout({name:this.options.view_xml});
            } else {
                var grid_view=get_xml_layout({model:this.options.model,type:"grid"});
            }
            var layout=grid_view.layout;
        }
        if (_.isString(layout)) {
            var doc=$.parseXML(layout);
            this.$grid=$(doc).children();
        } else {
            this.$grid=layout;
        }
        this.data.render_head=function(ctx) { return that.render_head.call(that,ctx); };
        this.data.render_body=function(ctx) { return that.render_body.call(that,ctx); };
    },

    render: function() {
        //log("grid_item.render",this);
        this.data.context.model=this.options.data;
        this.data.context.data=this.options.data.attributes; // XXX
        if (this.$grid.find("head").length>0) {
            this.data.show_head=true;
        }
        var $el=this.$grid.find("head field");
        if ($el.length>0) {
            var name=$el.attr("name");
            this.data.head_title=field_value(name,this.data.context);
        }
        this.data.next_action=this.options.next_action;
        var next_action_options=this.options.next_action_options;
        if (next_action_options) next_action_options+="&";
        next_action_options+="active_id="+this.data.context.model.id;
        this.data.next_action_options=next_action_options;
        NFView.prototype.render.call(this);
        return this;
    },

    render_head: function(context) {
        //log("GridItem.render_head",this,context);
        var that=this;
        var content=$("<div/>");
        this.$grid.children("head").children().each(function() {
            var $el=$(this);
            var tag=$el.prop("tagName");
            if (tag=="button") {
                var opts={
                    string: $el.attr("string"),
                    method: $el.attr("method"),
                    action: $el.attr("action"),
                    action_context: $el.attr("action_context"),
                    size: $el.attr("size"),
                    type: $el.attr("type"),
                    next: $el.attr("next"),
                    icon: $el.attr("icon"),
                    dropdown: $el.attr("dropdown"),
                    align: "right",
                    perm: $el.attr("perm"),
                    context: context
                };
                if (that.active_id) {
                    opts.action_options="refer_id="+that.active_id; // XXX: orig_id
                }
                if (opts.dropdown) { // XXX
                    var inner="";
                    $el.children().each(function() {
                        var $el2=$(this);
                        var tag=$el2.prop("tagName");
                        if (tag=="item") {
                            var opts2={
                                string: $el2.attr("string"),
                                method: $el2.attr("method"),
                                action: $el2.attr("action"),
                                action_options: $el2.attr("action_options"),
                                action_context: $el2.attr("action_context"),
                                states: $el2.attr("states"),
                                confirm: $el2.attr("confirm"),
                                perm: $el2.attr("perm"),
                                context: context
                            }
                            if (that.active_id) {
                                opts2.action_options="refer_id="+that.active_id; // XXX: orig_id
                            }
                            var view=Item.make_view(opts2);
                            inner+="<li id=\""+view.cid+"\" class=\"view\"></li>";
                        } else if (tag=="divider") {
                            inner+="<li class=\"divider\"></li>";
                        }
                    });
                    opts.inner=function() {return inner; };
                    var view=ButtonGroup.make_view(opts);
                } else {
                    var view=Button.make_view(opts);
                }
                content.append("<div id=\""+view.cid+"\" class=\"view\"></div>");
            }
        });
        return content.html();
    },

    render_body: function(context) {
        //log("GridItem.render_body",this,context);
        var that=this;
        var body=$("<div/>");
        var row=$('<div class="row"/>');
        body.append(row);
        var col=0;
        var readonly=this.readonly;
        var form_layout=this.options.form_layout||"horizontal";
        this.$grid.children().each(function() {
            var $el=$(this);
            var tag=$el.prop("tagName");
            if (tag=="field") {
                var name=$el.attr("name");
                var model=that.data.context.model;
                var field=model.get_field(name);
                if (field.type=="one2many" || field.type=="many2many") {
                    default_span=12;
                } else {
                    default_span=6;
                }
                var span=$el.attr("span");
                if (span) span=parseInt(span);
                else span=default_span;
                if (col+span>12) {
                    col=0;
                    row=$('<div class="row"/>');
                    body.append(row);
                }
                var cell=$('<div/>');
                cell.addClass("col-sm-"+span);
                if ($el.attr("offset")) {
                    cell.addClass("col-sm-offset-"+$el.attr("offset"));
                }
                if (form_layout=="horizontal") {
                    cell.addClass("form-horizontal");
                }
                row.append(cell);
                if ($el.attr("readonly")=="0") { // XXX
                    var readonly=false;
                } else {
                    var readonly=true;
                }
                var opts={
                    name: name,
                    readonly: readonly,
                    required: $el.attr("required"),
                    nolabel: $el.attr("nolabel"),
                    invisible: $el.attr("invisible"),
                    onchange: $el.attr("onchange"),
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
                    help: $el.attr("help"),
                    wysi: $el.attr("wysi"),
                    target: $el.attr("target"),
                    mode: $el.attr("mode"),
                    select_view_xml: $el.attr("select_view_xml"),
                    form_layout: form_layout,
                    context: context
                };
                if ($el.find("list").length>0) {
                    if (field.type=="one2many") {
                        opts.inner=function(params) { 
                            var view_cls_name=$el.attr("view_cls")||"sheet";
                            var $list=$el.find("list");
                            if (view_cls_name=="sheet") { // XXX
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
                                    default_count: 1,
                                    readonly: $el.attr("readonly")||that.readonly,
                                    context: params.context
                                }
                            } else if (view_cls_name=="form_list_view") { // XXX
                                var opts2={
                                    model: field.relation,
                                    list_layout: $list,
                                    context: params.context,
                                    readonly: true
                                }
                            }
                            var view_cls=get_view_cls(view_cls_name);
                            var view=view_cls.make_view(opts2);
                            html="<div id=\""+view.cid+"\" class=\"view\"></div>";
                            return html;
                        };
                    } else if (field.type=="many2many") {
                        opts.inner=function(params) { 
                            var $list=$el.find("list");
                            var sub_fields=[];
                            $list.children().each(function() {
                                var $el2=$(this);
                                sub_fields.push({
                                    col_type: "field",
                                    name: $el2.attr("name")
                                });
                            });
                            var opts2={
                                cols: sub_fields,
                                context: params.context
                            }
                            var view=List.make_view(opts2);
                            html="<div id=\""+view.cid+"\" class=\"view\"></div>";
                            return html;
                        };
                    }
                    opts.field_names=[];
                    $el.find("list").find("field").each(function() {
                        var $el2=$(this);
                        opts.field_names.push($el2.attr("name"));
                    });
                }
                var view=Field.make_view(opts);
                cell.append("<div id=\""+view.cid+"\" class=\"view\"></div>");
                col+=span;
            } else if (tag=="separator") {
                var span=$el.attr("span")
                if (span) span=parseInt(span);
                else span=12;
                var cell=$('<div/>');
                if (span!=12) { // XXX
                    cell.addClass("col-sm-"+span);
                } else {
                    cell.css({marginLeft:"28px"});
                }
                if ($el.attr("offset")) {
                    cell.addClass("col-sm-offset-"+$el.attr("offset"));
                }
                row.append(cell);
                var opts={
                    string: $el.attr("string")
                };
                var view=Separator.make_view(opts);
                cell.append("<div id=\""+view.cid+"\" class=\"view\"></div>");
                col+=span;
            } else if (tag=="newline") {
                col+=12;
            } else if (tag=="tabs") {
                var span=$el.attr("span")
                if (span) span=parseInt(span);
                else span=12;
                if (col+span>12) {
                    col=0;
                    row=$('<div class="row"/>');
                    body.append(row);
                }
                var cell=$('<div/>');
                if (span!=12) { // XXX
                    cell.addClass("col-sm-"+span);
                } else {
                    cell.css({marginLeft:"28px"});
                }
                row.append(cell);
                var opts={
                    tabs_layout: $el,
                    context: context
                };
                var view=TabsView.make_view(opts);
                cell.append("<div id=\""+view.cid+"\" class=\"view\"></div>");
                col+=span;
            } else if (tag=="group") {
                var span=$el.attr("span")
                if (span) span=parseInt(span);
                else span=12;
                var offset=$el.attr("offset")
                if (offset) offset=parseInt(offset);
                else offset=0;
                col+=offset;
                if (col+span>12) {
                    col=0;
                    row=$('<div class="row"/>');
                    body.append(row);
                }
                var cell=$('<div/>');
                cell.addClass("col-sm-"+span);
                if (offset) {
                    cell.addClass("col-sm-offset-"+offset);
                }
                row.append(cell);
                var opts={
                    group_layout: $el,
                    attrs: $el.attr("attrs"),
                    span: $el.attr("span"),
                    readonly: true,
                    form_layout: $el.attr("form_layout"),
                    columns: $el.attr("columns"),
                    context: context
                };
                if (col>0 && !opts.span) {
                    opts.span=12-col;
                }
                var view_cls=get_view_cls("group");
                var view=view_cls.make_view(opts);
                cell.append("<div id=\""+view.cid+"\" class=\"view\"></div>");
                col+=span;
            } else if (tag=="label") {
                var span=$el.attr("span")
                if (span) span=parseInt(span);
                else span=12;
                var cell=$('<div/>');
                cell.addClass("col-sm-"+span);
                row.append(cell);
                cell.text($el.attr("string"));
                col+=span;
            } else if (tag=="button") {
                var span=$el.attr("span")
                if (span) span=parseInt(span);
                else span=2;
                if (col+span>12) {
                    col=0;
                    row=$('<div class="row"/>');
                    body.append(row);
                }
                var cell=$('<div/>');
                cell.addClass("col-sm-"+span);
                row.append(cell);
                col+=span;
                var opts={
                    string: $el.attr("string"),
                    method: $el.attr("method"),
                    action: $el.attr("action"),
                    action_context: $el.attr("action_context"),
                    size: $el.attr("size"),
                    type: $el.attr("type"),
                    next: $el.attr("next"),
                    icon: $el.attr("icon"),
                    states: $el.attr("states"),
                    perm: $el.attr("perm"),
                    attrs: $el.attr("attrs"),
                    context: context
                };
                if (that.active_id) {
                    opts.action_options="refer_id="+that.active_id;
                }
                var view=Button.make_view(opts);
                cell.append("<div id=\""+view.cid+"\" class=\"view\"></div>");
            } else if (tag=="template") {
                var span=$el.attr("span")
                if (span) span=parseInt(span);
                else span=12;
                var offset=$el.attr("offset")
                if (offset) offset=parseInt(offset);
                else offset=0;
                col+=offset;
                if (col+span>12) {
                    col=0;
                    row=$('<div class="row"/>');
                    body.append(row);
                }
                var cell=$('<div/>');
                cell.addClass("col-sm-"+span);
                if (offset) {
                    cell.addClass("col-sm-offset-"+offset);
                }
                row.append(cell);
                var tmpl_src=(new XMLSerializer()).serializeToString($el[0]).replace("<template>","").replace("</template>","");
                var tmpl=Handlebars.compile(tmpl_src);
                var data={context:context};
                try {
                    var html=tmpl(data);
                } catch (err) {
                    throw "Failed to render template: "+err.message;
                }
                cell.append(html);
                col+=span;
            }
        });
        return body.html();
    },

    click_title: function(e) {
        log("click_title");
        e.preventDefault();
        if (this.$grid.attr("action")) {
            var action_name=this.$grid.attr("action");
            var action_options=this.$grid.attr("action_options");
        } else if (this.data.next_action) { // XXX: deprecated
            var action_name=this.data.next_action;
            var action_options=this.data.next_action_options;
        } else {
            log("no action");
            return;
        }
        var action={name:action_name};
        if (action_options) {
            if (action_options[0]=="{") {
                var data=this.data.context.model.get_vals_all();
                var opts=eval_json(action_options,data);
                _.extend(action,opts);
            } else { // XXX: deprecated
                _.extend(action,qs_to_obj(action_options));
            }
        }
        exec_action(action);
    },

    select_item: function(e) {
        log("grid_item.select_item");
        e.preventDefault();
        if (this.options.on_select_item) {
            this.options.on_select_item(this.options.data.id);
        }
    }
});

GridItem.register();
