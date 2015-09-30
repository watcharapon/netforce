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

var TreeView=NFView.extend({
    _name: "tree_view",
    events: {
        "click .search-btn": "click_search"
    },

    initialize: function(options) {
        //log("tree_view.initialize",this);
        var that=this;
        NFView.prototype.initialize.call(this,options);
        if (this.options.tree_layout) {
            var layout=this.options.tree_layout;
        } else {
            if (this.options.view_xml) {
                var tree_view=get_xml_layout({name:this.options.view_xml});
            } else {
                var tree_view=get_xml_layout({model:this.options.model,type:"tree"});
            }
            var layout=tree_view.layout;
        }
        if (_.isString(layout)) {
            var doc=$.parseXML(layout);
            this.$tree=$(doc).children();
        } else {
            this.$tree=layout;
        }
        this.item_views={};
    },

    render: function() {
        //log("tree_view.render",this);
        var that=this;
        var model_name=this.options.model;
        var field_names=[];
        var cols=[];
        var model_cls=get_model(model_name);
        this.$tree.children().each(function() {
            var $el=$(this);
            var tag=$el.prop("tagName");
            if (tag=="field") {
                var name=$el.attr("name");
                field_names.push(name);
                var f=model_cls.fields[name];
                if (!f) throw "No such field: "+name;
                cols.push({
                    col_type: "field",
                    name: name,
                    nowrap: $el.attr("nowrap"),
                    string: f.string
                });
            } else if (tag=="button") {
                cols.push({
                    col_type: "button",
                    button_string: $el.attr("string")
                });
            }
        });
        this.data.cols=cols;
        this.data.tree_view=this;
        var child_field=this.$tree.attr("child_field");
        if (!child_field) throw "Missing child_field in tree";
        field_names.push(child_field);
        this.field_names=field_names;
        var condition=this.options.condition||[];
        if (_.isString(condition)) {
            condition=JSON.parse(condition);
        }
        if (this.search_condition) {
            condition=this.search_condition; // XXX
        }
        var order=this.options.order;
        var limit=this.options.limit||80;
        var opts={
            order: order,
            limit: limit
        };
        rpc_execute(model_name,"search_read",[condition,field_names],opts,function(err,data) {
            data=that.remove_non_roots(data);
            that.collection=new NFCollection(data,{name:model_name});
            that.data.context.data=data;
            that.data.context.collection=that.collection;
            that.data.context.model=null; // XXX
            that.data.count=that.collection.length;
            that.collection.each(function(model) {
                model.set("_depth",0);
            });
            NFView.prototype.render.call(that);
            if (!_.isEmpty(that.search_condition)) {
                that.show_search();
            }
        });
        return this;
    },

    item_click: function(item_view) {
        log("tree_view.item_click",this,item_view);
        var that=this;
        var model_name=this.options.model;
        var model=item_view.context.model;
        var child_field=this.$tree.attr("child_field");
        var child_ids=model.get(child_field);
        if (_.isEmpty(child_ids)) {
            var action_name=this.$tree.attr("action");
            if (action_name) {
                var action={
                    name: action_name,
                    active_id: model.id
                };
                exec_action(action);
            }
        } else {
            if (!item_view.expanded) {
                log("expand");
                var cond=[["id","in",child_ids]];
                var opts={
                    field_names: this.field_names
                };
                rpc_execute(model_name,"search_read",[cond],opts,function(err,data) {
                    var pos=that.collection.indexOf(model)+1;
                    log("pos",pos);
                    var $prev_el=item_view.$el;
                    _.each(data,function(vals) {
                        var new_model=new NFModel(vals,{name:model_name});
                        new_model.set("_depth",model.get("_depth")+1);
                        that.collection.add(new_model,{at:pos});
                        pos+=1;
                        var ctx=_.clone(that.context);
                        ctx.model=new_model;
                        ctx.data=vals;
                        var opts={
                            tree_view: that,
                            context: ctx
                        };
                        var view=new TreeItem({options:opts});
                        that.item_views[new_model.id]=view;
                        view.render();
                        $prev_el.after(view.el);
                        $prev_el=view.$el;
                    });
                    item_view.expanded=true;
                    item_view.render();
                });
            } else {
                log("collapse");
                this.remove_childs(model.id);
                item_view.expanded=false;
                item_view.render();
            }
        }
    },

    remove_childs: function(id) {
        log("remove_childs",id);
        var that=this;
        var model=this.collection.get(id);
        var child_field=this.$tree.attr("child_field");
        var child_ids=model.get(child_field);
        _.each(child_ids,function(id) {
            var child=that.collection.get(id);
            if (!child) return;
            that.remove_childs(id);
            that.collection.remove(id);
            var view=that.item_views[id];
            remove_view_instance(view.cid);
        });
    },

    click_search: function(e) {
        e.preventDefault();
        e.stopPropagation();
        this.show_search();
    },

    show_search: function(e) {
        log("tree_view.show_search");
        var that=this;
        var opts={
            model: this.options.model
        };
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
        });
    },

    remove_non_roots: function(data) {
        var child_field=this.$tree.attr("child_field");
        var non_roots={};
        _.each(data,function(obj) {
            _.each(obj[child_field],function(id) {
                non_roots[id]=true;
            });
        });
        return _.filter(data,function(obj) {
            return !non_roots[obj.id];
        });
    }
});

TreeView.register();
