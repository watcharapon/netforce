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

var ChartLine=NFView.extend({
    _name: "chart_line",

    render: function() {
        var that=this;
        var name=this.options.name;
        var model=this.context.model;
        var data=model.get(name);
        setTimeout(function() { // XXX: timeout to get el width
            var width=parseInt(that.options.width||that.$el.width()); // XXX
            var height=parseInt(that.options.height||150);
            //that.$el.width(width);
            that.$el.width(width);
            that.$el.height(height);
            if (_.isEmpty(data)) {
                that.$el.text("There is no data to display.");
            } else {
                var chart=new Highcharts.Chart({
                    chart: {
                        renderTo: that.el,
                        type: "area"
                    },
                    title: {
                        text: ""
                    },
                    xAxis: {
                        type: "datetime"
                    },
                    yAxis: {
                        title: {
                            enabled: false,
                            text: ""
                        }
                    },
                    series: [{
                        name: "Amount",
                        data: data
                    }],
                    legend: {
                        enabled: false
                    },
                    plotOptions: {
                        area: {
                            marker: {
                                enabled: false,
                                states: {
                                    hover: {
                                        enabled: true
                                    }
                                }
                            },
                            fillColor: {
                                linearGradient: { x1: 0, y1: 0, x2: 0, y2: 1},
                                stops: [
                                    [0, Highcharts.getOptions().colors[0]],
                                    [1, 'rgba(2,0,0,0)']
                                ]
                            }
                        }
                    },
                    tooltip: {
                        formatter: function() {
                            return Highcharts.dateFormat("%A, %b %e %Y",this.x)+"<br><b>"+Highcharts.numberFormat(this.y,2)+"</b>";
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

ChartLine.register();
