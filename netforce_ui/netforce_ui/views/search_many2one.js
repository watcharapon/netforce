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

var SearchMany2One=NFView.extend({
    _name: "search_many2one",
    className: "modal nf-modal",

    events: {
        'click .close-modal': 'close_modal',
        'click .select-item-btn': 'select_item'
    },

    close_modal: function(e) {
        e.preventDefault();
        remove_view_instance(this.cid);
        var view_cid="."+this.cid;
        // remove backdrop
        $(view_cid).remove();
    },

    select_item: function(e){
        e.preventDefault();
        var model=this.collection.findWhere({'_selected': true});
        this.trigger("close_search",model);
    },

    initialize: function(options) {
        var that=this;
        NFView.prototype.initialize.call(this,options);
        if (!this.options.model) throw "SearchListView: missing model";
        var list_view=get_xml_layout({model:this.options.model,type:"list"});
        var layout=list_view.layout;
        if (_.isString(layout)) {
            var doc=$.parseXML(layout);
            this.$list=$(doc).children();
        } else {
            this.$list=layout;
        }
        this.data.render_list_head=function(ctx) { return that.render_list_head.call(that,ctx); };
        this.data.render_list_footer=function(ctx) { return that.render_list_footer.call(that,ctx); };
    },

    render_list_head: function(context) {
        var that=this;
        var html=$("<div/>");
        html.append('<button type="button" class="btn btn-sm btn-default select-item-btn" style="white-space:nowrap;"> '+ translate("Select")+"</button>");
        return html.html();
    },

    render_list_footer: function(context) {
        var that=this;
        var html=$("<div/>");
        html.append('<button type="button" class="btn btn-default select-item-btn" style="white-space:nowrap;"> '+ translate("Select")+"</button>");
        return html.html();
    },
    line_click: function(model) {
        log("search_list_view.line_click",this,model);
        this.trigger("close_search",model);
    },

    render: function() {
        //log("list_view.render",this);
        var that=this;
        var model_name=this.options.model;
        var model=get_model_cls(model_name);

        var condition=this.options.condition||[];
        var search_condition=this.search_condition||[];
        if (_.isString(search_condition)) {
            search_condition=JSON.parse(search_condition);
        }
        if (search_condition.length>0) {
            if (condition.length>0) {
                condition=[condition,search_condition];
            } else {
                condition=search_condition;
            }
        }
        var field_names=[];
        var cols=[];
        this.$list.children().each(function() {
            var tag=$(this).prop("tagName");
            if (tag=="field") {
                var name=$(this).attr("name");
                var field=get_field(that.options.model,name);
                field_names.push(name);
                if (!$(this).attr("invisible")) {
                    var col={
                        col_type: "field",
                        name: name,
                        link: $(this).attr("link"),
                        target: $(this).attr("target"),
                        preview: $(this).attr("preview"),
                        view: $(this).attr("view")
                    };
                    if (field.type=="float") {
                        col.align="right";
                    }
                    if (field.store) {
                        col.can_sort=true;
                    }
                    var f=model.fields[name];
                    col.string=f.string;
                    cols.push(col);
                }
            }
        });
        this.data.cols=cols;
        var opts={
            field_names: field_names,
            order: this.options.order,
            offset: this.options.offset,
            limit: this.options.limit||100,
            count: true
        }
        if (_.isString(condition)) {
            var ctx=clean_context(_.extend({},this.context,this.options));
            condition=eval_json(condition,ctx);
        }
        var that=this;
        that.data.popup_title=model.string;
        rpc_execute(model_name,"search_read",[condition],opts,function(err,data) {
            that.collection=new NFCollection(data[0],{name:model_name});
            that.collection.fields=field_names;
            that.collection.condition=condition;
            that.collection.order=that.options.order;
            that.collection.search_condition=condition; // XXX: check this
            // force show pagination
            that.collection.count=data[1];
            that.collection.offset=parseInt(that.options.offset);
            that.collection.limit=that.options.limit||100;

            that.collection.on("click",that.line_click,that);
            /*that.collection.on("reload",that.reload,that);*/
            that.data.context.data=data;
            that.data.context.collection=that.collection;
            that.data.context.model_name=model_name;

            that.data.context.one_select=true; //XXX
            that.data.context.search_list_view=that; //XXX

            // clear the old one
            that.on("one_select_model", function(model){
                if(model){ 
                    that.collection.each(function(model2){
                        if (model.get('id') != model2.get('id')){
                            model2.set("_selected",false);
                        }
                    });
                }
            });

            NFView.prototype.render.call(that);
            that.$el.find(".modal-dialog").width(that.options.width || '70%');
            that.show_search();
        });
        return this;
    },

    show_search: function(e) {
        log("list_view.show_search");
        var that=this;
        var opts={
            hide_close: true,
            model: this.options.model
        };
        if (this.options.search_view_xml) {
            opts.view_xml=this.options.search_view_xml;
        } else if (this.options.search_layout) {
            opts.view_layout=this.options.search_layout;
        }
        var $el=this.$list.find("search");
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

        view.on("search",function() {
            that.search_condition=view.get_condition();
            that.collection.offset=0;
            that.render();
        });

    },

    reload: function() {
        this.render();
    },

    render_waiting: function() {
        var img=$("<img/>").attr("src","/static/img/spinner.gif");
        this.$el.empty();
        this.$el.append(img);
    },

    click_tab: function(e) {
        log("list_view.click_tab",this,e);
        e.preventDefault();
    },

    show_active_tab: function() {
        var tab_no=this.tab_no||0;
        this.$el.find("li[data-tab="+tab_no+"]").addClass("active");
    },

});

SearchMany2One.register();
