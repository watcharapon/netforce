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

var Chart=NFView.extend({
    _name: "chart",

    render: function() {
        //log("chart.render",this);
        var that=this;
        var data=this.options.data||this.context.value|| this.context.data && this.context.data.value;
        if (!data) {
            log("WARNING","No chart data");
            return this;
        }
        //log("data",data);
        var type=this.options.type;
        setTimeout(function() { // XXX: timeout for el width
            var width=parseInt(that.options.width||that.$el.width); // XXX
            var height=parseInt(that.options.height||150);
            that.$el.width(width);
            that.$el.height(height);
            if (type=="line") {
                if (data.length==0) {
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
            } else if (type=="bar") {
                if (data.length==0) {
                    that.$el.text("There is no data to display.");
                } else {
                    var categs=[];
                    var values=[];
                    for (var i in data) {
                        var d=data[i];
                        categs.push(d[0]);
                        values.push(d[1]);
                    }
                    var chart=new Highcharts.Chart({
                        chart: {
                            renderTo: that.el,
                            type: "column"
                        },
                        title: {
                            text: that.options.title||""
                        },
                        xAxis: {
                            categories: categs
                        },
                        yAxis: {
                            title: {
                                enabled: false,
                                text: ""
                            }
                        },
                        series: [{
                            name: "Amount",
                            data: values,
                            point: {
                                events: {
                                    click: function() {
                                        log("click",that.category);
                                        if (that.options.onclick_action) {
                                            var action={
                                                name: that.options.onclick_action,
                                                context: {
                                                    category: that.category
                                                }
                                            };
                                            exec_action(action);
                                        }
                                    }
                                }
                            }
                        }],
                        tooltip: {
                            formatter: function() {
                                return this.x+"<br><b>"+Highcharts.numberFormat(this.y,2)+"</b>";
                            }
                        },
                        legend: {
                            enabled: false
                        },
                        credits: {
                            enabled: false
                        }
                    });
                }
            } else if (type=="multibar") {
                var series=[];
                for (var k in data) {
                    var data1=data[k].values;
                    series.push({
                        data: data1
                    });
                }
                var chart=new Highcharts.Chart({
                    chart: {
                        renderTo: that.el,
                        type: "column"
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
                    series: series,
                    legend: {
                        enabled: false
                    },
                    credits: {
                        enabled: false
                    }
                });
            } else if (type=="pie") {
                if (data.length==0) {
                    that.$el.text("There is no data to display.");
                } else {
                    var chart=new Highcharts.Chart({
                        chart: {
                            renderTo: that.el,
                            type: "pie",
                            margin: [30,0,30,0]
                        },
                        title: {
                            text: ""
                        },
                        series: [{
                            name: "Amount",
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
            }
        },100);
        return this;
    }
});

Chart.register();
