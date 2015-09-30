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
        this.num_cols=parseInt(this.options.num_cols)||1;
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
    }
});

GridView.register();
