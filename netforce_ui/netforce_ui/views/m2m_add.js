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

var M2MAdd=NFView.extend({
    _name: "m2m_add",
    className: "modal nf-modal",
    events: {
        "click .m2m-select": "select",
        "click .m2m-cancel": "cancel"
    },

    render: function() {
        var opts={
            model: this.options.model,
            condition: this.options.condition,
            view_xml: this.options.view_xml,
            show_search: true,
            no_click: true
        };
        var view_cls=get_view_cls("list_view");
        var view=new view_cls({options:opts});
        this.list_view=view;
        var content="<div id=\""+view.cid+"\" class=\"view\"></div>";
        this.data.content=content;
        NFView.prototype.render.call(this);
    },

    select: function() {
        log("m2m_select",this);
        var ids=this.list_view.get_selected_ids();
        log("selected ids",ids);
        if (ids.length==0) {
            alert("No items selected.");
            return;
        }
        $(".modal").modal("hide");
        this.trigger("items_selected",ids);
    },

    cancel: function() {
        log("m2m_cancel",this);
        $(".modal").modal("hide");
    }
});

M2MAdd.register();
