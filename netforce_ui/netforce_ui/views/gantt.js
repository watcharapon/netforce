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
    },

    initialize: function(options){
        console.log("Gantt.initialize");
        NFView.prototype.initialize.call(this,options);

    },

    render: function() {
        console.log("Gantt.render",this);
        this.data.title=this.options.string;
        NFView.prototype.render.call(this);
        setTimeout(function() {
            $("#ganttemplates").loadTemplates();
            var ge=new GanttMaster();
            var workspace=this.$el.find(".nf-gantt-content");
            var w=$(window).width();
            var h=$(window).height()-245;
            workspace.css({width: w, height: h});
            log("workspace",workspace);
            ge.init(workspace);
            var gantt_view=get_xml_layout({model:this.options.model,type:"gantt"});
            log("gantt_view",gantt_view);
            this.$layout=$($.parseXML(gantt_view.layout)).children();
            this.group_field=this.$layout.attr("group");
            if (!this.group_field) throw "Missing attribute 'group' in gantt layout";
            this.start_field=this.$layout.attr("start");
            if (!this.start_field) throw "Missing attribute 'start' in gantt layout";
            this.stop_field=this.$layout.attr("stop");
            if (!this.stop_field) throw "Missing attribute 'stop' in gantt layout";
            this.label_field=this.$layout.attr("label");
            if (!this.label_field) throw "Missing attribute 'label' in gantt layout";

            var cond=[];
            console.log("cond ", cond);
            var fields=[this.group_field,this.start_field,this.stop_field,this.label_field];
            rpc_execute(this.options.model,"search_read",[cond,fields],{},function(err,data) {
                if (err) {
                    throw "Failed to get gantt data: "+err.message;
                }
                var proj_data={
                    tasks: [],
                    canWrite: false,
                };
                _.each(data,function(obj) {
                    var task={
                        id: obj.id,
                        name: obj[this.label_field][1], // XXX
                        level: 1,
                        start: new moment(obj[this.start_field]).unix()*1000,
                        end: new moment(obj[this.stop_field]).unix()*1000,
                        duration: 5, // XXX
                        startIsMilestone: false,
                        endIsMilestone: false,
                        depends: "",
                        status: "STATUS_ACTIVE",
                        progress: 60,
                        assigs: [],
                    };
                    console.log("task",task);
                    proj_data.tasks.push(task);
                }.bind(this));
                ge.loadProject(proj_data);
            }.bind(this));
        }.bind(this),100);
        return this;
    },
});

Gantt.register();
