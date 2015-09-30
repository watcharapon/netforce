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

var RelatedTabs=NFView.extend({
    _name: "related_tabs",
    events: {
        "click ul.nav-tabs a": "click_tab"
    },

    initialize: function(options) {
        //log("related_tabs.initialize",this);
        NFView.prototype.initialize.call(this,options);
        this.$tabs=this.options.tabs_layout;
    },

    render: function() {
        //log("related_tabs.render");
        var that=this;
        var tabs=[];
        if (!this.active_tab) this.active_tab=0;
        this.$tabs.children().each(function(i) {
            var $el=$(this);
            var tag=$el.prop("tagName");
            if (tag!="field") throw "Expected 'field' element instead of '"+tag+"'";
            var name=$el.attr("name");
            var f=that.context.model.get_field(name);
            var tab={
                tab_type: "field",
                field_name: name,
                string: f.string, 
                active: i==that.active_tab,
                tab_id: i,
                tab_layout: $el
            }
            tabs.push(tab);
        });
        this.tabs=tabs;
        this.data.tabs=tabs;
        this.data.render_tab=function($tab,ctx) { return that.render_tab.call(that,$tab,ctx); };
        NFView.prototype.render.call(this);
        return this;
    },

    render_tab: function(context) {
        log("related_tabs.render_tab",this);
        var that=this;
        var body=$("<div/>");
        var tab=this.tabs[this.active_tab];
        var field_name=tab.field_name;
        var f=this.context.model.get_field(field_name);
        if (f.relfield) {
            var condition=[[f.relfield,"=",this.context.model.id]];
        } else {
            var ctx={
                active_id: this.context.model.id
            };
            var condition=eval_json(f.condition,ctx);
        }
        var opts={
            model: f.relation,
            condition: condition,
            list_layout: tab.tab_layout.find("list"),
            search_layout: tab.tab_layout.find("search"),
            show_search: true,
            context: context
        }
        var view=ListView.make_view(opts);
        html="<div id=\""+view.cid+"\" class=\"view\"></div>";
        body.append(html);
        return body.html();
    },

    click_tab: function(e) {
        log("click_tab");
        e.preventDefault();
        e.stopPropagation();
        var tab_id=$(e.target).attr("href").substr(1);
        log("tab_id",tab_id);
        this.active_tab=parseInt(tab_id);
        this.render();
    }
});

RelatedTabs.register();
