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
            layout_el: layout_el
        };
    },

    componentDidMount() {
        var cond=[];
        var field_names=null;
        rpc.execute(this.props.model,"search_read",[cond,field_names],{},function(err,data) {
            this.setState({data:data});
        }.bind(this));
    },

    render() {
        var field_els=xpath.select("field",this.state.layout_el);
        var m=this.get_model(this.props.model);
        return <div>
            <div className="page-header">
                <h2>{this.props.title}</h2>
            </div>
            <div style={{marginBottom:10}}>
                <button className="btn btn-default" style={{marginRight:10}} onClick={this.on_new}><span className="glyphicon glyphicon-plus"></span> New {m.string}</button>
                <button className="btn btn-default"><span className="glyphicon glyphicon-download"></span> Import</button>
            </div>
            {function() {
                if (!this.props.tabs) return;
                return <ul className="nav nav-tabs">
                    {this.props.tabs.map(function(o,i) {
                        console.log("i",i);
                        return <li key={i} className={i==0?"active":null}><a href="#">{o[0]}</a></li>
                    }.bind(this))}
                </ul>
            }.bind(this)()}
            <div style={{marginTop:10}}>
                <button className="btn btn-danger btn-sm">Delete</button>
                <button className="btn btn-default btn-sm pull-right" onClick={this.search}><i className="glyphicon glyphicon-search"></i> Search</button>
            </div>
            {function() {
                if (!this.state.data) return <Loading/>;
                if (this.state.data.length==0) return <p>There are no items to display.</p>
                return <table className="table">
                    <thead>
                        <tr>
                            {field_els.map(function(el,i) {
                                var name=el.getAttribute("name");
                                var f=this.get_field(this.props.model,name);
                                return <th key={i}>{f.string}</th>
                            }.bind(this))}
                        </tr>
                    </thead>
                    <tbody>
                        {this.state.data.map(function(obj) {
                            return <tr key={obj.id} onClick={this.on_select.bind(this,obj.id)}>
                                {field_els.map(function(el,i) {
                                    var name=el.getAttribute("name");
                                    var f=this.get_field(this.props.model,name);
                                    var val=obj[name];
                                    return <td key={i}>{utils.fmt_field_val(val,f)}</td>
                                }.bind(this))}
                            </tr>
                        }.bind(this))}
                    </tbody>
                </table>
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

    search(e) {
        e.preventDefault();
    },
});

var select=function(state) {
    return {
        ui_params: state.ui_params,
    }
}

module.exports=connect(select)(List);
