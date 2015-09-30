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

var Export=NFView.extend({
    _name: "export",
    events: {
        "click .field-row": "click_field",
        "click .select-all": "click_select_all",
        "click .do-export": "do_export"
    },

    render: function() {
        log("export.render");
        var that=this;
        var model_cls=get_model(this.options.model);
        this.data.model_name=this.options.model;
        this.data.model_string=model_cls.string;
        this.data.fields=[{
            name: "id",
            string: "Database ID",
            row_id: _.uniqueId("row")
        }];
        _.each(model_cls.fields,function(f,n) {
            var field={
                name: n,
                string: f.string,
                row_id: _.uniqueId("row")
            };
            if (f.type=="many2one") {
                field.can_expand=true;
            } else if (f.type=="one2many") {
                field.can_expand=true;
            }
            that.data.fields.push(field);
        });
        this.data.fields=_.sortBy(this.data.fields,function(f) {return f.string});
        NFView.prototype.render.call(this);
        //this.load_export_view();
        this.load_export_fields();
    },

    click_field: function(e) {
        log("export.click_field");
        log("target",e.target);
        if ($(e.target).prop("tagName")=="INPUT") return;
        e.preventDefault();
        var tr=$(e.target).parents("tr");
        var state=tr.data("state");
        if (state=="collapsed") {
            this.expand_field(tr);
        } else if (state=="expanded") {
            this.collapse_field(tr);
        }
    },

    expand_field: function(tr) {
        var model=tr.data("model");
        var field=tr.data("field");
        var depth=tr.data("depth");
        var path=tr.data("path");
        log("model",model,"field",field);
        var model_cls=get_model(model);
        var f=model_cls.fields[field];
        var rmodel=f.relation;
        var rmodel_cls=get_model_cls(rmodel);
        var rdepth=depth+1;
        var fields_=[];
        _.each(rmodel_cls.fields,function(f,n) {
            var field={
                name: n,
                string: f.string,
                row_id: _.uniqueId("row")
            };
            if (f.type=="many2one") {
                field.can_expand=true;
            } else if (f.type=="one2many") {
                field.can_expand=true;
            }
            fields_.push(field);
        });
        fields_=_.sortBy(fields_,function(f) {return f.string});
        var last_el=tr;
        _.each(fields_,function(f) {
            var html="<tr class='field-row' data-field='"+f.name+"' data-model='"+rmodel+"' data-depth='"+rdepth+"' data-row-id='"+f.row_id+"' data-state='collapsed' data-parent-id='"+tr.data("row-id")+"' data-path='"+path+"."+f.name+"'><td><input type='checkbox'/></td><td style='padding-left:"+rdepth*30+"px'>";
            if (f.can_expand) {
                html+="<i class='icon-chevron-right' style='margin-right:5px'></i>";
            }
            html+=f.string+"</td><td>"+f.name+"</td><td>"+rmodel_cls.string+"</td></tr>";
            var el=$(html);
            last_el.after(el);
            last_el=el;
        });
        tr.data("state","expanded");
    },

    collapse_field: function(tr) {
        var row_id=tr.data("row-id");
        this.$el.find("tr[data-parent-id="+row_id+"]").remove();
        tr.data("state","collapsed");
    },

    click_select_all: function(e) {
        log("export.click_select_all",e.target);
        var res=$("tr.field-row input:not(:checked)");
        if (res.length>0) {
            res.prop("checked",true);
            $(e.target).prop("checked",true);
        } else {
            $("tr.field-row input").prop("checked",false);
            $(e.target).prop("checked",false);
        }
    },

    do_export: function(e) {
        log("export.do_export");
        e.preventDefault();
        var export_fields=[];
        $("tr.field-row input:checked").each(function() {
            var path=$(this).parents("tr").data("path");
            export_fields.push(path);
        });
        log("export_fields",export_fields);
        this.export_fields=export_fields;
        this.save_export_fields();
        var action={
            name: "export_data", // XXX: should not need name
            type: "export",
            model: this.options.model,
            condition: this.options.condition,
            export_fields: export_fields
        };
        exec_action(action);
    },

    select_fields: function(fields) {
        log("export.select_fields",fields);
        var that=this;
        _.each(fields,function(name) {
            log("name",name);
            var comps=name.split(".");
            for (var i=0; i<comps.length-1; i++) {
                var path=comps.splice(0,i+1).join(".");
                log("parent path",path);
                var tr=that.$el.find("tr.field-row[data-path='"+path+"']")
                var state=tr.data("state");
                if (state=="collapsed") {
                    that.expand_field(tr);
                }
            }
            var inp=that.$el.find("tr.field-row[data-path='"+name+"']").find("input");
            log("inp",inp);
            inp.prop("checked",true);
        });
    },

    load_export_view: function() {
        var export_view=get_xml_layout({model:this.options.model,type:"export",noerr:true});
        if (!export_view) return;
        var layout=export_view.layout;
        var doc=$.parseXML(layout);
        var $layout=$(doc).children();
        var fields=[];
        $layout.find("field").each(function() {
            var $el=$(this);
            var name=$el.attr("name");
            fields.push(name);
        });
        this.select_fields(fields);
    },

    save_export_fields: function() {
        rpc_execute("field.default","set_default",[this.options.model,"_export_fields",JSON.stringify(this.export_fields)]);
    },

    load_export_fields: function() {
        var that=this;
        rpc_execute("field.default","get_default",[this.options.model,"_export_fields"],{},function(err,data) {
            if (!data) return;
            var fields=JSON.parse(data);
            that.select_fields(fields);
        });
    }
});

Export.register();
