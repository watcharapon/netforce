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

var ModelView=NFView.extend({
    _name: "model_view",

    initialize: function(options) {
        NFView.prototype.initialize.call(this,options);
    },

    render: function() {
        log("ModelView render",this);
        if (this.options.inner) {
            this.template=this.options.inner;
        } else {
            if (_.isString(this.options.template)) {
                this.template=get_template(this.options.template);
            } else {
                this.template=this.options.template;
            }
        }
        if (!this.template) throw "Missing template in ModelView";
        var fields=this.options.field_names;
        if (_.isString(fields)) {
            fields=JSON.parse(fields);
        }
        this.data.context._action_view=this;
        this.data.context.model=null;
        this.data.context.collection=null;
        var that=this;
        //this.data.context.collection=null; // XXX
        var model_cls=get_model_cls(this.options.model);
        if (this.options.method) {
            var method=this.options.method;
            var ctx=_.extend({},this.context,this.options);
            ctx=clean_context(ctx);
            this.render_waiting();
            rpc_execute(this.options.model,method,[],{context:ctx},function(err,data) {
                if (err) {
                    that.render_error(err);
                    return;
                }
                if(data.next && data.next.type=='url'){
                    window.location.href=data.next.url;
                    return;
                }
                that.data.context.data=data;
                that.data.context.model=new NFModel(data,{name:that.options.model});
                that.data.context.model.on("reload",that.reload,that);
                NFView.prototype.render.call(that);
            });
        } else {
            var active_id=this.options.active_id;
            if (active_id) {
                if (_.isString(active_id)) {
                    active_id=parseInt(active_id);
                }
                this.render_waiting();
                rpc_execute(this.options.model,"read",[[active_id]],{field_names:fields},function(err,data) {
                    if (err) {
                        that.render_error(err);
                        return;
                    }
                    that.data.context.data=data[0];
                    that.data.context.model=new NFModel(data[0],{name:that.options.model});
                    that.data.context.model.set_orig_data(data[0]);
                    that.data.context.model.on("reload",that.reload,that);
                    NFView.prototype.render.call(that);
                });
            } else {
                var ctx=_.clone(this.context);
                _.extend(ctx,this.options);
                ctx=clean_context(ctx);
                if (_.isString(ctx.defaults)) {
                    var ctx2=_.clone(this.options);
                    ctx.defaults=eval_json(ctx.defaults,ctx2);
                }
                this.render_waiting();
                rpc_execute(this.options.model,"default_get",[],{field_names: fields, context: ctx},function(err,data) {
                    if (err) {
                        that.render_error(err);
                        return;
                    }
                    if(data.next && data.next.type=='url'){
                        window.location.href=data.next.url;
                        return;
                    }
                    that.data.context.data=data;
                    that.data.context.model=new NFModel(data,{name:that.options.model});
                    that.data.context.model.on("reload",that.reload,that);
                    NFView.prototype.render.call(that);
                });
            }
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
        this.options.active_id=this.data.context.model.id;
        this.render();
    }
});

ModelView.register();
