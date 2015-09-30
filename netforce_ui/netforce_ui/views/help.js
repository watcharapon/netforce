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

var Help=NFView.extend({
    _name: "help",
    tagName: "span",
    events: {
        "click i": "onclick"
    },

    render: function() {
        var action=this.options.action;
        this.data.avail=ui_params_db.inline_help && ui_params_db.inline_help[action];
        NFView.prototype.render.call(this);
    },

    onclick: function(e) {
        var that=this;
        e.preventDefault();
        e.stopPropagation();
        var action=this.options.action;
        var condition=[["action","=",action]];
        rpc_execute("inline.help","search_read",[condition],{},function(err,data) {
            if (data.length>0) {
                var vals=data[0];
                var title=vals.title;
                var content=vals.content;
            } else {
                var title="Help not found";
                var content='<p>Help is not yet available for this item.</p><a href="/action#name=inline_help&mode=form&defaults.action='+action+'" class="btn btn-small"><i class="icon-arrow-right"></i> Add help</a>';
            }
            var opts={
                placement: "bottom",
                title: '<button type="button" id="close" class="close" style="margin-left:10px">&times;</button><b>'+title+'</b>',
                html: true,
                content: content
            };
            that.$el.find("i").popover(opts);
            that.$el.find("i").popover("show");
            that.$el.find(".popover").addClass("nf-help-popover");
            that.$el.find(".popover .close").on("click",function() {
                that.$el.find("i").popover("hide");
            });
        });
    }
});

Help.register();
