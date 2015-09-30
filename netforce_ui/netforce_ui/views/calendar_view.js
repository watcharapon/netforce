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

var CalendarView=NFView.extend({
    _name: "calendar_view",
    events: {
        "click .search-btn": "click_search"
    },

    initialize: function(options) {
        log("calendar_view.initialize",this);
        var that=this;
        NFView.prototype.initialize.call(this,options);
        if (!this.options.model) throw "CalendarView: missing model";
        if (this.options.calendar_layout) {
            var layout=this.options.calendar_layout;
        } else {
            if (this.options.view_xml) {
                var view=get_xml_layout({name:this.options.view_xml});
            } else {
                var view=get_xml_layout({model:this.options.model,type:"calendar"});
            }
            var layout=view.layout;
        }
        if (_.isString(layout)) {
            var doc=$.parseXML(layout);
            this.$layout=$(doc).children();
        } else {
            this.$layout=layout;
        }
        if (this.options.tabs) {
            var tabs=JSON.parse(this.options.tabs);
            this.data.tabs=[];
            _.each(tabs,function(tab) {
                that.data.tabs.push({
                    string: tab[0],
                    action: that.options.action_name,
                    action_opts: "mode=calendar&tab="+tab[0]
                });
            });
            log("XXX tabs",this.data.tabs);
        }
        this.modes=this.options.modes;
        if (!this.modes) this.modes="list,form";
        if (_.isString(this.modes)) {
            this.modes=this.modes.split(",");
        }
        this.data.render_top=function(ctx) { return that.render_top.call(that,ctx); };
    },

    render: function() {
        log("calendar_view.render",this);
        var that=this;
        var field_names=[];
        var start_field=this.$layout.attr("start_field")||this.$layout.attr("date_field");
        var end_field=this.$layout.attr("end_field");
        if (!start_field) throw "Missing start field in calendar view";
        var start_field_info=get_field(this.options.model,start_field);
        if (start_field_info.type=="datetime") {
            var show_time=true;
        } else {
            var show_time=false;
        }
        field_names.push(start_field);
        if (end_field) {
            field_names.push(end_field);
        }
        this.$layout.find("field").each(function() {
            field_names.push($(this).attr("name"));
        });
        var model_cls=get_model(this.options.model);
        if (end_field) {
            var name_field=field_names[2];
        } else {
            var name_field=field_names[1];
        }
        if (!name_field) throw "Missing name field in calendar";
        var get_events=function(start,end,timezone,cb) {
            log("calendar.get_events",start,end,timezone,cb);
            var date_from=moment(start).format("YYYY-MM-DD");
            var date_to=moment(end).format("YYYY-MM-DD");
            var condition=[[start_field,">=",date_from],[start_field,"<=",date_to]];
            var opts={
                field_names: field_names
            };
            rpc_execute(that.options.model,"search_read",[condition],opts,function(err,data) {
                that.collection=new NFCollection(data,{name:that.options.model});
                var events=[];
                that.collection.each(function(model) {
                    var ctx={model:model,no_link:true};
                    var title=field_value(name_field,ctx)||"";
                    var start=model.get(start_field);
                    if (start) {
                        start=moment(start).toDate();
                        var event={title:title,start:start,model:model};
                        if (end_field) {
                            var end=model.get(end_field);
                            if (end) {
                                event.end=moment(end).toDate();
                            }
                        }
                        var colors=that.eval_colors(model);
                        var event_color=null;
                        for (var color in colors) {
                            if (!colors[color]) continue;
                            if (color.indexOf(",")!=-1) continue;
                            event_color=color;
                        }
                        if (event_color) event.color=event_color;
                        events.push(event);
                    }
                });
                log("calendar events",events);
                cb(events);
            });
        }
        NFView.prototype.render.call(that);
        if (that.options.tabs && !that.options.tab) { // XXX
            that.$el.find(".nav-tabs").children().first().addClass("active");
        }
        setTimeout(function() { // XXX
            var opts={
                header: {
                    left: 'prev,next today month'+(show_time?',agendaWeek,agendaDay':',basicWeek,basicDay'),
                    center: 'title',
                    right: ''
                },
                editable: true,
                events: get_events,
                eventLimit: 11,
                eventRender:function (event,element) {
                    var vals=[];
                    var model=event.model;
                    _.each(field_names,function(name,i) {
                        if (end_field) {
                            if (i<3) return;
                        } else {
                            if (i<2) return;
                        }
                        var f=model_cls.fields[name];
                        if (!f) throw "Invalid field: "+name;
                        var ctx={model:model};
                        var val=field_value(name,ctx)||"";
                        vals.push(f.string+": "+val);
                    });
                    var title=vals.join("<br/>");
                    if (element.hasClass("fc-day-grid-event")) {
                        element.find(".fc-content").tooltip({
                            placement: "bottom",
                            html: true,
                            container: "body",
                            title: title
                        });
                    }
                },
                eventClick: function(calEvent,jsEvent,view) {
                    var model=calEvent.model;
                    var action=find_details_action(model.name,model.id);
                    exec_action(action);
                },
                dayClick: function(date,jsEvent,view) {
                    log("day_click",date);
                    var model=that.options.model;
                    var action=find_new_action(model);
                    var start_field=that.$layout.attr("start_field")||that.$layout.attr("date_field");
                    action.defaults={};
                    action.defaults[start_field]=moment(date).format("YYYY-MM-DD");
                    exec_action(action);
                },
                viewRender: function(view) {
                    var h=window.location.hash.substr(1);
                    var action=qs_to_obj(h);
                    var d=that.$el.find(".calendar").fullCalendar("getDate");
                    action.calendar_date=moment(d).format("YYYY-MM-DD");
                    action.calendar_mode=view.name;
                    var h2=obj_to_qs(action);
                    workspace.navigate(h2);
                },
                eventDrop: function(calEvent,delta,revertFunc) {
                    var model=calEvent.model;
                    var vals={};
                    if (show_time) {
                        vals[start_field]=calEvent.start.format("YYYY-MM-DD HH:mm:ss");
                    } else {
                        vals[start_field]=calEvent.start.format("YYYY-MM-DD");
                    }
                    if (end_field) {
                        if (show_time) {
                            vals[end_field]=calEvent.end.format("YYYY-MM-DD HH:mm:ss");
                        } else {
                            vals[end_field]=calEvent.end.format("YYYY-MM-DD");
                        }
                    }
                    log("calendar.drop",model.id,vals);
                    rpc_execute(that.options.model,"write",[[model.id],vals],{},function(err,data) {
                        if (err) {
                            alert("Error: failed to update dates");
                            revertFunc();
                        }
                    });
                },
                eventResize: function(calEvent,delta,revertFunc) {
                    var model=calEvent.model;
                    var vals={};
                    if (show_time) {
                        vals[end_field]=calEvent.end.format("YYYY-MM-DD HH:mm:ss");
                    } else {
                        vals[end_field]=calEvent.end.format("YYYY-MM-DD");
                    }
                    log("calendar.resize",model.id,vals);
                    rpc_execute(that.options.model,"write",[[model.id],vals],{},function(err,data) {
                        if (err) {
                            alert("Error: failed to update duration");
                            revertFunc();
                        }
                    });
                }
            }
            if (that.options.calendar_mode) {
                opts.defaultView=that.options.calendar_mode;
            }
            that.$el.find(".calendar").fullCalendar(opts);
            if (that.options.calendar_date) {
                var d=moment(that.options.calendar_date).toDate();
                that.$el.find(".calendar").fullCalendar("gotoDate",d);
            }
            var head=that.$el.find(".fc-header-right");
            head.append('<span class="fc-header-space"></span>');
            head.append('<span class="fc-button fc-state-default fc-corner-left fc-corner-right search-btn"><i class="icon-search"></i> Search</span>');
        },100);
        return this;
    },

    render_waiting: function() {
        var img=$("<img/>").attr("src","/static/img/spinner.gif");
        this.$el.empty();
        this.$el.append(img);
    },

    render_top: function(context) {
        log("calendar_view.render_top",this,context);
        var that=this;
        var html=$("<div/>");
        if (!this.$layout.find("top").attr("replace")) {
            var new_string="New";
            var model_cls=get_model(this.options.model);
            model_string=this.options.model_string||model_cls.string;
            if (model_string) {
                new_string+=" "+model_string;
            }
            var opts={
                string: new_string,
                action: this.options.action_name,
                action_options: "mode=form",
                icon: "plus-sign",
                context: context
            };
            var view=Button.make_view(opts);
            html.append("<div id=\""+view.cid+"\" class=\"view\"></div>");
            var opts={
                string: "Import",
                action: "import_data",
                action_options: "import_model="+that.options.model+"&next="+this.options.action_name,
                icon: "download",
                context: that.data.context
            };
            var view=Button.make_view(opts);
            html.append("<div id=\""+view.cid+"\" class=\"view\"></div>");
        }
        this.$layout.find("top").children().each(function() {
            var $el=$(this);
            var tag=$el.prop("tagName");
            if (tag=="button") {
                var opts={
                    string: $el.attr("string"),
                    action: $el.attr("action"),
                    action_options: $el.attr("action_options"),
                    size: $el.attr("size"),
                    type: $el.attr("type"),
                    next: $el.attr("next"),
                    icon: $el.attr("icon"),
                    perm: $el.attr("perm"),
                    dropdown: $el.attr("dropdown"),
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
                                action: $el2.attr("action"),
                                action_options: $el2.attr("action_options"),
                                perm: $el2.attr("perm"),
                                context: context
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
        if (_.contains(this.modes,"list")) {
            var opts={
                string: "List",
                icon: "list",
                pull: "right",
                onclick: function() { that.show_list(); },
                context: context
            };
            var view=Button.make_view(opts);
            html.append("<div id=\""+view.cid+"\" class=\"view\"></div>");
        }
        return html.html();
    },

    show_list: function() {
        log("calendar_view.show_list",this);
        var action={
            name: this.options.action_name,
            mode: "list"
        };
        exec_action(action);
    },

    click_search: function(e) {
        e.preventDefault();
        e.stopPropagation();
        this.show_search();
    },

    show_search: function(e) {
        log("calendar_view.show_search");
        var that=this;
        var opts={
            model: this.options.model
        };
        if (this.options.search_view_xml) {
            opts.view_xml=this.options.search_view_xml;
        } else if (this.options.search_layout) {
            opts.view_layout=this.options.search_layout;
        }
        var view=new SearchView({options:opts});
        if (that.search_condition) {
            view.set_condition(that.search_condition);
        }
        view.render();
        this.$el.find(".search-btn").hide();
        this.$el.find(".search").append(view.el);
        view.on("close",function() {
            that.$el.find(".search-btn").show();
        });
        view.on("search",function() {
            that.search_condition=view.get_condition();
            that.render();
            var h=window.location.hash.substr(1);
            var action=qs_to_obj(h);
            action.search_condition=that.search_condition;
            var h2=obj_to_qs(action);
            workspace.navigate(h2);
        });
    },

    eval_colors: function(model) {
        var str=this.$layout.attr("colors");
        if (!str) return {};
        var expr=JSON.parse(str);
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
        return attrs;
    }
});

CalendarView.register();
