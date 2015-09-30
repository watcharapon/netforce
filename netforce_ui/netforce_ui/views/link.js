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

var Link=NFView.extend({
    _name: "link",
    tagName: "a",
    events: {
        "click": "click"
    },

    render: function() {
        //log("link.render",this);
        //
        if (this.options.action) {
            var action={name:this.options.action};
            if (this.options.action_options) { // XXX
                _.extend(action,qs_to_obj(this.options.action_options));
            }
            if (this.options.active_id) { // XXX
                action.active_id=this.options.active_id;
            }
            var qs=obj_to_qs(action);
            this.$el.attr("href","#"+qs);
        } else {
            this.$el.attr("href","#");
        }
        if (this.options.string) {
            this.data.content=this.options.string;
        } else if (this.options.inner) {
            var data={
                context: this.context
            };
            this.data.content=this.options.inner(data);
        } else {
            this.data.content="";
        }
        NFView.prototype.render.call(this);
    },

    click: function(e) {
        e.preventDefault();
        e.stopPropagation();
        if (this.options.confirm) {
            var res=confirm(this.options.confirm);
            if (!res) return;
        }
        var that=this;
        if (this.options.action) {
            var action={name:this.options.action};
            if (this.options.action_options) { // XXX
                _.extend(action,qs_to_obj(this.options.action_options));
            }
            if (this.options.active_id) { // XXX
                action.active_id=this.options.active_id;
            }
            exec_action(action);
        } else if (this.options.method) {
            var method=this.options.method;
            var model=this.context.model;
            if (method=="_delete") {
                var ctx=qs_to_obj(this.options.method_context);
                var field=ctx.field;
                rpc_execute("delete",[[model.id]],{},function(err,data) {
                    if (err) {
                        set_flash("error",err.message);
                        render_flash();
                        return;
                    }
                    log("delete success");
                    var next=that.options.next;
                    if (next=="_reload") {
                        window.location.reload(); // XXX
                    }
                });
            }
        }
    }
});

Link.register();
