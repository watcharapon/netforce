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

var PageEdit=NFView.extend({
    _name: "page_edit",
    events: {
        "click .edit": "click_edit",
        "click .cancel": "click_cancel"
    },

    render: function() {
        this.data.mode=this.mode;
        NFView.prototype.render.call(this);
        return this;
    },

    click_edit: function(e) {
        log("page_edit.click_edit");
        var that=this;
        e.preventDefault();
        e.stopPropagation();
        this.mode="edit";
        this.render();
        this.editors=[];
        $(".inline-edit").each(function() {
            var el=this;
            $(el).attr("contenteditable","true");
            if ($(el).data("editor")) {
                var editor=CKEDITOR.inline(el,{
                    filebrowserUploadUrl:  '/ck_upload'
                });
                that.editors.push(editor);
                editor.on("blur",function() {
                    log("editor blur",el);
                    var model=$(el).data("model");
                    var id=$(el).data("id");
                    var field=$(el).data("field");
                    var val=editor.getData();
                    log("val",val);
                    if (id) {
                        var vals={};
                        vals[field]=val;
                        rpc_execute(model,"write",[[id],vals]);
                    } else {
                        var vals=$(el).data("defaults")||{};
                        vals[field]=val;
                        $(el).data("id",-1);
                        rpc_execute(model,"create",[vals],{},function(err,data) {
                            var new_id=data;
                            log("new_id",new_id);
                            $(el).data("id",new_id);
                        });
                    }
                });
            } else {
                $(el).on("blur",function() {
                    log("contenteditable blur",el);
                    var model=$(el).data("model");
                    var id=$(el).data("id");
                    var field=$(el).data("field");
                    var val=$.trim($(el).text());
                    log("val",val);
                    if (id) {
                        var vals={};
                        vals[field]=val;
                        rpc_execute(model,"write",[[id],vals]);
                    } else {
                        var vals=$(el).data("defaults")||{};
                        vals[field]=val;
                        $(el).data("id",-1);
                        rpc_execute(model,"create",[vals],{},function(err,data) {
                            var new_id=data;
                            log("new_id",new_id);
                            $(el).data("id",new_id);
                        });
                    }
                });
            }
        });
    },

    click_cancel: function(e) {
        log("page_edit.click_cancel");
        e.preventDefault();
        e.stopPropagation();
        this.mode="cancel";
        this.render();
        $(".inline-edit").each(function() {
            $(this).removeAttr("contenteditable");
        });
        _.each(this.editors,function(editor) {
            editor.destroy();
        });
    }
});

PageEdit.register();

$(function() {
    if ($(".inline-edit").length>0) {
        load_permissions(function() {
            if (check_other_permission("page_edit")) {
                if (!has_perm) return;
                var res=$(".inline-edit");
                if (res.length>0) {
                    var view=new PageEdit();
                    view.render();
                    $("body").append(view.el);
                    $("body").css("padding-top",40);
                }
            }
        });
    }
});
