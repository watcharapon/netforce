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

var MapView=NFView.extend({
    _name: "map_view",

    initialize: function(options) {
        //log("map_view.initialize",this);
        var that=this;
        NFView.prototype.initialize.call(this,options);
        if (this.options.grid_layout) {
            var layout=this.options.grid_layout;
        } else {
            if (this.options.view_xml) {
                var view=get_xml_layout({name:this.options.view_xml});
            } else {
                var view=get_xml_layout({model:this.options.model,type:"map"});
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
        //log("map_view.render",this);
        var that=this;
        this.data.page_title=this.$layout.attr("title")||this.options.string;
        var condition=this.options.condition||[];
        var coord_field=this.$layout.attr("coordinates_field");
        if (!coord_field) throw("Missing coordinates_field in map view");
        var title_field=this.$layout.attr("title_field");
        if (!title_field) throw("Missing title field in map view");
        window.nf_init_map=function() {
            log("nf_init_map");
            map_el=that.$el.find(".nf-map")[0];
            log("map_el",map_el);
            map=new google.maps.Map(map_el,{});
            var bounds = new google.maps.LatLngBounds();
            that.collection.each(function(m) {
                var val=m.get(coord_field);
                if (!val) return;
                var res=val.split(",");
                lat=parseFloat(res[0]);
                lng=parseFloat(res[1]);
                var pos = {lat: lat, lng: lng};
                var val=m.get(title_field);
                var f=get_field(that.options.model,title_field);
                var title_val=render_field_value(val,f);
                var marker = new google.maps.Marker({
                    position: pos,
                    map: map,
                    title: title_val
                });
                bounds.extend(new google.maps.LatLng(lat,lng));
            });
            map.fitBounds(bounds);
        };
        var field_names=[coord_field,title_field];
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
            NFView.prototype.render.call(that);
        });
        return this;
    },
});

MapView.register();
