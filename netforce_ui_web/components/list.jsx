React = require("react");
var connect = require("react-redux").connect;
var actions=require("../actions");
var ui_params=require("../ui_params");
var rpc=require("../rpc");
var utils=require("../utils");
var dom = require('xmldom').DOMParser;
var xpath = require('xpath');
var Loading=require("./loading")
var classNames = require('classnames');
var _=require("underscore");
var Search=require("./search")
var FieldChar=require("./field_char")
var FieldMany2One=require("./field_many2one")

var List=React.createClass({
    mixins: [ui_params],

    getInitialState() {
        var layout;
        if (this.props.layout) {
            layout=this.get_layout(this.props.layout);
        } else {
            layout=this.find_layout({model:this.props.model,type:"list"});
            if (!layout) throw "List layout not found for model "+this.props.model;
        }
        var doc=new dom().parseFromString(layout.layout);
        var layout_el=doc.documentElement;
        return {
            layout_el: layout_el,
            active_tab: 0,
            checked_items: {},
            offset: 0,
            limit: 100,
        };
    },

    componentDidMount() {
        this.load_data();
    },

    load_data() {
        console.log("List.load_data");
        var cond=[];
        if (this.props.tabs) {
            console.log("active_tab",this.state.active_tab);
            var tab_cond=this.props.tabs[this.state.active_tab][1];
            cond.push(tab_cond);
        }
        if (this.state.search_cond) {
            cond.push(this.state.search_cond);
        }
        var cond_nogroup=cond.slice(0);
        if (this.state.group_val) {
            cond.push([this.props.group_field,"=",this.state.group_val]);
        }
        console.log("cond",cond);
        var field_els=xpath.select("field", this.state.layout_el);
        var field_names=[];
        field_els.forEach(function(el) {
            var name=el.getAttribute("name");
            field_names.push(name);
        });
        this.setState({data:null,checked_items:{},check_all:false});
        var ctx={};
        rpc.execute(this.props.model,"search_read",[cond,field_names],{count:true,offset:this.state.offset,limit:this.state.limit,context:ctx},function(err,res) {
            this.setState({data:res[0],count:res[1]});
        }.bind(this));
        if (this.props.group_field) {
            var group_fields=[this.props.group_field];
            rpc.execute(this.props.model,"read_group",[],{group_fields:group_fields,condition:cond_nogroup},(err,res)=>{
                if (err) throw err;
                this.setState({group_data:res});
            });
        }
    },

    render() {
        var child_els=xpath.select("child::*",this.state.layout_el);
        var m=this.get_model(this.props.model);
        return <div>
            <div className="page-header">
                <h2>{this.props.title}</h2>
            </div>
            {function() {
                if (!this.state.error) return;
                return <div className="alert alert-danger">
                    <a className="close" data-dismiss="alert" href="#">&times;</a>
                    {this.state.error}
                </div>
            }.bind(this)()}
            {function() {
                if (!this.state.message) return;
                return <div className="alert alert-success">
                    <a className="close" data-dismiss="alert" href="#">&times;</a>
                    {this.state.message}
                </div>
            }.bind(this)()}
            <div className="btn-toolbar" style={{marginBottom:10}}>
                <button className="btn btn-default" style={{marginRight:10}} onClick={this.on_new}><span className="glyphicon glyphicon-plus"></span> New {m.string}</button>
                <button className="btn btn-default"><span className="glyphicon glyphicon-download"></span> Import</button>
            </div>
            {function() {
                if (!this.props.tabs) return;
                return <ul className="nav nav-tabs">
                    {this.props.tabs.map(function(o,i) {
                        return <li key={i} className={i==this.state.active_tab?"active":null}><a href="#" onClick={this.click_tab.bind(this,i)}>{o[0]}</a></li>
                    }.bind(this))}
                </ul>
            }.bind(this)()}
            {function() {
                if (!this.state.group_data) return;
                return <ul className="nav nav-pills" style={{margin:"10px 0"}}>
                    {this.state.group_data.map((r,i)=>{
                        var v=r[this.props.group_field];
                        var f=this.get_field(this.props.model,this.props.group_field);
                        var search_val;
                        if (f.type=="many2one"||f.type=="reference") {
                            search_val=v?v[0]:null;
                        } else {
                            search_val=v;
                        }
                        return <li key={i} className={search_val==this.state.group_val?"active":null}><a href="#" onClick={this.click_group_pill.bind(this,search_val)}>{utils.fmt_field_val(v,f)} ({r._count})</a></li>
                    })}
                </ul>
            }.bind(this)()}
            {function() {
                if (!this.state.show_search) return;
                return <Search model={this.props.model} on_close={this.hide_search} on_search={this.search}/>
            }.bind(this)()}
            <div style={{marginTop:10}}>
                <button className="btn btn-danger btn-sm" onClick={this.call_method.bind(this,"delete")}>Delete</button>
                {function() {
                    if (this.state.show_search) return;
                    return <button className="btn btn-default btn-sm pull-right" onClick={this.show_search}><i className="glyphicon glyphicon-search"></i> Search</button>
                }.bind(this)()}
            </div>
            {function() {
                if (!this.state.data) return <Loading/>;
                if (this.state.data.length==0) return <p>There are no items to display.</p>
                return <div>
                    <table className="table table-striped table-hover">
                        <thead>
                            <tr>
                                <th style={{width:10}}><input type="checkbox" checked={this.state.check_all} onClick={this.on_check_all}/></th>
                                {child_els.map(function(el,i) {
                                    if (el.tagName=="field") {
                                        var name=el.getAttribute("name");
                                        var f=this.get_field(this.props.model,name);
                                        return <th key={i}>{f.string}</th>
                                    } else if (el.tagName=="actions") {
                                        return <th key={i}></th>
                                    }
                                }.bind(this))}
                            </tr>
                        </thead>
                        <tbody>
                            {this.state.data.map(function(obj) {
                                return <tr key={obj.id}>
                                    <td><input type="checkbox" onClick={this.on_check.bind(this,obj.id)} checked={this.state.checked_items[obj.id]}/></td>
                                    {child_els.map(function(el,i) {
                                        if (el.tagName=="field") {
                                            var name=el.getAttribute("name");
                                            var f=this.get_field(this.props.model,name);
                                            var val=obj[name];
                                            var val_str=utils.fmt_field_val(val,f);
                                            var edit=el.getAttribute("edit");
                                            return <td key={i} onClick={!edit?this.on_select.bind(this,obj.id):null}>
                                                {function() {
                                                    if (edit) {
                                                        if (f.type=="char") {
                                                            return <FieldChar model={this.props.model} name={name} data={obj} auto_save="1"/>;
                                                        } else if (f.type=="text") {
                                                            return <FieldChar model={this.props.model} name={name} data={obj} auto_save="1"/>;
                                                        } else if (f.type=="boolean") {
                                                            return <FieldChar model={this.props.model} name={name} data={obj} auto_save="1"/>;
                                                        } else if (f.type=="integer") {
                                                            return <FieldChar model={this.props.model} name={name} data={obj} auto_save="1"/>;
                                                        } else if (f.type=="float") {
                                                            return <FieldChar model={this.props.model} name={name} data={obj} auto_save="1"/>;
                                                        } else if (f.type=="decimal") {
                                                            return <FieldChar model={this.props.model} name={name} data={obj} auto_save="1"/>;
                                                        } else if (f.type=="date") {
                                                            return <FieldChar model={this.props.model} name={name} data={obj} auto_save="1"/>;
                                                        } else if (f.type=="datetime") {
                                                            return <FieldChar model={this.props.model} name={name} data={obj} auto_save="1"/>;
                                                        } else if (f.type=="selection") {
                                                            return <FieldChar model={this.props.model} name={name} data={obj} auto_save="1"/>;
                                                        } else if (f.type=="file") {
                                                            return <FieldChar model={this.props.model} name={name} data={obj} auto_save="1"/>;
                                                        } else if (f.type=="many2one") {
                                                            return <FieldMany2One model={this.props.model} name={name} data={obj} auto_save="1" nolink={el.getAttribute("nolink")} width={parseInt(el.getAttribute("width"))}/>;
                                                        } else if (f.type=="reference") {
                                                            return <FieldChar model={this.props.model} name={name} data={obj} auto_save="1"/>;
                                                        } else {
                                                            throw "Invalid field type "+f.type;
                                                        }
                                                    } else {
                                                        return val_str;
                                                    }
                                                }.bind(this)()}
                                            </td>
                                        } else if (el.tagName=="actions") {
                                            var action_els=xpath.select("child::*",el);
                                            return <td key={i}>
                                                <div className="btn-group" style={{whiteSpace:"nowrap"}}>
                                                    {action_els.map((el,i)=>{
                                                        return <button key={i} className="btn btn-default" style={{float:"none",display:"inline-block"}}>
                                                            {function() {
                                                                var icon=el.getAttribute("icon");
                                                                if (!icon) return;
                                                                return <span className={"glyphicon glyphicon-"+icon}></span>
                                                            }.bind(this)()}
                                                            {el.getAttribute("string")}
                                                        </button>
                                                    })}
                                                </div>
                                            </td>
                                        }
                                    }.bind(this))}
                                </tr>
                            }.bind(this))}
                        </tbody>
                    </table>
                    {function() {
                        var num_pages=Math.ceil(this.state.count/this.state.limit);
                        var page_no=Math.floor(this.state.offset/this.state.limit);
                        var pages=[page_no];
                        for (var i=0; i<4; i++) {
                            if (pages.length>=5) break;
                            if (page_no<=num_pages-2-i) pages.push(page_no+1+i);
                            if (pages.length>=5) break;
                            if (page_no>=1+i) pages.unshift(page_no-1-i);
                        }
                        console.log("pages",pages);
                        return <div>
                            <ul className="pagination" style={{float:"right"}}>
                                {function() {
                                    if (page_no<=0) return;
                                    return <li><a className="page-link" href="#" onClick={this.change_page.bind(this,0)}>&laquo; Start</a></li>
                                }.bind(this)()}
                                {function() {
                                    if (page_no<=0) return;
                                    return <li><a className="page-link" href="#" onClick={this.change_page.bind(this,page_no-1)}>&lsaquo; Prev</a></li>
                                }.bind(this)()}
                                {_.range(5).map(function(i) {
                                    if (i>pages.length-1) return; 
                                    return <li key={i} className={pages[i]==page_no?"active":null}><a className="page-link" href="#" onClick={this.change_page.bind(this,pages[i])}>{pages[i]+1}</a></li>
                                }.bind(this))}
                                {function() {
                                    if (page_no>=num_pages-1) return;
                                    return <li><a className="page-link" href="#" onClick={this.change_page.bind(this,page_no+1)}>Next &rsaquo;</a></li>
                                }.bind(this)()}
                                {function() {
                                    if (page_no>=num_pages-1) return;
                                    return <li><a className="page-link" href="#" onClick={this.change_page.bind(this,num_pages-1)}>End &raquo;</a></li>
                                }.bind(this)()}
                            </ul>
                            <div style={{float:"left",margin:"20px 0"}}>
                                <span style={{margin:10}}>
                                    Page
                                    <select style={{margin:5}} onChange={this.change_page} value={page_no} onChange={this.change_page}>
                                        {_.range(num_pages).map(function(i) {
                                            return <option value={i} key={i}>{i+1}</option>
                                        }.bind(this))}
                                    </select>
                                    of {num_pages}
                                </span>
                                <span style={{margin:10}}>({this.state.count} total items)</span>
                                <span style={{margin:10}}>
                                    Showing
                                    <select style={{margin:5}} onChange={this.change_limit} value={this.state.limit}>
                                        <option value={10}>10</option>
                                        <option value={25}>25</option>
                                        <option value={50}>50</option>
                                        <option value={100}>100</option>
                                        <option value={200}>200</option>
                                        <option value={1000}>1000</option>
                                    </select>
                                    items per page
                                </span>
                            </div>
                        </div>
                    }.bind(this)()}
                </div>
            }.bind(this)()}
        </div>
    },

    on_new() {
        if (this.props.on_new) {
            this.props.on_new();
        }
    },

    on_select(active_id) {
        if (this.props.on_select) {
            this.props.on_select(active_id);
        }
    },

    on_check(active_id) {
        var checked=this.state.checked_items;
        if (checked[active_id]) {
            delete checked[active_id];
        } else {
            checked[active_id]=true;
        }
        this.setState({checked_items:checked});
    },

    on_check_all() {
        var checked=this.state.checked_items;
        if (this.state.check_all) {
            this.state.data.forEach(function(obj) {
                checked[obj.id]=false;
            });
            this.setState({checked_items:checked,check_all:false});
        } else {
            this.state.data.forEach(function(obj) {
                checked[obj.id]=true;
            });
            this.setState({checked_items:checked,check_all:true});
        }
    },

    show_search(e) {
        e.preventDefault();
        this.setState({show_search:true});
    },

    hide_search() {
        this.setState({show_search:false,search_cond:null},()=>this.load_data());
    },

    search(cond) {
        this.setState({search_cond:cond},()=>this.load_data());
    },

    click_tab(tab_no,e) {
        console.log("click_tab",tab_no);
        e.preventDefault();
        this.setState({
            active_tab: tab_no,
            group_val: null,
            show_search: false,
            search_cond: null,
        },function() {
            this.load_data();
        }.bind(this));
    },

    click_group_pill(val,e) {
        console.log("click_group_pill",val);
        e.preventDefault();
        if (this.state.group_val==val) {
            new_group_val=null;
        } else {
            new_group_val=val;
        }
        this.setState({
            group_val: new_group_val,
        },function() {
            this.load_data();
        }.bind(this));
    },

    call_method(method,e) {
        e.preventDefault();
        var ctx={};
        var ids=[];
        this.state.data.forEach(function(obj) {
            if (this.state.checked_items[obj.id]) ids.push(obj.id);
        }.bind(this));
        if (ids.length==0) {
            this.setState({"error": "No items selected."});
            return;
        }
        rpc.execute(this.props.model,method,[ids],{context:ctx},function(err,res) {
            if (err) {
                this.setState({"error": err});
                return;
            }
            this.load_data();
        }.bind(this));
    },

    change_limit: function(e) {
        var limit=e.target.value;
        this.setState({limit:limit},function() {
            this.load_data();
        }.bind(this));
    },

    change_page: function(page_no,e) {
        if (!_.isNumber(page_no)) { // XXX
            e=page_no;
            var page_no=e.target.value;
        }
        e.preventDefault();
        var offset=page_no*this.state.limit;
        this.setState({offset:offset},function() {
            this.load_data();
        }.bind(this));
    },
});

var select=function(state) {
    return {
        ui_params: state.ui_params,
    }
}

module.exports=connect(select)(List);
