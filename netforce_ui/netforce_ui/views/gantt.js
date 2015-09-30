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

var Gantt=NFView.extend({
    _name: "gantt",
    events: {
        "click .btn-back": "do_back",
        "click .btn-forward": "do_forward",
        "click .btn-mode": "change_mode"
    },

    initialize: function(options){
        console.log("Gantt.initialize");
        NFView.prototype.initialize.call(this,options);

        var h=window.location.hash.substr(1);
        var action=qs_to_obj(h)
        if(!action.mode){
            action.mode='today';
        }
        if(!action.time_start){ 
            var time_start=new Date();
            time_start.setHours(0);
            time_start.setMinutes(0);
            time_start.setSeconds(0);
        }
        if(!action.time_stop){
            var time_stop=new Date();
            time_stop.setHours(23);
            time_stop.setMinutes(59);
            time_stop.setSeconds(59);
            action.time_start=this.js2psql_date(time_start);
            action.time_stop=this.js2psql_date(time_stop);
        }

        var h2=obj_to_qs(action);
        workspace.navigate(h2);
    },

    js2psql_date: function(date){
        var d=date.getDate();
        var m=date.getMonth()+1;
        var y=date.getFullYear();
        var H=date.getHours();
        var M=date.getMinutes();
        var S=date.getSeconds();
        date='' + y + '-' + (m<=9 ? '0' + m : m) + '-' + (d <= 9 ? '0' + d : d);
        time=' '+(H<=9?"0"+H:H)+":"+(M<=9?"0"+M:M)+":"+(S<=9?"0"+S:S)
        return date+time
    },

    psql2js_date: function(date){
        // %Y-%m-%d %H:%M:%S
        var dt=date.split(" ");
        var new_date=dt[0].replace(/-/g,"/")+" "+dt[1];
        new_date=new Date(new_date);
        return new_date;
    },

    change_mode: function(e){
        console.log("Gantt.change_mode"); 
        var h=window.location.hash.substr(1);
        var action=qs_to_obj(h)
        action.mode=$(e.target).attr("data-mode") || "";

        var time_start=this.psql2js_date(action.time_start);
        var time_stop=this.psql2js_date(action.time_stop);

        if(action.mode=='today'){
            time_start=new Date();
            time_start.setHours(0);
            time_start.setMinutes(0);
            time_start.setSeconds(0);
            time_stop=new Date();
            time_stop.setHours(23);
            time_stop.setMinutes(59);
            time_stop.setSeconds(59);

        }else if(action.mode=='month'){
            var year=time_start.getFullYear();
            var crr_month=time_start.getMonth();
            console.log("crr_month ", crr_month);
            var days_in_month=new Date(year,crr_month,0).getDate();

            time_start=new Date(year,crr_month,1);
            time_stop=new Date(year,crr_month,days_in_month);

        }else if(action.mode=='week'){
            var copy_time_start=new Date(time_start.getTime());
            var date=copy_time_start.getDate();
            time_start.setDate(date);
            time_start.setHours(0)
            time_start.setMinutes(0)
            time_start.setSeconds(0);

            time_stop=new Date(copy_time_start.getTime());
            time_stop.setDate(date+7)
            time_stop.setHours(23)
            time_stop.setMinutes(59)
            time_stop.setSeconds(59);

        }else if(action.mode=='day'){
            var copy_time_start=new Date(time_start.getTime());
            var date=copy_time_start.getDate();
            time_start.setDate(date);
            time_start.setHours(0);
            time_start.setMinutes(0);
            time_start.setSeconds(0);

            time_stop=new Date(copy_time_start.getTime());
            time_stop.setDate(date);
            time_stop.setHours(23);
            time_stop.setMinutes(59);
            time_stop.setSeconds(59);
        }
        
        action.time_start=this.js2psql_date(time_start);
        action.time_stop=this.js2psql_date(time_stop);
        var h2=obj_to_qs(action);
        workspace.navigate(h2);
        this.render();
    },

    do_back: function(e){
        console.log("Gantt.do_back"); 
        var h=window.location.hash.substr(1)
        var action=qs_to_obj(h)
        var time_start=this.psql2js_date(action.time_start);
        var time_stop=this.psql2js_date(action.time_stop);

        switch(action.mode){
            case 'today':
                var prev_date=time_start.getDate()-1;
                time_start.setDate(prev_date);
                time_start.setHours(0);
                time_start.setMinutes(0);
                time_start.setSeconds(0);

                time_stop.setDate(prev_date);
                time_stop.setHours(23);
                time_stop.setMinutes(59);
                time_stop.setSeconds(59);

                break;

            case 'month':
                var prev_month=time_start.getMonth()-1;
                var year=time_start.getFullYear();
                var days_in_month=new Date(year,prev_month+1,0).getDate();
                time_start=new Date(year,prev_month,1);
                time_stop=new Date(year,prev_month,days_in_month);
                break;

            case "week":
                var year=time_start.getFullYear();
                var month=time_start.getMonth();
                var date_start=time_start.getDate();
                time_stop=new Date(year,month, time_start.getDate(),23,59,59);
                time_start.setDate(time_stop.getDate()-7);
                break;

            case "day":
                var prev_date=time_start.getDate()-1;
                time_start.setDate(prev_date);
                time_start.setHours(0);
                time_start.setMinutes(0);
                time_start.setSeconds(0);
                break;
            default:
                console.log("defaut");
        }

        action.time_start=this.js2psql_date(time_start);
        action.time_stop=this.js2psql_date(time_stop);
        var h2=obj_to_qs(action);
        workspace.navigate(h2);
        this.render();
    },

    do_forward: function(e){
        console.log("Gantt.do_forward"); 
        var h=window.location.hash.substr(1)
        var action=qs_to_obj(h)
        var time_start=this.psql2js_date(action.time_start);
        var time_stop=this.psql2js_date(action.time_stop);

        if(action.mode=='today'){
            var next_date=time_stop.getDate()+1;

            time_start.setDate(next_date);
            time_start.setHours(0);
            time_start.setMinutes(0);
            time_start.setSeconds(0);

            time_stop.setDate(next_date);
            time_stop.setHours(23);
            time_stop.setMinutes(59);
            time_stop.setSeconds(59);

        } else if(action.mode=='month'){
            var next_month=time_start.getMonth()+1;
            var year=time_start.getFullYear();
            
            var days_in_month=new Date(year,next_month+1,0).getDate();
            time_start=new Date(year,next_month,1);
            time_stop=new Date(year,next_month,days_in_month);

        }else if(action.mode=="week"){
            var year=time_stop.getFullYear();
            var month=time_stop.getMonth();
            var date=time_stop.getDate();

            var start=new Date(year,month,date);
            time_start=start;

            var stop=new Date(time_start.getTime());
            time_stop.setDate(stop.getDate()+7);
            time_stop.setHours(23);
            time_stop.setMinutes(59);
            time_stop.setSeconds(59);

        }else if (action.mode=="day"){
            var next_date=time_stop.getDate()+1;

            time_start.setDate(next_date);
            time_start.setHours(0);
            time_start.setMinutes(0);
            time_start.setSeconds(0);

            time_stop.setDate(next_date);
            time_stop.setHours(23);
            time_stop.setMinutes(59);
            time_stop.setSeconds(59);
        }

        action.time_start=this.js2psql_date(time_start);
        action.time_stop=this.js2psql_date(time_stop);
        var h2=obj_to_qs(action);
        workspace.navigate(h2);
        this.render();
    },

    render: function() {
        var that=this;
        var h=window.location.hash.substr(1);
        var action=qs_to_obj(h)
        console.log("render.action ", action);
        var time_start=this.psql2js_date(action.time_start);
        var time_stop=this.psql2js_date(action.time_stop);
        var mode=action.mode;
        this.data.title=this.options.string;
        this.data.mode=mode;
        this.data.sub_title="";

        //["Thu", "Jul", "31", "2014", "13:21:01", "GMT+0700", "(ICT)"]
        var start_str=time_start.toString().split(" ");
        var stop_str=time_stop.toString().split(" ");
        if(mode=='today' || mode=='day'){
            // 31, Jul 2014
            this.data.sub_title=start_str[2]+", "+start_str[1]+" "+start_str[3];
        }else if (mode=='month'){
            // Jul 2014
            this.data.sub_title=start_str[1]+" "+start_str[3];
        }else if (mode=='week'){
            // May 24 - Jul 31 2014
            this.data.sub_title=(start_str[1]+" "+start_str[2]) + " - " + (stop_str[1]+" "+stop_str[2]) +" " + stop_str[3];
        }

        this.data.time_start=this.js2psql_date(time_start);
        this.data.time_stop=this.js2psql_date(time_stop);

        NFView.prototype.render.call(this);
        var gantt_view=get_xml_layout({model:this.options.model,type:"gantt"});
        log("gantt_view",gantt_view);
        this.$layout=$($.parseXML(gantt_view.layout)).children();
        this.group_field=this.$layout.attr("group");
        this.start_field=this.$layout.attr("start");
        this.stop_field=this.$layout.attr("stop");
        this.label_field=this.$layout.attr("label");

        var cond=[];
        cond.push(['time_start', '>=', that.data.time_start])
        cond.push(['time_stop', '<=', that.data.time_stop])
        console.log("cond ", cond);
        var fields=[this.group_field,this.start_field,this.stop_field,this.label_field];
        rpc_execute(this.options.model,"search_read",[cond,fields],{},function(err,data) {
            that.draw_chart(data);
        });
        return this;
    },

    draw_chart: function(data) {
        var that=this;
        var tasks=[];
        var taskNames=[];
        var time_start=null;
        var time_end=null;
        //FIXME format for support all the browser is yyy/mm/dd H:M:S
        var convert_time=function(date){
            var dt=date.split(" ");
            var new_date=dt[0].replace(/-/g,"/")+" "+dt[1];
            return new_date;
        }
        _.each(data,function(obj) {
            var group=obj[that.group_field][1];
            taskNames.push(group);
            var t0=new Date(convert_time(obj[that.start_field]));
            var t1=new Date(convert_time(obj[that.stop_field]));
            var label=obj[that.label_field][1];
            tasks.push({
                job_id: obj.job_id,
                startDate: t0,
                endDate: t1,
                taskName: group,
                label: label
            });
            if (!time_start || t0<time_start) time_start=t0;
            if (!time_end || t1>time_end) time_end=t1;
        });
        taskNames.sort();
        taskNames=_.uniq(taskNames);
        log("tasks",tasks);
        log("taskNames",taskNames);
        log("time_start",time_start);
        log("time_end",time_end);
        var svg=d3.select(this.$el.find("svg")[0]);
        var width=1000;
        var height=80*taskNames.length;
        svg.attr("height",height+50+50);
        var x_scale = d3.time.scale().domain([ time_start, time_end ]).range([ 0, width ]).clamp(true);
        var y_scale = d3.scale.ordinal().domain(taskNames).rangeRoundBands([ 0, height ], .1);
        var margin_left=160;

        // draw horizontal grid
        svg.selectAll("line")
            .data(taskNames)
            .enter()
            .append("line")
            .attr("x1",margin_left+x_scale(time_start))
            .attr("y1",function(d) {
                return 50+y_scale(d)+15;
            })
            .attr("x2",margin_left+x_scale(time_end))
            .attr("y2",function(d) {
                return 50+y_scale(d)+15;
            })
            .style("fill","none")
            .style("stroke","#999")
            .style("shape-rendering","crispEdges");

        // draw rectangles
        svg.selectAll("rect")
            .data(tasks)
            .enter()
            .append("rect")
            .on("click",function(d){
                var action_name=that.$layout.attr("action");
                if (action_name) {
                    var action={
                        name: action_name,
                        mode: "form",
                        active_id: d.job_id
                    };
                    exec_action(action);
                }
            })
            .style("fill","#99f")
            .style("stroke","#333")
            .style("shape-rendering","crispEdges")
            .attr("x",function(d) {
                return margin_left+x_scale(d.startDate);
            })
            .attr("y",function(d) {
                return 50+y_scale(d.taskName);
            })
            .attr("height", 30)
            .attr("width", function(d) { 
                return x_scale(d.endDate) - x_scale(d.startDate); 
            });

        // draw text above rectangles
        svg.selectAll("text")
            .data(tasks)
            .enter()
            .append("text")
            .style("fill","black")
            .attr("x",function(d) {
                return margin_left+(x_scale(d.startDate)+x_scale(d.endDate))/2;
            })
            .attr("y",function(d) {
                return 50+y_scale(d.taskName)-5;
            })
            .style("text-anchor","middle")
            .text(function(d) { 
                return d.label; 
            });

        // draw x-axis
        var x_axis=d3.svg.axis()
            .scale(x_scale)
            .orient("bottom");
        svg.append("g")
            .attr("transform","translate("+margin_left+","+(height+30)+")")
            .call(x_axis)
            .selectAll("path,line")
            .style("fill","none")
            .style("stroke","black")
            .style("shape-rendering","crispEdges");

        // draw y-axis
        var y_axis=d3.svg.axis()
            .scale(y_scale)
            .orient("left");
        svg.append("g")
            .attr("transform","translate("+margin_left+",30)")
            .call(y_axis)
            .selectAll("path,line")
            .style("fill","none")
            .style("stroke","black")
            .style("shape-rendering","crispEdges");
    }
});

Gantt.register();
