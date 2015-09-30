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

var InlineHelp=NFView.extend({
    _name: "inline_help",
    events: {
        "click a.close": "click_close",
        "click a.hide-help": "click_hide",
        "click a.show-help": "click_show"
    },

    render: function() {
        var that=this;
        var action=this.options.action;
        if (!action) return;
        setTimeout(function() { // XXX
            rpc_execute("inline.help","search_read",[["action","=",action]],{},function(err,res) {
                if (res.length==0) {
                    log("inline help not found",action);
                    return;
                }
                that.data.hide=res[0].hide;
                that.data.title=res[0].title;
                that.help_id=res[0].id;
                NFView.prototype.render.call(that);
                var iframe=that.$el.find("iframe")[0];
                $(iframe).load(function() {
                    var w=iframe.contentWindow.document.body.scrollWidth;
                    var h=iframe.contentWindow.document.body.scrollHeight;
                    log("resize iframe",w,h);
                    iframe.width=w+"px";
                    iframe.height=h+"px";
                });
            });
        },1000);
    },

    click_close: function(e) {
        e.preventDefault();
        this.$el.hide();
    },

    click_hide: function(e) {
        var that=this;
        e.preventDefault();
        rpc_execute("inline.help","write",[[this.help_id],{"hide":true}],{},function(err,res) {
            that.render();
        });
    },

    click_show: function(e) {
        var that=this;
        e.preventDefault();
        rpc_execute("inline.help","write",[[this.help_id],{"hide":false}],{},function(err,res) {
            that.render();
        });
    }
});

InlineHelp.register();
