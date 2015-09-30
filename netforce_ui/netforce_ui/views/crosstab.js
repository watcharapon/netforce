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

var Crosstab=NFView.extend({
    _name: "crosstab",

    initialize: function(options) {
        NFView.prototype.initialize.call(this,options);
    },

    render: function() {
        log("crosstab.render",this);
        var collection=this.context.collection;
        var group_fields=this.options.group_fields;
        var group_field=group_fields[0];
        var subgroup_field=group_fields[1];
        var model_cls=get_model(collection.name);
        this.data.group_field_string=model_cls.fields[group_field].string;
        this.data.subgroup_field_string=model_cls.fields[subgroup_field].string;
        var groups={};
        var subgroups={};
        if (this.options.sum_fields) {
            var sum_field_names=this.options.sum_fields.split(",");
        } else {
            var sum_field_names=[];
        }
        var sum_fields=[];
        _.each(sum_field_names,function(n) {
            var f=model_cls.fields[n];
            if (!f) throw "Invalid field: "+n;
            sum_fields.push({
                name: n,
                string: f.string,
                value: 0
            });
        });
        var grand_total={
            count: 0,
            sum_fields: sum_fields
        };
        this.data.grand_total=grand_total;
        collection.each(function(m) {
            var ctx={model:m};
            var group_val=field_value(group_field,ctx);
            var subgroup_val=field_value(subgroup_field,ctx);
            var group=groups[group_val];
            if (!group) {
                var sum_fields=[];
                _.each(sum_field_names,function(n) {
                    var f=model_cls.fields[n];
                    if (!f) throw "Invalid field: "+n;
                    sum_fields.push({
                        name: n,
                        string: f.string,
                        value: 0
                    });
                });
                group={
                    value: group_val,
                    totals: {},
                    grand_total: {
                        count: 0,
                        sum_fields: sum_fields
                    }
                };
                groups[group_val]=group;
            }
            var subgroup=subgroups[subgroup_val];
            if (!subgroup) {
                var sum_fields=[];
                _.each(sum_field_names,function(n) {
                    var f=model_cls.fields[n];
                    if (!f) throw "Invalid field: "+n;
                    sum_fields.push({
                        name: n,
                        string: f.string,
                        value: 0
                    });
                });
                subgroup={
                    value: subgroup_val,
                    grand_total: {
                        count: 0,
                        sum_fields: sum_fields
                    }
                };
                subgroups[subgroup_val]=subgroup;
            }
            var totals=group.totals;
            if (!totals[subgroup_val]) {
                var sum_fields=[];
                _.each(sum_field_names,function(n) {
                    var f=model_cls.fields[n];
                    if (!f) throw "Invalid field: "+n;
                    sum_fields.push({
                        name: n,
                        string: f.string,
                        value: 0
                    });
                });
                totals[subgroup_val]={
                    count: 0,
                    sum_fields: sum_fields
                };
            }
            totals[subgroup_val].count+=1;
            _.each(totals[subgroup_val].sum_fields,function(sum) {
                sum.value+=m.get(sum.name)||0;
            });
            group.grand_total.count+=1;
            _.each(group.grand_total.sum_fields,function(sum) {
                sum.value+=m.get(sum.name)||0;
            });
            subgroup.grand_total.count+=1;
            _.each(subgroup.grand_total.sum_fields,function(sum) {
                sum.value+=m.get(sum.name)||0;
            });
            grand_total.count+=1;
            _.each(grand_total.sum_fields,function(sum) {
                sum.value+=m.get(sum.name)||0;
            });
        });
        log("groups",groups);
        log("subgroups",subgroups);
        _.each(groups,function(group) {
            _.each(subgroups,function(o,v) {
                if (!group.totals[v]) {
                    var sum_fields=[];
                    _.each(sum_field_names,function(n) {
                        var f=model_cls.fields[n];
                        if (!f) throw "Invalid field: "+n;
                        sum_fields.push({
                            name: n,
                            string: f.string,
                            value: 0
                        });
                    });
                    group.totals[v]={
                        count: 0,
                        sum_fields: sum_fields
                    };
                }
            });
            group.totals=_.sortBy(group.totals,function(o,v) {
                return v;
            });
        });
        this.data.groups=_.sortBy(groups,function(o) {
            return o["value"];
        });
        this.data.subgroups=_.sortBy(subgroups,function(o) {
            return o["value"];
        });
        NFView.prototype.render.call(this);
    }
});

Crosstab.register();
