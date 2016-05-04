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

var FieldMany2Many=NFView.extend({
    _name: "field_many2many",
    className: "nf-field form-group",

    events: {
        "click .m2m-add": "add_item",
        "click .m2m-remove": "remove_item"
    },

    initialize: function(options) {
        NFView.prototype.initialize.call(this,options);
        this.listen_attrs();
    },

    render: function() {
        //log("field_m2m render",this);
        var that=this;
        var attrs=this.eval_attrs();
        if (attrs.invisible) {
            this.$el.hide();
        } else {
            this.$el.show();
        }
        if (this.options.invisible) return;
        var name=this.options.name;
        var model=this.context.model;
        var field=model.get_field(name);
        this.data.string=field.string;
        var relation=field.relation;
        var ctx=_.clone(this.context);
        ctx.parent_id=model.id;
        var view_opts={
            "model": relation,
            "template": this.options.inner||this.options.template,
            "context": ctx
        };
        if (!view_opts.template) {
            //log("m2m get list view");
            var list_view=get_xml_layout({model:relation,type:"list"});
            var doc=$.parseXML(list_view.layout);
            view_opts.template=function(params) { 
                var $list=$(doc).find("list");
                var cols=[];
                $list.find("field").each(function() {
                    var $el=$(this);
                    cols.push({
                        col_type: "field",
                        name: $el.attr("name")
                    });
                });
                //log("m2m cols",cols);
                var opts={
                    cols: cols,
                    context: params.context
                }
                var view=List.make_view(opts);
                html="<div id=\""+view.cid+"\" class=\"view\"></div>";
                return html;
            };
        }
        var val=model.get(name);
        this.data.value=val;
        if (!val) val=[];
        //log("val",val);
        view_opts.condition=[["id","in",val]];
        var view_cls=get_view_cls("collection_view");
        var view=view_cls.make_view(view_opts);
        this.action_view=view;
        var tag=view.tagName;
        this.data.content='<'+tag+' id="'+view.cid+'" class="view"></'+tag+'>';
        this.data.readonly=field.readonly||this.options.readonly;
        var form_layout=this.options.form_layout||"stacked";
        this.data.horizontal=form_layout=="horizontal";
        this.data.render_head=function(ctx) { return that.render_head.call(that,ctx); };
        return NFView.prototype.render.call(this);
    },

    render_head: function(context) {
        var that=this;
        var html=$("<div/>");
        if (!this.data.readonly) {
            var opts={
                string: "Add",
                size: "small",
                context: context
            };
            opts.onclick=function() {
                that.add_item();
            }
            var view=Button.make_view(opts);
            html.append("<div id=\""+view.cid+"\" class=\"view\"></div>");
            if (this.data.value) {
                var opts={
                    string: "Remove",
                    size: "small",
                    context: context
                };
                opts.onclick=function() {
                    that.remove_item();
                }
                var view=Button.make_view(opts);
                html.append("<div id=\""+view.cid+"\" class=\"view\"></div>");
                if (this.options.view_layout && this.options.show_buttons) {
                    this.options.view_layout.find("head").children().each(function() {
                        var $el=$(this);
                        var tag=$el.prop("tagName");
                        if (tag=="button") {
                            var opts={
                                string: $el.attr("string"),
                                size: "small",
                                context: context
                            };
                            opts.onclick=function() {
                                that.call_method($el.attr("method"));
                            }
                            var view=Button.make_view(opts);
                            html.append("<div id=\""+view.cid+"\" class=\"view\"></div>");
                        }
                    });
                }
            }
        }
        return html.html();
    },

    add_item: function() {
        log("m2m_add",this);
        var that=this;
        var name=this.options.name;
        var model=this.context.model;
        var field=model.get_field(name);
        var relation=field.relation;
        var view_cls=get_view_cls("m2m_add");
        var options={
            model: relation,
            view_xml: this.options.select_view_xml
        };
        if (this.options.condition) {
            var data=this.context.model.get_vals();
            options.condition=eval_json(this.options.condition,data);
        }
        var view=view_cls.make_view(options);
        view.render();
        var modal_cont=$("<div/>").addClass("nf-modal-container");
        modal_cont.append(view.el);
        $("body").append(modal_cont);
        modal_cont.find(".modal").modal({show:true});
        view.on("items_selected",function(ids) {
            log("items_selected",ids);
            var model=that.context.model;
            var name=that.options.name;
            var val=model.get(name);
            if (!val) val=[];
            val=val.concat(ids);
            model.set(name,val);
            if (that.options.auto_save) {
                model.save({},{
                    success: function() {
                        model.trigger("reload");
                    }
                });
            } else {
                that.render();
                if (that.options.onchange) {
                    var path=model.get_path(name);
                    var form=that.context.form;
                    form.do_onchange(that.options.onchange,path);
                }
            }
        });
    },

    remove_item: function() {
        log("m2m_remove",this);
        var that=this;
        var collection=this.action_view.collection;
        var cids=[];
        collection.each(function(m) {
            if (m.get("_selected")) cids.push(m.cid);
        });
        log("cids",cids);
        if (cids.length==0) {
            alert("No items selected.");
            return;
        }
        collection.remove(cids);
        var ids=[];
        collection.each(function(m) {
            ids.push(m.id);
        });
        log("ids",ids);
        var model=this.context.model;
        var name=this.options.name;
        model.set(name,ids);
        if (this.options.auto_save) {
            model.save({},{
                success: function() {
                    model.trigger("reload");
                }
            });
        } else {
            this.render();
            if (this.options.onchange) {
                var path=model.get_path(name);
                var form=this.context.form;
                form.do_onchange(this.options.onchange,path);
            }
        }
    },

    call_method: function(method,context) {
        log("m2m.call_method",this,method);
        var that=this;
        if (!context) context={};
        var collection=this.action_view.collection;
        var ids=[];
        collection.each(function(m) {
            if (m.get("_selected")) ids.push(m.id);
        });
        if (ids.length==0) {
            set_flash("error","No items selected.");
            render_flash();
            return;
        }
        var model=this.context.model;
        rpc_execute(collection.name,method,[ids],{context:context},function(err,data) {
            if (err) {
                set_flash("error",err.message);
                render_flash();
                return;
            }
            if (data && data.flash) {
                set_flash("success",data.flash);
            }
            model.trigger("reload");
        });
    },

    eval_attrs: function() {
        var str=this.options.attrs;
        //log("eval_attrs",this,str);
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
                } else if (op=="not in") {
                    clause_v=!_.contains(cons,v);
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
    },

    listen_attrs: function() {
        var str=this.options.attrs;
        //log("listen_attrs",this,str);
        if (!str) return;
        var expr=JSON.parse(str);
        var attrs={};
        var depends=[];
        for (var attr in expr) {
            var conds=expr[attr];
            for (var i in conds) {
                var clause=conds[i];
                var n=clause[0];
                depends.push(n);
            }
        }
        //log("==> depends",depends);
        var model=this.context.model;
        for (var i in depends) {
            var n=depends[i];
            //log("...listen "+n);
            model.on("change:"+n,this.render,this);
        }
    }
});

FieldMany2Many.register();
