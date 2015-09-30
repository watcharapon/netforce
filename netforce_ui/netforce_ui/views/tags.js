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

var Tags=NFView.extend({
    _name: "tags",
    className: "form-group",
    events: {
        "change input": "onchange",
        "blur input": "blur"
    },

    initialize: function(options) {
        NFView.prototype.initialize.call(this,options);
        var name=this.options.name;
        var model=this.context.model;
        model.on("change:"+name,this.render,this);
        if (this.options.inner) {
            this.template=this.options.inner;
        }
    },

    render: function() {
        log("tags render",this.options.name);
        var name=this.options.name;
        var model=this.context.model;
        var value=model.get(name);
        var field=model.get_field(name);
        this.data.string=field.string;
        this.data.readonly=field.readonly||this.options.readonly||this.context.readonly;
        NFView.prototype.render.call(this);
        if (this.options.invisible) {
            this.$el.hide();
        }
        if (this.options.size) {
            this.$el.find("input").addClass("input-"+this.options.size);
        }
        if (this.options.span) {
            this.$el.addClass("col-sm-"+this.options.span);
            this.$el.find("input").addClass("col-sm-"+this.options.span);
        }
        if (this.options.offset) {
            this.$el.addClass("offset"+this.options.offset);
        }
        if (this.options.width) {
            this.$el.find("input").width(this.options.width-8);
            this.$el.width(this.options.width);
        }
        if (this.options.nomargin) {
            this.$el.find("input").css({margin:"0"});
            this.$el.css({margin:"0"});
        }
        var that=this;
        var relation=field.relation;
        rpc_execute(relation,"search_read",[[],["name"]],{},function(err,data) { // TODO: filter
            var data2=[];
            var id2name={};
            for (var i in data) {
                var obj=data[i];
                data2.push({id:obj.id,text:obj.name});
                id2name[obj.id]=obj.name;
            }
            var val=[];
            for (var i in value) {
                var id=value[i];
                var name=id2name[id];
                val.push({id:id,text:name});
            }
            that.$el.find("input").select2({data:data2,multiple:true});
            that.$el.find("input").select2("val",val);
        });
    },

    onchange: function() {
        log("tags change",onchange);
        var val_s=this.$el.find("input").val();
        var val=_.map(val_s.split(","),function(v) {
            return parseInt(v);
        });
        log("val",val);
        var name=this.options.name;
        var model=this.context.model;
        model.set(name,val);
    },

    focus: function() {
        this.$el.find("input").focus();
    },

    blur: function() {
        this.trigger("blur");
    }
});

Tags.register();
