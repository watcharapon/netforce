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

var Window=NFView.extend({
    _name: "window",

    initialize: function(options) {
        NFView.prototype.initialize.call(this,options);
        this.model=this.options.model;
        this.mode=this.options.mode||"list";
        this.title=this.options.title;
        if (this.options.active_id) {
            this.active_id=parseInt(this.options.active_id);
        }
        var h=window.location.hash;
        var action=qs_to_obj(h.substr(1));
        this.action_name=action.name; // XXX
    },

    render: function() {
        log("window render",this);
        this.data.mode=this.mode;
        this.data.window=this;
        NFView.prototype.render.call(this);
    }
});

Window.register();
