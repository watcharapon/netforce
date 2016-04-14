React = require("react");
var connect = require("react-redux").connect;
var actions=require("../actions")
var ui_params=require("../ui_params");
var rpc=require("../rpc");
var dom = require('xmldom').DOMParser;
var xpath = require('xpath');
var Loading=require("./loading")
var classNames = require('classnames');
var FieldChar=require("./field_char");
var FieldDecimal=require("./field_decimal");
var FieldSelect=require("./field_select");
var FieldMany2One=require("./field_many2one");
var FieldOne2Many=require("./field_one2many");
var Group=require("./group");
var Tabs=require("./tabs");

var FormLayout=React.createClass({
    mixins: [ui_params],

    getInitialState() {
        console.log("FormLayout.getInitialState");
        return {};
    },

    componentDidMount() {
        console.log("FormLayout.componentDidMount");
    },

    render() {
        console.log("FormLayout.render");
        var child_els=xpath.select("child::*", this.props.layout_el);
        var cols=[];
        var rows=[];
        child_els.forEach(function(el,i) {
            var invisible=el.getAttribute("invisible");
            if (invisible) return;
            if (el.tagName=="field") {
                var name=el.getAttribute("name");
                var f=this.get_field(this.props.model,name);
                if (f.type=="char") {
                    var field_component=<FieldChar model={this.props.model} name={name} data={this.props.data}/>;
                } else if (f.type=="text") {
                    var field_component=<FieldChar model={this.props.model} name={name} data={this.props.data}/>;
                } else if (f.type=="boolean") {
                    var field_component=<FieldChar model={this.props.model} name={name} data={this.props.data}/>;
                } else if (f.type=="integer") {
                    var field_component=<FieldChar model={this.props.model} name={name} data={this.props.data}/>;
                } else if (f.type=="float") {
                    var field_component=<FieldChar model={this.props.model} name={name} data={this.props.data}/>;
                } else if (f.type=="decimal") {
                    var field_component=<FieldChar model={this.props.model} name={name} data={this.props.data}/>;
                } else if (f.type=="date") {
                    var field_component=<FieldChar model={this.props.model} name={name} data={this.props.data}/>;
                } else if (f.type=="datetime") {
                    var field_component=<FieldChar model={this.props.model} name={name} data={this.props.data}/>;
                } else if (f.type=="selection") {
                    var field_component=<FieldSelect model={this.props.model} name={name} data={this.props.data}/>;
                } else if (f.type=="file") {
                    var field_component=<FieldChar model={this.props.model} name={name} data={this.props.data}/>;
                } else if (f.type=="many2one") {
                    var field_component=<FieldMany2One model={this.props.model} name={name} data={this.props.data}/>;
                } else if (f.type=="reference") {
                    var field_component=<FieldChar model={this.props.model} name={name} data={this.props.data}/>;
                } else if (f.type=="one2many") {
                    var res=xpath.select("list",el);
                    var list_layout_el=res.length>0?res[0]:null;
                    var field_component=<FieldOne2Many model={this.props.model} name={name} data={this.props.data} list_layout_el={list_layout_el}/>;
                } else {
                    throw "Invalid field type: "+f.type;
                }
                var col=<div key={cols.length} className="col-sm-6">
                    <div className="form-group">
                        <label className="control-label col-sm-4">{f.string}</label>
                        <div className="col-sm-8">
                            {field_component}
                        </div>
                    </div>
                </div>
                cols.push(col);
            } else if (el.tagName=="newline") {
            } else if (el.tagName=="separator") {
            } else if (el.tagName=="button") {
            } else if (el.tagName=="group") {
                var col=<div key={cols.length} className="col-sm-12">
                    <Group model={this.props.model} layout_el={el} data={this.props.data}/>
                </div>
                cols.push(col);
            } else if (el.tagName=="tabs") {
                var col=<div key={cols.length} className="col-sm-12">
                    <Tabs model={this.props.model} layout_el={el} data={this.props.data}/>
                </div>
                cols.push(col);
            } else if (el.tagName=="head") {
            } else if (el.tagName=="foot") {
            } else if (el.tagName=="related") {
            } else {
                throw "Unexpected tag name: "+el.tagName;
            }
        }.bind(this));
        rows.push(<div key={rows.length} className="row">{cols}</div>);
        return <div>
            {rows}
        </div>
    },
});

var select=function(state) {
    return {
        ui_params: state.ui_params,
    }
}

module.exports=connect(select)(FormLayout);
