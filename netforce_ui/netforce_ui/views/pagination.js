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

var Pagination=NFView.extend({
    _name: "pagination",
    events: {
        "click .page-link": "click_page",
        "change .page-select": "select_page",
        "change .limit-select": "select_limit"
    },

    render: function() {
        //log("pagination render",this);
        var collection=this.context.collection;
        var count=collection.count||collection.length;
        var offset=collection.offset||0;
        var limit=collection.limit||count;
        var cur_page=Math.floor(offset/limit)+1;
        var last_page=Math.floor((count-1)/limit)+1;
        log("pagination",collection.name,"count",count,"offset",offset,"limit",limit,"cur_page",cur_page,"last_page",last_page);
        if (last_page==1) return this;
        this.data.last_page=last_page;
        var pages=[];
        for (var p=1; p<=Math.min(100,last_page); p++) {
            pages.push({
                page: p,
                offset: (p-1)*limit,
                active: p==cur_page
            });
        }
        this.data.pages=pages;
        var page0=Math.max(1,cur_page-2);
        var page1=Math.min(last_page,cur_page+2);
        if (cur_page+2>last_page) page0=Math.max(1,page0-(cur_page+2-last_page));
        if (cur_page-2<1) page1=Math.min(last_page,page1+(1-(cur_page-2)));
        var items=[];
        for (var p=page0; p<=page1; p++) {
            items.push({
                page: p,
                offset: (p-1)*limit,
                active: p==cur_page
            });
        }
        this.data.items=items;
        if (cur_page>1) {
            this.data.page_prev={
                offset: (cur_page-1-1)*limit
            }
            this.data.page_start={
                offset: 0
            }
        }
        if (cur_page<last_page) {
            this.data.page_next={
                offset: (cur_page+1-1)*limit
            };
            this.data.page_end={
                offset: (last_page-1)*limit
            }
        }
        NFView.prototype.render.call(this);
        return this;
    },

    click_page: function(e) {
        log("click_page");
        e.preventDefault();
        e.stopPropagation();
        var offset=$(e.target).data("offset");
        log("offset",offset);
        var collection=this.context.collection;
        collection.offset=offset;
        collection.get_data();
        if (this.options.navigate) {
            var h=window.location.hash.substr(1);
            var action=qs_to_obj(h);
            action.offset=offset;
            var h2=obj_to_qs(action);
            workspace.navigate(h2);
        }
    },

    select_page: function(e) {
        log("select_page");
        e.preventDefault();
        e.stopPropagation();
        var offset=parseInt($(e.target).val());
        log("offset",offset);
        var collection=this.context.collection;
        collection.offset=offset;
        collection.get_data();
        if (this.options.navigate) {
            var h=window.location.hash.substr(1);
            var action=qs_to_obj(h);
            action.offset=offset;
            var h2=obj_to_qs(action);
            workspace.navigate(h2);
        }
    },

    select_limit: function(e) {
        log("select_limit");
        e.preventDefault();
        e.stopPropagation();
        var limit=parseInt($(e.target).val());
        log("limit",limit);
        var collection=this.context.collection;
        collection.limit=limit;
        collection.get_data();
        if (this.options.navigate) {
            var h=window.location.hash.substr(1);
            var action=qs_to_obj(h);
            action.limit=limit;
            var h2=obj_to_qs(action);
            workspace.navigate(h2);
        }
    }
});

Pagination.register();
