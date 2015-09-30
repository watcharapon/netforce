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

var CollectionView=NFView.extend({
    _name: "collection_view",

    initialize: function(options) {
        NFView.prototype.initialize.call(this,options);
        this.base_condition=this.options.condition;
        if (_.isString(this.base_condition)) {
            var ctx=_.clone(this.options);
            this.base_condition=eval_json(this.base_condition,ctx);
        }
        this.search_condition=this.options.search_condition;
        if (_.isString(this.search_condition)) {
            var ctx=_.clone(this.options);
            this.search_condition=eval_json(this.search_condition,ctx);
        }
        this.order=this.options.order;
        this.collection=new NFCollection([],{name:this.options.model});
        this.collection.on("reload",this.reload,this);
    },

    render: function() {
        log("CollectionView render",this,this.options);
        if (this.options.inner) {
            this.template=this.options.inner;
        } else {
            if (_.isString(this.options.template)) {
                this.template=get_template(this.options.template);
            } else {
                this.template=this.options.template;
            }
        }
        if (!this.template) throw "Missing template in CollectionView";
        var fields=this.options.field_names;
        this.data.context._action_view=this;
        this.data.context.model=null;
        this.data.context.collection=null;
        var that=this;
        //this.data.context.model=null; // XXX
        this.data.context.collection=this.collection;
        if (this.options.data) {
            this.data.context.data=this.options.data;
            this.collection.reset(this.options.data,{name:this.collection.name});
            NFView.prototype.render.call(this);
        } else if (this.options.method) {
            var method=this.options.method;
            var ctx=_.extend({},this.context,this.options);
            ctx=clean_context(ctx);
            this.render_waiting();
            rpc_execute(this.options.model,method,[],{context:ctx},function(err,data) {
                if (err) {
                    that.render_error(err);
                    return;
                }
                that.data.context.data=data;
                that.collection.reset(data);
                NFView.prototype.render.call(that);
            });
        } else {
            var condition=this.base_condition||[];
            if (this.search_condition) {
                if (condition.length>0) {
                    condition=[condition,this.search_condition];
                } else {
                    condition=this.search_condition;
                }
            }
            var offset=this.options.offset||0;
            this.data.context.offset=offset;
            var limit=this.options.limit||100;
            this.data.context.limit=limit;
            var args={
                field_names: fields,
                offset: offset,
                limit: limit,
                count: true
            };
            if (this.order) {
                args.order=this.order;
            }
            this.render_waiting();
            rpc_execute(this.options.model,"search_read",[condition],args,function(err,data) { // XXX: use collection get_data
                if (err) {
                    that.render_error(err);
                    return;
                }
                that.data.context.data=data[0];
                that.collection.reset(data[0],{silent:true,name:that.collection.name}); // XXX: don't trigger re-render
                that.collection.each(function(m) {
                    m.set_orig_data(m.attributes); // XXX
                });
                that.collection.count=data[1];
                that.collection.condition=that.base_condition;
                that.collection.order=that.order;
                that.collection.limit=limit;
                var orig_ids=_.pluck(data[0],"id");
                that.collection.orig_ids=orig_ids;
                NFView.prototype.render.call(that);
            });
        }
        return this;
    },

    render_waiting: function() {
        var img=$("<img/>").attr("src","/static/img/spinner.gif");
        this.$el.empty();
        this.$el.append(img);
    },

    render_error: function(err) {
        var div=$("<div/>").addClass("alert alert-error").css({"margin":"10px 0"}).text(err.message);
        this.$el.empty();
        this.$el.append(div);
    },

    reload: function() { // XXX
        this.render();
    }
});

CollectionView.register();
