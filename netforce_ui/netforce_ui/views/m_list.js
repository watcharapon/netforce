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

var MList=NFView.extend({
    _name: "m_list",
    events: {
        "click .add-line": "add_line"
    },

    initialize: function(options) {
        log("MList.initialize",this);
        NFView.prototype.initialize.call(this,options);
        var collection=this.context.collection;
        if (collection) {
            collection.on("add remove",this.render,this);
        }
    },

    render: function() {
        log("MList.render",this);
        var that=this;
        var content="";
        if (this.context.collection) {
            this.context.collection.each(function (model) {
                var ctx=_.clone(that.context);
                ctx.model=model;
                var data={
                    context: ctx
                };
                content+=that.options.inner(data);
            });
        } else if (this.context.model) {
            var ctx=_.clone(that.context);
            ctx.model=this.context.model;
            var data={
                context: ctx
            };
            content+=that.options.inner(data);
        }
        this.data.action=this.options.action;
        this.data.content=content;
        NFView.prototype.render.call(this);
    },

    add_line: function(e) {
        log("MList.add_line");
        e.preventDefault();
        e.stopPropagation();
        var action={
            name: this.options.action,
            target: "_popup",
            context: {
                collection: this.context.collection
            }
        };
        exec_action(action);
    }
});

MList.register();
