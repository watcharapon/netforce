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

var TreeItem=NFView.extend({
    _name: "tree_item",
    tagName: "tr",
    events: {
        "click": "item_click"
    },

    initialize: function(options) {
        //log("tree_item.initialize",this);
        NFView.prototype.initialize.call(this,options);
        this.tree_view=this.options.tree_view;
        if (!this.tree_view) throw "Missing tree_view";
    },

    render: function() {
        //log("tree_item.render",this);
        var cols=[];
        var i=0;
        var model=this.context.model;
        this.tree_view.$tree.children().each(function() {
            var $el=$(this);
            var tag=$el.prop("tagName");
            if (tag=="field") {
                cols.push({
                    col_type: "field",
                    name: $(this).attr("name"),
                    nowrap: $(this).attr("nowrap"),
                    first: i==0
                });
            } else if (tag=="button") {
                cols.push({
                    col_type: "button",
                    button_string: $(this).attr("string"),
                    action: $(this).attr("action"),
                    action_options: ($(this).attr("action_options")?$(this).attr("action_options")+"&":"")+"active_id="+model.id,
                    first: i==0
                });
            }
            i+=1;
        });
        this.data.cols=cols;
        var child_field=this.tree_view.$tree.attr("child_field");
        var model=this.context.model;
        var children=model.get(child_field);
        if (!_.isEmpty(children) && !this.expanded) {
            this.data.collapsed=true;
            this.data.expanded=false;
        }
        if (this.expanded) {
            this.data.expanded=true;
            this.data.collapsed=false;
        }
        this.data.padding=model.get("_depth")*15;
        NFView.prototype.render.call(this);
        return this;
    },

    item_click: function(e) {
        log("tree_item.click",this);
        e.preventDefault();
        e.stopPropagation();
        this.tree_view.item_click(this);
    }
});

TreeItem.register();
