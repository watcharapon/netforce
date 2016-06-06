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

var FormList=NFView.extend({
    _name: "form_list",
    events: {
        "click .btn-add": "add_item"
    },

    initialize: function(options) {
        //log("form_list.initialize",this);
        NFView.prototype.initialize.call(this,options);
        if (this.options.layout) {
            var layout=this.options.layout;
        } else {
            var model=this.context.model;
            var name=this.options.name;
            var field=model.get_field(name);
            var relation=field.relation;
            var form_view=get_xml_layout({model:relation,type:"form"});
            var layout=form_view.layout;
        }
        if (_.isString(layout)) {
            var doc=$.parseXML(layout);
            this.$form=$(doc).children();
        } else {
            this.$form=layout;
        }
        this.data.layout=this.$form;
    },

    render: function() {
        //log("form_list.render",this);
        var that=this;
        var got_collection=function() {
            that.data.context.collection=that.collection;
            that.data.context.model=null; // XXX
            that.data.context.readonly=that.options.readonly;
            NFView.prototype.render.call(that);
        }
        if (!this.collection) {
            //log("make collection");
            var model=this.context.model;
            var name=this.options.name;
            var field=model.get_field(name);
            var relation=field.relation;
            var ids=model.get(name)||[]; // XXX
            var field_names=[];
            this.$form.find("field").each(function() {
                field_names.push($(this).attr("name"));
            });
            if (ids.length>0) {
                rpc_execute(relation,"read",[ids,field_names],{},function(err,data) {
                    that.collection=new NFCollection(data,{name:relation});
                    that.collection.orig_ids=_.pluck(data,"id");
                    //log("orig_ids",that.collection.orig_ids);
                    that.collection.on("add",that.render,that);
                    that.collection.on("remove",that.render,that);
                    model.set(name,that.collection);
                    got_collection();
                });
            } else {
                rpc_execute(relation,"default_get",[field_names],{},function(err,data) {
                    that.collection=new NFCollection([data],{name:relation});
                    that.collection.orig_ids=[];
                    that.collection.on("add",that.render,that);
                    that.collection.on("remove",that.render,that);
                    model.set(name,that.collection);
                    got_collection();
                });
            }
        } else {
            got_collection();
        }
        return this;
    },

    add_item: function(e) {
        log("add_item",this);
        e.preventDefault();
        e.stopPropagation();
        this.collection.add({},{name:this.collection.name});
    }
});

FormList.register();
