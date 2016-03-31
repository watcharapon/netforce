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

var PageView=NFView.extend({
    _name: "page_view",
    events: {
        "click ol.breadcrumb li": "click_bread",
        "click .related-tab": "click_related_tab"
    },

    initialize: function(options) {
        //log("page_view.initialize",this);
        var that=this;
        NFView.prototype.initialize.call(this,options);
        if (this.options.page_layout) {
            var layout=this.options.page_layout;
        } else {
            if (this.options.view_xml) {
                var page_view=get_xml_layout({name:this.options.view_xml});
            } else {
                var page_view=get_xml_layout({model:this.options.model,type:"page",noerr:true});
                if (!page_view) {
                    page_view=get_xml_layout({model:this.options.model,type:"form"});
                }
            }
            var layout=page_view.layout;
        }
        if (_.isString(layout)) {
            var doc=$.parseXML(layout);
            this.$layout=$(doc).children();
        } else {
            this.$layout=layout;
        }
        this.active_id=parseInt(this.options.active_id);
        if (!this.active_id) throw "Missing active_id"; 
        this.data.render_body=function(ctx) { return that.render_body.call(that,ctx); };
        this.data.render_toolbar=function(ctx) { return that.render_toolbar.call(that,ctx); };
        this.data.render_foot=function(ctx) { return that.render_foot.call(that,ctx); };
        this.data.render_related=function(ctx) { return that.render_related.call(that,ctx); };
        this.data.bread_string=this.options.string;
        this.related_tab=parseInt(this.options.related_tab);
    },

    render: function() {
        //log("page_view.render",this);
        var that=this;
        var model_name=this.options.model;
        var field_names=[];
        var model_cls=get_model(model_name);
        this.$layout.find("field").each(function() {
            if ($(this).parents("field").length>0) {
                return;
            }
            if ($(this).parents("related").length>0) {
                return;
            }
            if ($(this).parents("related_tabs").length>0) {
                return;
            }
            var name=$(this).attr("name");
            field_names.push(name);
        });
        this.field_names=field_names;
        var title_field=this.$layout.attr("title_field");
        if (title_field) {
            this.field_names.push(title_field);
        }
        var subtitle_field=this.$layout.attr("subtitle_field");
        if (subtitle_field) {
            this.field_names.push(subtitle_field);
        }
        this.render_waiting();
        var model_cls=get_model(model_name);
        rpc_execute(model_name,"read",[[this.active_id]],{field_names:field_names},function(err,data) {
            that.model=new NFModel(data[0],{name:model_name});
            that.data.context.data=data[0];
            that.data.context.model=that.model;
            if (title_field) {
                that.data.title=that.model.get(title_field);
            } else {
                if (that.$layout.attr("title")) {
                    that.data.title=that.$layout.attr("title");
                } else {
                    that.data.title="View";
                    if (model_cls.string) {
                        that.data.title+=" "+model_cls.string;
                    }
                }
            }
            if (subtitle_field) {
                that.data.subtitle=field_value(subtitle_field,that.data.context);
            }
            if (that.$layout.attr("show_company")) {
                that.data.show_company=true;
                var val=that.model.get("company_id");
                that.data.company_name=val?val[1]:null;
            }
            that.model.on("reload",that.reload,that);
            var args=[that.options.search_condition || []];
            var opts={
                offset: that.options.offset||0,
                limit: that.options.limit||100,
            };
            nf_execute(model_name,"search",args,opts,function(err,data) {
                if (err) throw "ERROR: "+err;
                that.data.count=data.length;
                that.data.record_index=data.indexOf(that.active_id);
                that.data.record_index_p1=that.data.record_index+1;
                if (that.data.record_index>0) {
                    var prev_active_id=data[that.data.record_index-1];
                    var h=window.location.hash.substr(1);
                    var action=qs_to_obj(h);
                    action.active_id=prev_active_id;
                    var h2=obj_to_qs(action);
                    that.data.prev_url="#"+h2;

                    var start_active_id=data[0];
                    var h=window.location.hash.substr(1);
                    var action=qs_to_obj(h);
                    action.active_id=start_active_id;
                    var h2=obj_to_qs(action);
                    that.data.start_url="#"+h2;
                }
                if (that.data.record_index < that.data.count-1) {
                    var next_active_id=data[that.data.record_index+1];
                    var h=window.location.hash.substr(1);
                    var action=qs_to_obj(h);
                    action.active_id=next_active_id;
                    var h2=obj_to_qs(action);
                    that.data.next_url="#"+h2;

                    var end_active_id=data[data.length-1];
                    var h=window.location.hash.substr(1);
                    var action=qs_to_obj(h);
                    action.active_id=end_active_id;
                    var h2=obj_to_qs(action);
                    that.data.end_url="#"+h2;
                }
                NFView.prototype.render.call(that);
                if (that.focus_field) {
                    var view=that.get_field_view(that.focus_field);
                    view.focus();
                }
            });
        });
        return this;
    },

    render_waiting: function() {
        var img=$("<img/>").attr("src","/static/img/spinner.gif");
        this.$el.empty();
        this.$el.append(img);
    },

    reload: function() {
        log("page_view.reload");
        this.render();
    },

    render_body: function(context) {
        //log("page_view.render_body",this,context);
        var that=this;
        var body=$("<div/>");
        var row=$('<div class="row"/>');
        body.append(row);
        var col=0;
        var form_layout=this.options.form_layout||"horizontal";
        this.$layout.children().each(function() {
            var $el=$(this);
            var tag=$el.prop("tagName");
            if (tag=="field") {
                var name=$el.attr("name");
                var field=get_field(that.options.model,name);
                if (field.type=="one2many") {
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
                    cell.addClass("offset"+$el.attr("offset"));
                }
                if (form_layout=="horizontal") {
                    cell.addClass("form-horizontal");
                }
                row.append(cell);
                var opts={
                    name: name,
                    readonly: true,
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
                    action: $el.attr("action"),
                    action_options: $el.attr("action_options"),
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
                                    readonly: true,
                                    context: params.context
                                }
                            } else if (view_cls_name=="form_list_view") { // XXX
                                var opts2={
                                    model: field.relation,
                                    list_layout: $list,
                                    context: params.context
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
                if (span) cols=parseInt(span);
                else span=12;
                var cell=$('<div/>');
                cell.addClass("col-sm-"+span);
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
                if (span) cols=parseInt(span);
                else span=12;
                if (col+span>12) {
                    col=0;
                    row=$('<div class="row"/>');
                    body.append(row);
                }
                var cell=$('<div/>');
                cell.addClass("col-sm-"+span);
                row.append(cell);
                var opts={
                    tabs_layout: $el,
                    nobackground: true, // XXX
                    context: context
                };
                var view=TabsView.make_view(opts);
                cell.append("<div id=\""+view.cid+"\" class=\"view\"></div>");
                col+=span;
            } else if (tag=="button") {
                var pull=$el.attr("pull");
                if (!pull) {
                    var span=$el.attr("span");
                    if (span) span=parseInt(span);
                    else span=1;
                    if (col+span>12) {
                        col=0;
                        row=$('<div class="row"/>');
                        body.append(row);
                    }
                }
                var cell=$('<div/>');
                if (!pull) {
                    cell.addClass("col-sm-"+span);
                    if ($el.attr("offset")) {
                        cell.addClass("offset"+$el.attr("offset"));
                    }
                }
                row.append(cell);
                var model=context.model;
                var refer_id=model.id;
                var opts={
                    string: $el.attr("string"),
                    method: $el.attr("method"),
                    action: $el.attr("action"),
                    size: $el.attr("size"),
                    type: $el.attr("type"),
                    icon: $el.attr("icon"),
                    dropdown: $el.attr("dropdown"),
                    action_options: "refer_id="+refer_id,
                    pull: pull,
                    context: context
                };
                if (opts.dropdown) {
                    var inner="";
                    $el.children().each(function() {
                        var $el2=$(this);
                        var tag=$el2.prop("tagName");
                        if (tag=="item") {
                            var opts2={
                                string: $el2.attr("string"),
                                method: $el2.attr("method"),
                                action: $el2.attr("action"),
                                states: $el2.attr("states"),
                                action_options: "refer_id="+refer_id,
                                context: context
                            }
                            var view=Item.make_view(opts2);
                            inner+="<li id=\""+view.cid+"\" class=\"view\"></li>";
                        }
                    });
                    opts.inner=function() {return inner; };
                    var view=ButtonGroup.make_view(opts);
                } else {
                    var view=Button.make_view(opts);
                }
                cell.append("<div id=\""+view.cid+"\" class=\"view\"></div>");
            } else if (tag=="related_tabs") {
                var span=$el.attr("span")
                if (span) cols=parseInt(span);
                else span=12;
                if (col+span>12) {
                    col=0;
                    row=$('<div class="row"/>');
                    body.append(row);
                }
                var cell=$('<div/>');
                cell.addClass("col-sm-"+span);
                row.append(cell);
                var opts={
                    tabs_layout: $el,
                    context: context
                };
                var view=RelatedTabs.make_view(opts);
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
                    cell.addClass("offset"+offset);
                }
                row.append(cell);
                var opts={
                    group_layout: $el,
                    attrs: $el.attr("attrs"),
                    span: $el.attr("span"),
                    readonly: true,
                    form_layout: $el.attr("form_layout"),
                    context: context
                };
                if (col>0 && !opts.span) {
                    opts.span=12-col;
                }
                var view_cls=get_view_cls("group");
                var view=view_cls.make_view(opts);
                cell.append("<div id=\""+view.cid+"\" class=\"view\"></div>");
                col+=span;
            }
        });
        return body.html();
    },

    render_toolbar: function(context) {
        //log("render_toolbar",this,context);
        var that=this;
        var html=$("<div/>");
        if (this.options.next_action) {
            if (check_model_permission(this.options.model,"write")) {
                var opts={
                    string: "Edit",
                    size: "small",
                    icon: "edit",
                    onclick: function() { that.click_edit(); },
                    context: context
                };
                var view=Button.make_view(opts);
                html.append("<div id=\""+view.cid+"\" class=\"view\"></div>");
            }
        }
        var $el=this.$layout.find("head field");
        if ($el.length>0) {
            var name=$el.attr("name");
            html.append("<b style='margin-left:10px'>"+field_value(name,context)+"</b>");
        }
        this.$layout.children("head").children().each(function() {
            var $el=$(this);
            var tag=$el.prop("tagName");
            if (tag=="button") {
                var opts={
                    string: $el.attr("string"),
                    method: $el.attr("method"),
                    action: $el.attr("action"),
                    size: $el.attr("size")||"small",
                    type: $el.attr("type"),
                    next: $el.attr("next"),
                    icon: $el.attr("icon"),
                    dropdown: $el.attr("dropdown"),
                    pull: "right", // XXX
                    context: context
                };
                opts.action_options="refer_id="+that.active_id;
                if (opts.dropdown) {
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
                                states: $el2.attr("states"),
                                confirm: $el2.attr("confirm"),
                                context: context
                            }
                            if (!opts2.action_options||opts2.action_options[0]!="{") { // XXX: deprecated
                                opts2.action_options=(opts2.action_options?opts2.action_options+"&":"")+"refer_model="+that.options.model+"&refer_id="+that.active_id;
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
                html.append("<div id=\""+view.cid+"\" class=\"view\"></div>");
            }
        });
        return html.html();
    },

    render_foot: function(context) {
        //log("render_foot",this,context);
        var that=this;
        var foot=$("<div/>");
        this.$layout.find("foot").children().each(function() {
            var $el=$(this);
            var tag=$el.prop("tagName");
            if (tag=="button") {
                var opts={
                    string: $el.attr("string"),
                    method: $el.attr("method"),
                    action: $el.attr("action"),
                    action_context: $el.attr("action_context"),
                    size: $el.attr("size")||"large",
                    type: $el.attr("type"),
                    next: $el.attr("next"),
                    icon: $el.attr("icon"),
                    states: $el.attr("states"),
                    perm: $el.attr("perm"),
                    attrs: $el.attr("attrs"),
                    split: $el.attr("split"),
                    confirm: $el.attr("confirm"),
                    context: context
                };
                if (that.active_id) {
                    opts.action_options="refer_id="+that.active_id;
                }
                if (opts.split) {
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
                                if (opts2.action_options) { // XXX
                                    opts2.action_options+="&";
                                } else{
                                    opts2.action_options="";
                                }
                                opts2.action_options+="refer_id="+that.active_id; // XXX: orig_id
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
                foot.append("<div id=\""+view.cid+"\" class=\"view\"></div>");
            }
        });
        return foot.html();
    },

    render_related: function(context) {
        //log("page_view.render_related",this,context);
        var that=this;
        var model=this.model;
        if (!model.id) return "";
        var content=$("<div/>");
        var $related=this.$layout.find("related");
        if ($related.attr("tabs")) {
            $ul=$("<ul class='nav nav-tabs nf-nav-tabs'>");
            $ul.appendTo(content);
            var active_tab=this.related_tab||0;
            var i=0;
            $related.children().each(function() {
                var $el=$(this);
                var tag=$el.prop("tagName");
                var $li=$("<li><a href='#' class='related-tab' data-tab='"+i+"'>"+$el.attr("string")+"</a></li>");
                $ul.append($li);
                if (i==active_tab) {
                    $li.addClass("active");
                    if (tag=="action") {
                        var opts={
                            name: $el.attr("name")
                        };
                        var expr=$el.attr("options");
                        var data=that.model.toJSON();
                        var vals=eval_json(expr,data);
                        _.extend(opts,vals);
                        var view_cls=get_view_cls("action_view");
                        var view=view_cls.make_view(opts);
                        content.append("<div id=\""+view.cid+"\" class=\"view\"></div>");
                    } else if (tag=="field") {
                        var name=$el.attr("name");
                        var model=that.model;
                        var f=model.get_field(name);
                        var cond=[];
                        if (f.relfield) {
                            cond.push([f.relfield,"=",model.id]);
                        }
                        if (f.condition) {
                            if (_.isString(f.condition)) {
                                var data=that.model.toJSON();
                                var cond2=eval_json(f.condition,data);
                                cond.push(cond2);
                            }
                        }
                        var opts={
                            model: f.relation,
                            condition: cond,
                            order: f.order,
                            show_search: true // XXX
                        };
                        var $layout=$el.find("list");
                        if ($layout.length>0) {
                            opts.list_layout=$layout;
                        }
                        var view_cls=get_view_cls("list_view");
                        var view=view_cls.make_view(opts);
                        content.append("<div id=\""+view.cid+"\" class=\"view\"></div>");
                    }
                }
                i+=1;
            });
        } else {
            $related.children().each(function() {
                var $el=$(this);
                var tag=$el.prop("tagName");
                if (tag=="field") {
                    var name=$el.attr("name");
                    var opts={
                        model: that.options.model,
                        field_name: name,
                        attrs: $el.attr("attrs"),
                        list_view_xml: $el.attr("list_view_xml"),
                        click_action: $el.attr("click_action"), // XXX
                        action: $el.attr("action"),
                        context: context
                    };
                    var $list=$el.find("list");
                    if ($list.length>0) {
                        opts.list_layout=$list;
                    }
                    var $form=$el.find("form");
                    if ($form.length>0) {
                        opts.form_layout=$form;
                    }
                    var view_cls=get_view_cls("related");
                    var view=view_cls.make_view(opts);
                    content.append("<div id=\""+view.cid+"\" class=\"view\"></div>");
                }
            });
        }
        return content.html();
    },

    click_bread: function(e) {
        log("page_view.click_bread");
        e.preventDefault();
        var action={
            name: this.options.action_name,
            mode: this.options.prev_mode || "list", // XXX: change this, use event
            active_id: this.active_id
        }
        if (this.options.search_condition) {
            action.search_condition=this.options.search_condition;
        }
        if (this.options.tab_no) {
            action.tab_no=this.options.tab_no; // XXX: simplify all this stuff
        }
        if (this.options.offset) {
            action.offset=this.options.offset; // XXX: simplify all this stuff
        }
        exec_action(action);
    },

    click_edit: function() {
        log("page_view.click_edit");
        var action={
            name: this.options.action_name,
            mode: "form",
            active_id: this.active_id
        }
        if (this.options.search_condition) {
            action.search_condition=this.options.search_condition;
        }
        if (this.options.tab_no) {
            action.tab_no=this.options.tab_no;
        }
        if (this.options.offset) {
            action.offset=this.options.offset;
        }
        exec_action(action);
    },

    click_related_tab: function(e) {
        log("page_view.click_related_tab");
        e.preventDefault();
        this.related_tab=$(e.target).closest("a").data("tab");
        log("tab_no",this.related_tab);
        var html=this.render_related(this.context);
        this.$el.find(".related").html(html);
        var that=this;
        this.$el.find(".view").each(function() {
            var view_id=$(this).attr("id");
            //log("render sub",view_id);
            var view=get_view_inst(view_id);
            view.options.show_pagination=true;
            view.render();
            $(this).replaceWith(view.$el);
            that.subviews[view_id]=view;
        });
    }
});

PageView.register();
