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

var FieldFile=NFView.extend({
    _name: "field_file",
    className: "form-group nf-field",
    events: {
        "click .file-choose": "choose",
        "click .file-clear": "clear",
        "change input": "change"
    },

    initialize: function(options) {
        NFView.prototype.initialize.call(this,options);
        var name=this.options.name;
        var model=this.context.model;
        model.on("change:"+name,this.render,this);
        if (this.options.inner) {
            this.template=this.options.inner;
        }
        this.listen_attrs();
    },

    render: function() {
        //log("field_file render",this.options.name);
        var name=this.options.name;
        var model=this.context.model;
        this.data.value=model.get(name);
        if (this.data.value) {
            var re=/^(.*),(.*?)(\..*)?$/;
            var m=re.exec(this.data.value);
            if (m) {
                var s=m[1];
                if (m[3]) s+=m[3];
            } else {
                s=this.data.value;
            }
            this.data.value_string=s;
            if (s.match(/\.png$|\.jpg$|\.gif$/i)) {
                this.data.picture=true;
            }
            this.data.value=encodeURIComponent(this.data.value);
        }
        var field=model.get_field(name);
        this.data.string=field.string;
        this.data.readonly=field.readonly||this.options.readonly;
        var form_layout=this.options.form_layout||"stacked";
        this.data.horizontal=this.options.form_layout=="horizontal";
        NFView.prototype.render.call(this);
        var attrs=this.eval_attrs();
        if (this.options.invisible || attrs.invisible) {
            this.$el.hide();
        } else {
            this.$el.show();
        }
    },

    choose: function(e) {
        log("choose");
        e.preventDefault();
        e.stopPropagation();
        this.$el.find("input").trigger("click");
    },

    clear: function() {
        var name=this.options.name;
        var model=this.context.model;
        model.set(name,null);
    },

    change: function() {
        log("file changed");
        var that=this;
        var inp_el=this.$el.find("input[type='file']")[0];
        var files=inp_el.files;
        if (!files.length) return;
        var file=files[0];
        log("file",file);
        var name=this.options.name;
        var model=this.context.model;
        var img=$("<img/>").attr("src","/static/img/spinner.gif").addClass("loading");
        this.$el.find("div.controls").prepend(img);
        if (window.FormData!==undefined) {
            log("upload start (ajax)");
            that.$el.find(".progress").text("0%");
            var file_data;
            var send_data=function() {
                log("send_data",file_data);
                if (file_data instanceof ArrayBuffer) {
                    content_type="image/jpeg";
                } else if (file_data instanceof FormData) {
                    content_type=false;
                } else {
                    throw "Invalid file data";
                }
                $.ajax({
                    url: "/upload?filename="+encodeURIComponent(file.name),
                    type: "POST",
                    data: file_data,
                    processData: false,
                    contentType: content_type,
                    success: function(res) { // TODO: use Location header instead
                        log("upload done (ajax)",res);
                        that.$el.find("img.loading").remove();
                        var val=res;
                        model.set(name,val);
                        if (that.options.onchange) {
                            var form=that.context.form;
                            form.do_onchange(that.options.onchange,name); // XXX: path
                        }
                    },
                    xhr: function() {
                        var xhr=jQuery.ajaxSettings.xhr();
                        xhr.upload.addEventListener("progress",function(evt) {
                            if (!evt.lengthComputable) return;
                            var pc=Math.floor(evt.loaded*100/evt.total)+"%";
                            that.$el.find(".progress").text(pc);
                        },false);
                        return xhr;
                    }
                });
            }
            if (this.options.resize && window.FileReader!==undefined) {
                var res=that.options.resize.split("x");
                var max_w=parseInt(res[0]);
                var max_h=parseInt(res[1]);
                var canvas=document.createElement("canvas");
                var mp_img=new MegaPixImage(file);
                mp_img.onrender=function() {
                    var new_data_url=canvas.toDataURL("image/jpeg",0.8);
                    log("data size: "+new_data_url.length);
                    var blob=dataURLtoBlob(new_data_url);
                    if (blob.type!="image/jpeg") { // android bug #1
                        log("reencoding to jpeg");
                        var ctx=canvas.getContext("2d");
                        var img_data=ctx.getImageData(0,0,canvas.width,canvas.height);
                        var enc=new JpegEncoder();
                        new_data_url=enc.encode(img_data,80);
                        log("data size2: "+new_data_url.length);
                        blob=dataURLtoBlob(new_data_url);
                        var f=new FileReader();
                        f.onload=function(e) {
                            file_data=e.target.result; // android bug #2
                            send_data();
                        }
                        f.readAsArrayBuffer(blob);
                    } else {
                        file_data=new FormData();
                        file_data.append("file",blob,file.name);
                        file_data.append("filename",file.name);
                        send_data();
                    }
                };
                mp_img.render(canvas,{maxWidth:max_w,maxHeight:max_h});
            } else {
                file_data=new FormData();
                file_data.append("file",file);
                send_data();
            }
        } else {
            alert("Can't upload file (unsupported browser)");
        }
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

FieldFile.register();
