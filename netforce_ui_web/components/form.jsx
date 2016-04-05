React = require("react");
var connect = require("react-redux").connect;
var actions=require("../actions")
var ui_params=require("../ui_params");
var dom = require('xmldom').DOMParser;
var xpath = require('xpath');
var Loading=require("./loading")
var classNames = require('classnames');

var Form=React.createClass({
    mixins: [ui_params],

    getInitialState() {
        var layout=this.find_layout({model:this.props.model,type:"form"});
        if (!layout) throw "Form layout not found for model "+this.props.model;
        var doc=new dom().parseFromString(layout.layout);
        var layout_el=doc.documentElement;
        return {
            layout_el: layout_el
        };
    },

    componentDidMount() {
        var field_names=null;
        if (this.props.active_id) {
            rpc.execute(this.props.model,"read",[[this.props.active_id],field_names],{},function(err,data) {
                this.setState({data:data[0]});
            }.bind(this));
        } else {
            rpc.execute(this.props.model,"default_get",[field_names],{},function(err,data) {
                this.setState({data:data});
            }.bind(this));
        }
    },

    render() {
        var title;
        var m=this.get_model(this.props.model);
        if (this.props.active_id) {
            title="Edit "+m.string;
        } else {
            title="New "+m.string;
        }
        return <div>
            {function() {
                if (!this.props.bread_title) return;
                return <ol className="breadcrumb">
                    <li><a href="#" onClick={this.on_bread}>{this.props.bread_title}</a></li>
                </ol>
            }.bind(this)()}
            <div className="page-header">
                <h2>{title}</h2>
            </div>
            {function() {
                if (!this.state.data) return <Loading/>;
                return <form className="form-horizontal">
                    <div className="row">
                        <div className="col-sm-6">
                            <div className="form-group">
                                <label className="control-label col-sm-4">AAA</label>
                                <div className="col-sm-8">
                                    <input type="text" className="form-control"/>
                                </div>
                            </div>
                        </div>
                        <div className="col-sm-6">
                            <div className="form-group">
                                <label className="control-label col-sm-4">BBB</label>
                                <div className="col-sm-8">
                                    <input type="text" className="form-control"/>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div>
                        <button className="btn btn-primary btn-lg">Save</button>
                    </div>
                </form>
            }.bind(this)()}
        </div>
    },

    on_bread(e) {
        e.preventDefault();
        if (this.props.on_bread) {
            this.props.on_bread();
        }
    }
});

var select=function(state) {
    return {
        ui_params: state.ui_params,
    }
}

module.exports=connect(select)(Form);
