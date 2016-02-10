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

var ColumnsView=NFView.extend({
    _name: "columns_view",
    events: {
        "dragstart .nf-columns-record": "drag_start_record",
        "dragover .nf-columns-group-body": "drag_over_group_body",
        "drop .nf-columns-group-body": "drop_group_body",
    },

    initialize: function(options) {
        //log("columns_view.initialize",this);
        var that=this;
        NFView.prototype.initialize.call(this,options);
        if (this.options.grid_layout) {
            var layout=this.options.grid_layout;
        } else {
            if (this.options.view_xml) {
                var view=get_xml_layout({name:this.options.view_xml});
            } else {
                var view=get_xml_layout({model:this.options.model,type:"columns"});
            }
            var layout=view.layout;
        }
        if (_.isString(layout)) {
            var doc=$.parseXML(layout);
            this.$layout=$(doc).children();
        } else {
            this.$layout=layout;
        }
    },

    render: function() {
        //log("columns_view.render",this);
        var that=this;
        this.data.page_title=this.$layout.attr("title")||this.options.string;
        var condition=this.options.condition||[];
        var group_field=this.$layout.attr("group_field");
        if (!group_field) throw("Missing group_field in columns view");
        var title_field=this.$layout.attr("title_field");
        if (!title_field) throw("Missing title field in columns view");
        var field_names=[group_field,title_field];
        var content_fields=[];
        this.$layout.find("field").each(function() {
            var name=$(this).attr("name");
            field_names.push(name);
            content_fields.push(name);
        });
        var opts={
            field_names: field_names,
            count: true
        };
        rpc_execute(this.options.model,"search_read",[condition],opts,function(err,data) {
            that.collection=new NFCollection(data[0],{name:that.options.model});
            var groups={};
            that.collection.each(function(m) {
                var val=m.get(group_field);
                var f=get_field(that.options.model,group_field);
                var group_val=render_field_value(val,f);
                log("group_val",group_val);
                if (!groups[group_val]) {
                    groups[group_val]={
                        title: group_val,
                        records: []
                    };
                }
                var group=groups[group_val];
                var val=m.get(title_field);
                var f=get_field(that.options.model,group_field);
                var title_val=render_field_value(val,f);
                var fields=[];
                _.each(content_fields,function(n) {
                    var val=m.get(n);
                    var f=get_field(that.options.model,n);
                    var s=render_field_value(val,f);
                    fields.push({
                        string: f.string,
                        value: s
                    });
                });
                group.records.push({
                    id: m.get("id"),
                    title: title_val,
                    fields: fields
                });
            });
            that.data.columns=_.values(groups);
            log("columns",that.data.columns);
            NFView.prototype.render.call(that);
        });
        return this;
    },

    drag_start_record: function(e) {
        log("start_drag_record");
        var model_id=$(e.target).data("model-id");
        log("model_id",model_id);
        e.originalEvent.dataTransfer.setData("model_id",model_id);
    },

    drag_over_group_body: function(e) {
        log("start_over_group_body");
        e.preventDefault();
    },

    drop_group_body: function(e) {
        log("drop_group_body");
        e.preventDefault();
        var model_id=e.originalEvent.dataTransfer.getData("model_id");
        log("model_id",model_id);
        var el=this.$el.find('.nf-columns-record[data-model-id="'+model_id+'"]');
        log("el",el);
        var body=$(e.target);
        if (!body.hasClass("nf-columns-group-body")) {
            body=body.parents(".nf-columns-group-body");
        }
        log("body",body);
        body.append(el);
    },
});

ColumnsView.register();
