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

var Feedback=NFView.extend({
    _name: "feedback",
    className: "feedback",
    events: {
        "click .fb-button": "click_fb",
        "click .feedback-send": "click_send",
        "click .feedback-no": "click_no"
    },

    click_fb: function(e) {
        log("click_fb");
        e.preventDefault();
        this.$el.find("textarea").val("");
        this.$el.find(".send-feedback").show();
    },

    click_send: function(e) {
        log("click_send");
        e.preventDefault();
        var msg=this.$el.find("textarea").val();
        var vals={
            "message": msg
        }
        this.$el.find(".send-feedback").hide();
        rpc_execute("feedback","create",[],{"vals":vals},function(err,data) {
            if (err) {
                alert("Failed to send feedback");
                return;
            }
            alert("Thanks for your feedback!");
        });
    },

    click_no: function(e) {
        log("click_no");
        e.preventDefault();
        this.$el.find(".send-feedback").hide();
    }
});

Feedback.register();
