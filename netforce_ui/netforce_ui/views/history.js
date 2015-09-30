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

var History=NFView.extend({
    _name: "history",
    events: {
        "click .hist-toggle": "toggle",
        "click .hist-add": "add_note",
        "click .note-save": "save_note",
        "click .note-cancel": "cancel_note",
        "click .del-note": "delete_note"
    },

    render: function() {
        NFView.prototype.render.call(this);
        this.$el.css({marginTop:"18px"});
        return this;
    },

    toggle: function(e) {
        e.preventDefault();
        e.stopPropagation();
        this.$el.find(".hist-table").toggle();
    },

    add_note: function(e) {
        this.$el.find(".add-btn").hide();
        e.preventDefault();
        e.stopPropagation();
        var action={
            view_type: "model",
            model: "message",
            template: "add_note",
            target: "add-note"
        }
        this.add_note_view=exec_action(action);
    },

    save_note: function(e) {
        e.preventDefault();
        e.stopPropagation();
        var model=this.add_note_view.data.context.model;
        var vals={
            "subject": "Note",
            "body": model.get("body"),
            "attach": model.get("attach"),
            "ref_uuid": this.options.uuid
        }
        var m=get_model_cls("message");
        var that=this;
        m.create(vals,function(err,data) {
            if (err) throw "ERROR: "+err;
            that.render();
        });
    },

    cancel_note: function(e) {
        e.preventDefault();
        e.stopPropagation();
        this.$el.find("#add-note").empty();
        this.$el.find(".add-btn").show();
    },

    delete_note: function(e) {
        e.preventDefault();
        e.stopPropagation();
        var res=confirm("Are you sure you want to delete this message?");
        if (!res) return;
        var $el=$(e.target).parents("tr").first();
        log("el",$el);
        var id=$el.data("id");
        log("id",id);
        var that=this;
        rpc_execute("message","delete",[[id]],{},function(err,data) {
            if (err) throw "ERROR: "+err;
            that.render();
        });
    }
});

History.register();
