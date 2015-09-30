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

var ChartPie=NFView.extend({
    _name: "chart_pie",

    render: function() {
        var that=this;
        var name=this.options.name;
        var model=this.context.model;
        var data=model.get(name);
        setTimeout(function() { // XXX: timeout to get el width
            var width=parseInt(that.options.width||300); // XXX
            var height=parseInt(that.options.height||200);
            that.$el.width(width);
            that.$el.height(height);
            if (_.isEmpty(data)) {
                that.$el.text("There is no data to display.");
            } else {
                var values=[];
                var chart=new Highcharts.Chart({
                    chart: {
                        renderTo: that.el,
                        type: "pie"
                    },
                    title: {
                        text: ""
                    },
                    series: [{
                        name: "Value",
                        data: data
                    }],
                    plotOptions: {
                        pie: {
                            dataLabels: {
                                enabled: true
                            }
                        }
                    },
                    credits: {
                        enabled: false
                    }
                });
            }
        },100);
        return this;
    }
});

ChartPie.register();
