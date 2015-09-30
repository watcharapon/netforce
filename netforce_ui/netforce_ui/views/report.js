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

var Report=NFView.extend({
    _name: "report",

    initialize: function(options) {
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
            this.$layout=$(doc).children();
        } else {
            this.$layout=layout;
        }
        if (this.options.active_id) {
            this.active_id=parseInt(this.options.active_id);
        } else {
            this.active_id=null;
        }
        this.data.render_body=function(ctx) { return that.render_body.call(that,ctx); };
        this.data.render_foot=function(ctx) { return that.render_foot.call(that,ctx); };
    },

    render: function() {
        var that=this;
        var model_name=this.options.model;
        var field_names=[];
        var model_cls=get_model_cls(model_name);
        this.$layout.find("field").each(function() {
            if ($(this).parents("field").length>0) {
                return;
            }
            if ($(this).parents("related").length>0) {
                return;
            }
            var name=$(this).attr("name");
            field_names.push(name);
        });
        this.field_names=field_names;
        this.data.page_title=this.options.string;
        this.render_waiting();
        if (this.active_id) {
            rpc_execute(model_name,"read",[[this.active_id]],{field_names:field_names,get_time:true},function(err,data) {
                var read_time=data[0].read_time;
                delete data[0].read_time;
                that.model=new NFModel(data[0],{name:model_name});
                that.model.set_orig_data(data[0]);
                that.model.read_time=read_time;
                that.data.context.data=data[0];
                that.data.context.model=that.model;
                NFView.prototype.render.call(that);
                that.show_report();
            });
        } else {
            var ctx=clean_context(_.extend({},this.context,this.options));
            if (this.options.defaults) {
                ctx.defaults=this.options.defaults;
            }
            var opts={
                field_names: field_names,
                context: ctx
            };
            rpc_execute(model_name,"default_get",[],opts,function(err,data) {
                that.model=new NFModel(data,{name:model_name});
                that.data.context.data=data;
                that.data.context.model=that.model;
                NFView.prototype.render.call(that);
                that.show_report();
            });
        }
        return this;
    },

    render_waiting: function() {
        var img=$("<img/>").attr("src","/static/img/spinner.gif");
        this.$el.empty();
        this.$el.append(img);
    },

    render_body: function(context) {
        var that=this;
        var body=$("<div/>");
        var row=$('<div class="row"/>');
        body.append(row);
        var col=0;
        var readonly=this.readonly;
        this.$layout.children().each(function() {
            var $el=$(this);
            var tag=$el.prop("tagName");
            if (tag=="field") {
                var name=$el.attr("name");
                var field=get_field(that.options.model,name);
                if (field.type=="one2many" || field.type=="many2many") {
                    default_span=12;
                } else {
                    default_span=5;
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
                row.append(cell);
                var opts={
                    name: name,
                    readonly: $el.attr("readonly")||that.readonly,
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
                                        readonly: $el2.attr("readonly"),
                                        onchange: $el2.attr("onchange"),
                                        onfocus: $el2.attr("onfocus")
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
                if (span) span=parseInt(span);
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
                    readonly: $el.attr("readonly")||that.readonly,
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
                    readonly: $el.attr("readonly")||that.readonly,
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
            } else if (tag=="label") {
                var span=$el.attr("span")
                if (span) cols=parseInt(span);
                else span=12;
                var cell=$('<div style="margin-bottom:10px"/>');
                cell.addClass("col-sm-"+span);
                row.append(cell);
                cell.text($el.attr("string"));
                col+=span;
            } else if (tag=="button") {
                var span=$el.attr("span")
                if (span) cols=parseInt(span);
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
            } else if (tag=="html") {
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
                cell.append($el.children().clone());
                col+=span;
            }
        });
        return body.html();
    },

    render_foot: function(context) {
        var that=this;
        var foot=$("<div/>");
        if (!this.$layout.find("foot").attr("replace")) {
            if (this.options.report_type=="jasper") {
                var opts={
                    string: "Export PDF",
                    type: "primary",
                    onclick: function() {
                        that.export_pdf();
                    },
                    context: context
                };
                var view=Button.make_view(opts);
                foot.append("<div id=\""+view.cid+"\" class=\"view\"></div>");
                var opts={
                    string: "Export XLS",
                    onclick: function() {
                        that.export_xls();
                    },
                    context: context
                };
                var view=Button.make_view(opts);
                foot.append("<div id=\""+view.cid+"\" class=\"view\"></div>");
            } else {
                var opts={
                    string: "Run Report",
                    type: "primary",
                    onclick: function() {
                        that.run_report();
                    },
                    context: context
                };
                var view=Button.make_view(opts);
                foot.append("<div id=\""+view.cid+"\" class=\"view\"></div>");
                var opts={
                    string: "Export XLS",
                    onclick: function() {
                        that.export_xls();
                    },
                    context: context
                };
                var view=Button.make_view(opts);
                foot.append("<div id=\""+view.cid+"\" class=\"view\"></div>");
                if (this.options.report_template_xls_custom) {
                    var opts={
                        string: "Export Custom XLS",
                        onclick: function() {
                            that.export_custom_xls();
                        },
                        context: context
                    };
                    var view=Button.make_view(opts);
                    foot.append("<div id=\""+view.cid+"\" class=\"view\"></div>");
                }
            }
        }
        this.$layout.find("foot").children().each(function() {
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
                    states: $el.attr("states"),
                    perm: $el.attr("perm"),
                    attrs: $el.attr("attrs"),
                    split: $el.attr("split"),
                    context: context
                };
                if (that.active_id) {
                    opts.action_options="refer_id="+that.active_id;
                }
                var view=Button.make_view(opts);
                foot.append("<div id=\""+view.cid+"\" class=\"view\"></div>");
            }
        });
        return foot.html();
    },

    run_report: function() {
        log("run_report",this);
        var that=this;
        if (!this.model.check_required()) {
            set_flash("error","Some required fields are missing");
            render_flash();
            return;
        }
        this.model.save({},{
            success: function() {
                that.active_id=that.model.id;
                that.render();
            },
            error: function(model,err) {
                log("save error",err);
                set_flash("error",err.message);
                render_flash();
            }
        });
    },

    show_report: function() {
        log("report.show_report",this);
        var that=this;
        var ids;
        var ctx={};
        if (this.model.id) {
            ids=[this.model.id];
        } else {
            ids=null;
            if (this.options.defaults) ctx.defaults=this.options.defaults;
        }
        rpc_execute(this.options.model,"get_report_data",[ids],{context:ctx},function(err,data) {
            if (err) {
                set_flash("error",err.message);
                return;
            }
            if (!data) return;
            var tmpl_name=that.options.report_template;
            if (!tmpl_name) throw "Missing report template";
            log("report_template",tmpl_name);
            tmpl=get_template(tmpl_name);
            data.context={}; // XXX
            var report_html=tmpl(data);
            that.$el.find(".report-content").html(report_html);
            that.$el.find(".report-content").find(".view").each(function() {
                var view_id=$(this).attr("id");
                var view=get_view_inst(view_id);
                view.render();
                $(this).replaceWith(view.$el);
                that.subviews[view_id]=view;
            });

            if (that.model.id) {
                var h=window.location.hash.substr(1);
                var action=qs_to_obj(h);
                action.active_id=that.model.id;
                var h2=obj_to_qs(action);
                workspace.navigate(h2);
            }
        });
    },

    export_pdf: function() {
        log("export_pdf",this);
        var that=this;
        if (!this.model.check_required()) {
            set_flash("error","Some required fields are missing");
            render_flash();
            return;
        }
        this.model.save({},{
            success: function() {
                var url="/report?type=report_jasper&model="+that.options.model+"&refer_id="+that.model.id+"&convert=pdf&nonce="+(new Date()).getTime();
                if (that.options.report_template_jasper) url+="&template="+that.options.report_template_jasper;
                else if (that.options.template_method) url+="&template_method="+that.options.template_method;
                download_url(url);
            },
            error: function(model,err) {
                log("save error",err);
                set_flash("error",err.message);
                render_flash();
            }
        });
    },

    export_xls: function() {
        log("export_xls",this);
        var that=this;
        if (!this.model.check_required()) {
            set_flash("error","Some required fields are missing");
            render_flash();
            return;
        }
        this.model.save({},{
            success: function() {
                var url="/report_export_xls?model="+that.options.model+"&active_id="+that.model.id+"&template="+that.options.report_template_xls+"&nonce="+(new Date()).getTime();
                download_url(url);
            },
            error: function(model,err) {
                log("save error",err);
                set_flash("error",err.message);
                render_flash();
            }
        });
    },

    export_custom_xls: function() {
        log("export_custom_xls",this);
        var that=this;
        if (!this.model.check_required()) {
            set_flash("error","Some required fields are missing");
            render_flash();
            return;
        }
        this.model.save({},{
            success: function() {
                var url="/report_export_xls?model="+that.options.model+"&active_id="+that.model.id+"&method=get_report_data_custom&template="+that.options.report_template_xls_custom+"&fast_render=1&nonce="+(new Date()).getTime();
                download_url(url);
            },
            error: function(model,err) {
                log("save error",err);
                set_flash("error",err.message);
                render_flash();
            }
        });
    }
});

Report.register();
