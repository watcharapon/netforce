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

var MultiView=NFView.extend({
    _name: "multi_view",

    initialize: function(options) {
        //log("multi_view.initialize",this);
        NFView.prototype.initialize.call(this,options);
        if (!this.options.model) throw "MultiView: missing model";
        this.modes=this.options.modes||"list,form";
        if (_.isString(this.modes)) {
            this.modes=this.modes.split(",");
        }
        //log("modes",this.modes);
        this.mode=this.options.mode||this.modes[0];
        //log("mode",this.mode);
        if (this.options.search_condition) {
            this.search_condition=this.options.search_condition;
        }
        if (_.isString(this.search_condition)) {
            this.search_condition=JSON.parse(this.search_condition);
        }
    },

    render: function() {
        //log("multi_view render",this);
        var that=this;
        this.remove_subviews();
        if (this.mode=="list") {
            var opts={
                model: this.options.model,
                active_id: this.options.active_id,
                condition: this.options.condition,
                search_condition: this.search_condition,
                tab_no: this.options.tab_no,
                order: this.options.order,
                limit: this.options.limit,
                string: this.options.string,
                view_xml: this.options.list_view_xml,
                search_view_xml: this.options.search_view_xml,
                show_full: true, // XXX
                tabs: this.options.tabs,
                action_name: this.options.name, // XXX
                model_string: this.options.model_string,
                offset: this.options.offset,
                modes: this.modes,
                context: this.context
            };
            if (_.contains(this.modes,"page")) {
                opts.action=this.options.name;
                opts.action_options={mode:"page"};
            } else if (_.contains(this.modes,"form")) {
                opts.action=this.options.name;
                opts.action_options={mode:"form"};
            }
            var view=new ListView({options:opts});
            view.render();
            this.$el.append(view.el);
            this.subviews[view.cid]=view;
        } else if (this.mode=="calendar") {
            var opts={
                model: this.options.model,
                condition: this.options.condition,
                search_condition: this.search_condition,
                order: this.options.order,
                limit: this.options.limit,
                string: this.options.string,
                view_xml: this.options.calendar_view_xml,
                search_view_xml: this.options.search_view_xml,
                tabs: this.options.tabs,
                tab: this.options.tab,
                action_name: this.options.name, // XXX
                model_string: this.options.model_string,
                offset: this.options.offset,
                modes: this.modes,
                calendar_date: this.options.calendar_date,
                calendar_mode: this.options.calendar_mode,
                context: this.context
            };
            var view=new CalendarView({options:opts});
            view.render();
            this.$el.append(view.el);
            this.subviews[view.cid]=view;
        } else if (this.mode=="form") {
            var opts={
                model: this.options.model,
                active_id: this.options.active_id,
                search_condition: this.options.search_condition,
                tab_no: this.options.tab_no,
                offset: this.options.offset,
                string: this.options.string,
                view_xml: this.options.form_view_xml,
                next_action: this.options.name,
                refer_model: this.options.refer_model, // XXX
                refer_id: this.options.refer_id, // XXX
                action_name: this.options.name, // XXX
                model_string: this.options.model_string,
                defaults: this.options.defaults,
                modes: this.modes,
                context: this.context
            };
            if (_.contains(this.modes,"page")) {
                opts.next_action_options="mode=page";
            } else {
                opts.next_action_options="mode=form";
            }
            if (this.search_condition) {
                opts.next_action_options+="&search_condition="+JSON.stringify(this.options.search_condition); // XXX
            }
            if (this.options.tab_no) {
                opts.next_action_options+="&tab_no="+this.options.tab_no // XXX: simplify all this
            }
            if (this.options.offset) {
                opts.next_action_options+="&offset="+this.options.offset // XXX: simplify all this
            }
            var view=new FormView({options:opts});
            view.render();
            this.$el.append(view.el);
            this.subviews[view.cid]=view;
        } else if (this.mode=="page") {
            var opts={
                model: this.options.model,
                active_id: this.options.active_id,
                search_condition: this.options.search_condition,
                tab_no: this.options.tab_no,
                related_tab: this.options.related_tab,
                offset: this.options.offset,
                string: this.options.string,
                view_xml: this.options.page_view_xml||this.options.form_view_xml,
                action_name: this.options.name, // XXX
                context: this.context
            };
            if (_.contains(this.modes,"form")) { // XXX
                opts.next_action=this.options.name;
                opts.next_action_options="mode=form";
            };
            if (_.contains(this.modes,"grid")) { // XXX: change this, use event instead
                opts.prev_mode="grid";
            } else {
                opts.prev_mode="list";
            }
            var view=new PageView({options:opts});
            view.render();
            this.$el.append(view.el);
            this.subviews[view.cid]=view;
        } else if (this.mode=="tree") {
            var opts={
                model: this.options.model,
                condition: this.options.condition,
                string: this.options.string,
                view_xml: this.options.tree_view_xml,
                context: this.context
            };
            var view=new TreeView({options:opts});
            view.render();
            this.$el.append(view.el);
            this.subviews[view.cid]=view;
        } else if (this.mode=="grid") {
            var opts={
                model: this.options.model,
                condition: this.options.condition,
                order: this.options.order,
                string: this.options.string,
                view_xml: this.options.grid_view_xml,
                modes: this.modes,
                show_top: true,
                show_head: true,
                action_name: this.options.name, // XXX
                context: this.context
            };
            if (_.contains(this.modes,"page")) { // XXX
                opts.next_action=this.options.name;
                opts.next_action_options="mode=page";
            };
            var view=new GridView({options:opts});
            view.render();
            this.$el.append(view.el);
            this.subviews[view.cid]=view;
        } else if (this.mode=="columns") {
            var opts={
                model: this.options.model,
                condition: this.options.condition,
                order: this.options.order,
                string: this.options.string,
                view_xml: this.options.columns_view_xml,
                context: this.context
            };
            var view=new ColumnsView({options:opts});
            view.render();
            this.$el.append(view.el);
            this.subviews[view.cid]=view;
        } else if (this.mode=="map") {
            var opts={
                model: this.options.model,
                condition: this.options.condition,
                order: this.options.order,
                string: this.options.string,
                view_xml: this.options.map_view_xml,
                context: this.context
            };
            var view=new MapView({options:opts});
            view.render();
            this.$el.append(view.el);
            this.subviews[view.cid]=view;
        } else {
            throw "Invalid mode "+this.mode;
        }
        view.on("click_item",function(opts) {
            var action={
                name: that.options.name,
                active_id: opts.active_id
            };
            if (_.contains(this.modes,"page")) {
                action.mode="page";
            } else if (_.contains(this.modes,"form")) {
                action.mode="form";
            } else {
                log("can't view item details because no page or form view");
                return;
            }
            exec_action(action);
        });
        view.on("change_mode",function(opts) {
            var action={
                name: that.options.name
            };
            if (opts.mode) {
                action.mode=opts.mode;
            }
            if (opts.active_id) {
                action.active_id=opts.active_id;
            }
            if (that.options.search_condition) {
                action.search_condition=that.options.search_condition;
            }
            if (that.options.tab_no) {
                action.tab_no=that.options.tab_no;
            }
            if (that.options.offset) {
                action.offset=that.options.offset;
            }
            exec_action(action);
        });
        return this;
    }
});

MultiView.register();
