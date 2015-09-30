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

var ContextMenu=NFView.extend({
    _name: "context_menu",
    events: {
        "click a": "click_item"
    },

    render: function() {
        var that=this;
        NFView.prototype.render.call(this);
        this.$el.find(".dropdown-menu").show();
        this.$el.find(".dropdown-menu").css({
            position: "absolute",
            left: this.getLeftLocation(),
            top: this.getTopLocation()
        });
        $(document).click(function() {
            that.$el.find(".dropdown-menu").hide();
        });
    },

    getLeftLocation: function() {
        var mouseWidth = this.options.click_x;
        var pageWidth = $(window).width();
        var menuWidth = this.$el.width();
        
        // opening menu would pass the side of the page
        if (mouseWidth + menuWidth > pageWidth &&
            menuWidth < mouseWidth) {
            return mouseWidth - menuWidth;
        } 
        return mouseWidth;
    },       

    getTopLocation: function() {
        var mouseHeight = this.options.click_y;
        var pageHeight = $(window).height();
        var menuHeight = this.$el.height();

        // opening menu would pass the bottom of the page
        if (mouseHeight + menuHeight > pageHeight &&
            menuHeight < mouseHeight) {
            return mouseHeight - menuHeight;
        } 
        return mouseHeight;
    },

    click_item: function(e) {
        e.preventDefault();
        var $el=$(e.target).parents("li");
        var i=$el.index();
        var item=this.options.items[i];
        var cb=item.callback;
        if (cb) {
            cb();
        }
    }
});

ContextMenu.register();
