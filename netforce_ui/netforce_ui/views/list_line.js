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

var ListLine=NFView.extend({
    _name: "list_line",
    tagName: "tr",
    className: "list-line",
    events: {
        "click": "line_click",
        "change .list-line-select input": "line_select"
    },

    render: function() {
        //log("list_line render",this);
        var that=this;
        var list_view=this.options.list_view;
        var cols=list_view.cols;
        this.data.cols=cols;
        var colors=this.eval_colors();
        _.each(cols,function(col) {
            col.color=null;
            for (color_ in colors) {
                if (!colors[color_]) continue;
                if (color_.indexOf(",")==-1) continue;
                var field=color_.split(",")[0];
                if (field!=col.name) continue;
                col.color=color_.split(",")[1];
                break;
            }
        });
        this.data.select_model=!list_view.options.noselect && !list_view.options.select_group;
        this.data.select_group=list_view.options.select_group;
        NFView.prototype.render.call(this);
        for (var color in colors) {
            if (!colors[color]) continue;
            if (color.indexOf(",")!=-1) continue;
            if (color=="bold") {
                this.$el.find("td").css("font-weight","bold");
            } else {
                this.$el.find("td").css("background-color",color);
            }
        }
        if (list_view.options.active_id) {
            active_id=parseInt(list_view.options.active_id);
            var model=this.context.model;
            if (model.id==active_id) {
                this.$el.find("td").css("border-top","1px solid #666");
                this.$el.find("td").css("border-bottom","1px solid #666");
                setTimeout(function() {
                    var vh=$(window).height();
                    var eh=that.$el.height();
                    $("body,html").scrollTop(that.$el.offset().top+eh/2-vh/2);
                },100); // XXX
            }
        }
        this.$el.data("model-id",this.context.model.id);
    },

    line_click: function(e) {
        log("list_line.line_click",this);
        if ($(e.target).prop("tagName")=="A") return; // for links in list items
        if ($(e.target).parent(".list-line-select").length>0) return;
        e.preventDefault();
        e.stopPropagation();
        var model=this.context.model;
        model.trigger("click",model);
    },

    line_select: function(e) {
        e.preventDefault();
        e.stopPropagation();
        var val=$(e.target).is(":checked");
        var model=this.context.model;
        model.set("_selected",val);
    },

    eval_colors: function() {
        var str=this.options.list_view.options.colors;
        if (!str) return {};
        var expr=JSON.parse(str);
        var model=this.context.model;
        var attrs={};
        for (var attr in expr) {
            var conds=expr[attr];
            var attr_val=true;
            for (var i in conds) {
                var clause=conds[i];
                var n=clause[0];
                var op=clause[1];
                var cons=clause[2];
                var v=model.get(n);
                var clause_v;
                if (op=="=") {
                    clause_v=v==cons;
                } else if (op=="!=") {
                    clause_v=v!=cons;
                } else if (op=="in") {
                    clause_v=_.contains(cons,v);
                } else if (op=="<") {
                    clause_v=v<cons;
                } else if (op==">") {
                    clause_v=v>cons;
                } else {
                    throw "Invalid operator: "+op;
                }
                if (!clause_v) {
                    attr_val=false;
                    break;
                }
            }
            attrs[attr]=attr_val;
        }
        //log("==>",attrs);
        return attrs;
    }
});

ListLine.register();
