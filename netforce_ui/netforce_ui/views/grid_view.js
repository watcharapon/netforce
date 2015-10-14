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

var GridView=NFView.extend({
    _name: "grid_view",
    events: {
        "click .search-btn": "click_search"
    },

    initialize: function(options) {
        //log("grid_view.initialize",this);
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
        this.modes=this.options.modes;
        if (!this.modes) this.modes="list,form";
        if (_.isString(this.modes)) {
            this.modes=this.modes.split(",");
        }
        this.data.render_top=function(ctx) { return that.render_top.call(that,ctx); };
        this.data.render_head=function(ctx) { return that.render_head.call(that,ctx); };
        this.data.on_select_item=_.bind(this.on_select_item,this);
    },

    render: function() {
        //log("grid_view.render",this);
        var that=this;
        var model_name=this.options.model;
        var field_names=[];
        var model_cls=get_model_cls(model_name);
        this.$grid.find("field").each(function() {
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
        var condition=this.options.condition||[];
        if (_.isString(condition)) {
            var ctx=clean_context(_.extend({},this.context,this.options));
            condition=eval_json(condition,ctx);
        }
        var opts={
            field_names: field_names,
            order: this.options.order,
            offset: this.options.offset,
            limit: this.options.limit||25,
            count: true
        }
        var grid_span=parseInt(this.$grid.attr("span"))||12;
        this.num_cols=parseInt(this.$grid.attr("num_cols")||this.options.num_cols)||1;
        this.data.grid_item_span=grid_span/this.num_cols;
        if (12%this.num_cols) {
            throw "Invalid number of columns in grid view: "+this.num_cols;
        }
        this.data.page_title=this.$grid.attr("title")||this.options.string;
        rpc_execute(model_name,"search_read",[condition],opts,function(err,data) {
            that.collection=new NFCollection(data[0],{name:model_name});
            that.collection.condition=condition;
            that.collection.order=that.options.order;
            that.collection.fields=field_names;
            //if (that.options.show_full) { // FIXME
                that.collection.count=data[1];
                that.collection.offset=that.options.offset;
                that.collection.limit=that.options.limit||25;
            //}
            that.collection.on("reload",that.reload,that);
            that.collection.on("reset",that.render_collection,that);
            that.data.context.data=data[0];
            that.data.context.collection=that.collection;
            that.data.context.model=null; // XXX
            that.data.grid_layout=that.$grid;
            that.render_collection();
        });
        return this;
    },

    render_top: function(context) {
        var that=this;
        var html=$("<div/>");
        if (!this.$grid.find("top").attr("replace")) {
            if (check_model_permission(this.options.model,"create")) {
                var new_string="New";
                var model_cls=get_model(this.options.model);
                model_string=this.options.model_string||model_cls.string;
                if (model_string) {
                    new_string+=" "+model_string;
                }
                var opts={
                    string: new_string,
                    onclick: function() { that.trigger("change_mode",{mode:"form"}); },
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
        }
        if (_.contains(this.modes,"list")) {
            var opts={
                string: "List",
                icon: "align-justify",
                pull: "right",
                onclick: function() { that.trigger("change_mode",{mode:"list"}); },
                context: context
            };
            var view=Button.make_view(opts);
            html.append("<div id=\""+view.cid+"\" class=\"view\"></div>");
        }
        if (_.contains(this.modes,"Calendar")) {
            var opts={
                string: "Calendar",
                icon: "calendar",
                pull: "right",
                onclick: function() { that.trigger("change_mode",{mode:"calendar"}); },
                context: context
            };
            var view=Button.make_view(opts);
            html.append("<div id=\""+view.cid+"\" class=\"view\"></div>");
        }
        return html.html();
    },

    render_head: function(context) {
        var that=this;
        var html=$("<div/>");
        if (_.isEmpty(this.options.search_condition)) {
            html.append('<button type="button" class="btn btn-sm btn-default pull-right search-btn" style="white-space:nowrap;"><i class="icon-search"></i> Search</button>');
        }
        return html.html();
    },

    click_search: function(e) {
        e.preventDefault();
        e.stopPropagation();
        this.show_search();
    },

    show_search: function(e) {
        log("grid_view.show_search");
        var that=this;
        var opts={
            model: this.options.model
        };
        if (this.options.search_view_xml) {
            opts.view_xml=this.options.search_view_xml;
        } else if (this.options.search_layout) {
            opts.view_layout=this.options.search_layout;
        }
        var $el=this.$grid.find("search");
        if ($el.length>0) {
            opts.view_layout=$el;
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
            that.collection.offset=0;
            that.render();

            var h=window.location.hash.substr(1);
            var action=qs_to_obj(h);
            action.search_condition=that.search_condition;
            if (_.isEmpty(action.search_condition)) delete action.search_condition;
            if (action.offset) delete action.offset;
            var h2=obj_to_qs(action);
            workspace.navigate(h2);
        });
    },

    render_collection: function() {
        var items=[];
        var rows=[{
            items: items
        }];
        var c=0;
        this.collection.each(function(m) {
            if (c>=this.num_cols) {
                items=[];
                rows.push({
                    items: items
                });
                c=0;
            }
            items.push({
                data: m
            });
            c+=1;
        });
        this.data.rows=rows;
        NFView.prototype.render.call(this);
    },

    reload: function() {
        this.render();
    },

    on_select_item: function(model_id) {
        log("grid_view.on_select_item",model_id);
        this.trigger("click_item",{active_id:model_id});
    }
});

GridView.register();
