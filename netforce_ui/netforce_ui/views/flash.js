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

var flash=null;
var flash_view;

var Flash=NFView.extend({
    _name: "flash",

    initialize: function(options) {
        flash_view=this;
        NFView.prototype.initialize.call(this,options);
    },

    render: function() {
        this.data.flash=window.flash;
        NFView.prototype.render.call(this);
        clear_flash();
    }
});

Flash.register();

set_flash=function(type,message) { // XXX: deprecated, remove later
    //alert("set_flash "+message);
    log("set_flash",type,message);
    if (_.isString(type)) {
        window.flash={
            type: type,
            message: message
        };
    } else if (_.isObject(type)) {
        window.flash=type;
    }
}

clear_flash=function() {
    //alert("clear_flash");
    //log("clear_flash");
    window.flash=null;
}

render_flash=function() {
    flash_view.render();
}
