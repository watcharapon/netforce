React = require("react");
var ui_params=require("../ui_params");
var utils=require("../utils");
var rpc=require("../rpc");
var dom = require('xmldom').DOMParser;
var xpath = require('xpath');
var Loading=require("./loading")
var RelatedForm=require("./related_form")

var RelatedO2M=React.createClass({
    getInitialState() {
        var f=ui_params.get_field(this.props.model,this.props.name);
        if (this.props.list_layout_el) {
            this.list_layout_el=this.props.list_layout_el;
        } else {
            layout=ui_params.find_layout({model:f.relation,type:"list"});
            if (!layout) throw "List layout not found for model "+f.relation;
            var doc=new dom().parseFromString(layout.layout);
            this.list_layout_el=doc.documentElement;
        }
        return {};
    },

    componentDidMount() {
        this.load_data();
    },

    load_data: function() {
        var f=ui_params.get_field(this.props.model,this.props.name);
        var fr=ui_params.get_field(f.relation,f.relfield);
        var cond;
        if (fr.type=="many2one") {
            cond=[[f.relfield,"=",this.props.active_id]];
        } else if (fr.type=="reference") {
            cond=[[f.relfield,"=",this.props.model+","+this.props.active_id]];
        } else {
            throw "Invalid related field type: "+fr.type;
        }
        var field_els=xpath.select("field", this.list_layout_el);
        var field_names=field_els.map(function(el) {
            var name=el.getAttribute("name");
            return name;
        });
        var ctx={};
        rpc.execute(f.relation,"search_read",[cond,field_names],{context:ctx},function(err,res) {
            if (err) throw err;
            this.setState({data:res});
        }.bind(this));
    },

    render() {
        var field_els=xpath.select("field", this.list_layout_el);
        var f=ui_params.get_field(this.props.model,this.props.name);
        var relation=f.relation;
        return <div>
            <h3>{f.string}</h3>
            {function() {
                if (this.state.show_form) {
                    return <RelatedForm model={f.relation} relfield={f.relfield} parent_model={this.props.model} parent_id={this.props.active_id} on_save={this.on_save} on_cancel={this.on_cancel}/>
                } else {
                    return <div className="btn-toolbar">
                        <button className="btn btn-sm btn-default" onClick={this.click_add}>Add</button>
                        <button className="btn btn-sm btn-default" onClick={this.click_delete}>Delete</button>
                    </div>
                }
            }.bind(this)()}
            {function() {
                if (!this.state.data) return <Loading/>
                return <table className="table">
                    <thead>
                        <tr>
                            {field_els.map(function(el,i) {
                                var name=el.getAttribute("name");
                                var f=ui_params.get_field(relation,name);
                                return <th key={i}>{f.string}</th>
                            }.bind(this))}
                        </tr>
                    </thead>
                    <tbody>
                        {this.state.data.map(function(obj,i) {
                            return <tr key={i}>
                                {field_els.map(function(el,i) {
                                    var name=el.getAttribute("name");
                                    var f=ui_params.get_field(relation,name);
                                    var val=obj[name];
                                    var val_str=utils.fmt_field_val(val,f);
                                    return <td key={i}>{val_str}</td>
                                }.bind(this))}
                            </tr>
                        }.bind(this))}
                    </tbody>
                </table>
            }.bind(this)()}
        </div>
    },

    click_add: function() {
        this.setState({show_form:true});
    },

    click_delete: function() {
    },

    on_save: function() {
        this.setState({show_form:false});
        this.load_data();
    },

    on_cancel: function() {
        this.setState({show_form:false});
    },
});

module.exports=RelatedO2M;
