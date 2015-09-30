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

var MsgBar=NFView.extend({
    _name: "msg_bar",
    tagName: "span",

    initialize: function(options) {
        var that=this;
        NFView.prototype.initialize.call(this,options);
        var ctx=get_global_context();
        var user_id=ctx.user_id;
        nf_unlisten("new_message");
        nf_listen("new_message",function() {
            that.render();
            nf_play_sound("/static/sound/new_message.mp3");
        });
    },

    render: function() {
        var that=this;
        this.data.num_messages=null;
        NFView.prototype.render.call(this);
        var ctx=get_global_context();
        var user_id=ctx.user_id;
        var condition=[["to_id","=",user_id],["state","=","new"]];
        var field_names=["date","from_id","subject","body"];
        setTimeout(function() { // XXX
            rpc_execute("message","search_read",[condition],{field_names:field_names},function(err,data) {
                that.data.num_messages=data.length;
                NFView.prototype.render.call(that);
                if (data.length>0) {
                    var vals=data[data.length-1];
                    var opts={
                        placement: "bottom",
                        title: vals.subject,
                        html: true,
                        content: '<p><i>From '+vals.from_id[1]+', 1 minute ago</i></p><p>'+vals.body+'</p><a class="btn btn-success msg-btn-ok">OK</a>'
                    };
                    that.$el.find("a").popover(opts);
                    that.$el.find("a").popover("show");
                    $(".msg-btn-ok").on("click",function() {
                        var id=vals.id;
                        rpc_execute("message","write",[[id],{state:"opened"}],{},function(err,data) {
                            that.render();
                        });
                    });
                }
            });
        },2000);
        return this;
    }
});

MsgBar.register();
