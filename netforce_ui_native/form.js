/**
 * Sample React Native App
 * https://github.com/facebook/react-native
 */
'use strict';
import React, {
  AppRegistry,
  Component,
  StyleSheet,
  Text,
  TextInput,
  Navigator,
  AsyncStorage,
  View
} from 'react-native';

var xpath = require('xpath');
var dom = require('xmldom').DOMParser;

var RPC=require("./RPC");
var Button=require("./button");
var UIParams=require("./ui_params");
var utils=require("./utils");

var Icon = require('react-native-vector-icons/FontAwesome');

var FieldChar=require("./field_char");
var FieldText=require("./field_text");
var FieldFloat=require("./field_float");
var FieldDecimal=require("./field_decimal");
var FieldInteger=require("./field_integer");
var FieldDate=require("./field_date");
var FieldDateTime=require("./field_datetime");
var FieldSelect=require("./field_select");
var FieldMany2One=require("./field_many2one");

class Form extends Component {
    constructor(props) {
        super(props);
        this.state = {};
    }

    componentDidMount() {
        var layout=UIParams.get_layout("work_time_form_mobile");
        this.layout_doc=new dom().parseFromString(layout.layout);
        this.load_data();
    }

    load_data() {
        console.log("Form.load_data");
        var cond=this.props.condition||[];
        var field_nodes=xpath.select("//field", this.layout_doc);
        var fields=[];
        field_nodes.forEach(function(el) {
            fields.push(el.getAttribute("name"));
        });
        console.log("fields",fields);
        if (this.props.active_id) {
            RPC.execute(this.props.model,"read",[[this.props.active_id],fields],{},function(err,data) {
                if (err) {
                    alert("ERROR: "+err);
                    return;
                }
                this.setState({
                    data: data[0],
                });
            }.bind(this));
        } else {
            RPC.execute(this.props.model,"default_get",[fields],{},function(err,data) {
                if (err) {
                    alert("ERROR: "+err);
                    return;
                }
                this.setState({
                    data: data,
                });
            }.bind(this));
        }
    }

    render() {
        if (!this.state.data) return <Text>Loading...</Text>
        var root=this.layout_doc.documentElement;
        var child_els=xpath.select("child::*", root);
        var cols=[];
        var rows=[];
        {child_els.forEach(function(el,i) {
            if (el.tagName=="newline") {
                rows.push(<View style={{flexDirection:"row", justifyContent: "space-between"}} key={rows.length}>{cols}</View>);
                cols=[];
                return;
            } else if (el.tagName=="field") {
                var name=el.getAttribute("name");
                var f=UIParams.get_field(this.props.model,name);
                var invisible=el.getAttribute("invisible");
                if (invisible) return;
                var val=this.state.data[name];
                var val_str=utils.field_val_to_str(val,f);
                var field_component;
                if (f.type=="char") {
                    field_component=<FieldChar model={this.props.model} name={name} data={this.state.data}/>
                } else if (f.type=="text") {
                    field_component=<FieldText model={this.props.model} name={name} data={this.state.data}/>
                } else if (f.type=="float") {
                    field_component=<FieldFloat model={this.props.model} name={name} data={this.state.data}/>
                } else if (f.type=="decimal") {
                    field_component=<FieldDecimal model={this.props.model} name={name} data={this.state.data}/>
                } else if (f.type=="integer") {
                    field_component=<FieldInteger model={this.props.model} name={name} data={this.state.data}/>
                } else if (f.type=="date") {
                    field_component=<FieldDate model={this.props.model} name={name} data={this.state.data}/>
                } else if (f.type=="datetime") {
                    field_component=<FieldDateTime model={this.props.model} name={name} data={this.state.data}/>
                } else if (f.type=="selection") {
                    field_component=<FieldSelect model={this.props.model} name={name} data={this.state.data}/>
                } else if (f.type=="many2one") {
                    field_component=<FieldMany2One navigator={this.props.navigator} model={this.props.model} name={name} data={this.state.data}/>
                } else {
                    throw "Invalid field type: "+f.type;
                }
                var col=<View key={cols.length} style={{flexDirection:"column",flex:1}}>
                    <Text style={{fontWeight:"bold",marginRight:5}}>{f.string}</Text>
                    {field_component}
                </View>;
                cols.push(col);
            } else {
                throw "Invalid tag name: "+el.tagName;
            }
        }.bind(this))}
        rows.push(<View style={{flexDirection:"row", justifyContent: "space-between"}} key={rows.length}>{cols}</View>);
        return <View style={{flex:1}}>
            <View>
                {rows}
            </View>
            <View style={{paddingTop:5,marginTop:20}}>
                <Button onPress={this.press_save.bind(this)}>
                    <View style={{height:50,backgroundColor:"#37b",alignItems:"center",justifyContent:"center"}}>
                        <Text style={{color:"#fff"}}><Icon name="check" size={16} color="#eee"/> Save</Text>
                    </View>
                </Button>
            </View>
            {function() {
                if (!this.props.active_id) return;
                return <View style={{paddingTop:5}}>
                    <Button onPress={this.press_delete.bind(this)}>
                        <View style={{height:50,backgroundColor:"#c33",alignItems:"center",justifyContent:"center"}}>
                            <Text style={{color:"#fff"}}>Delete</Text>
                        </View>
                    </Button>
                </View>
            }.bind(this)()}
        </View>
    }

    get_change_vals() {
        console.log("get_change_vals");
        var vals={};
        for (var name in this.state.data) {
            if (name=="id") continue;
            var v=this.state.data[name];
            var f=UIParams.get_field(this.props.model,name);
            if (v!=null) {
                if (f.type=="many2one") {
                    v=v[0];
                }
            }
            vals[name]=v;
        }
        return vals;
    }

    press_save() {
        var vals=this.get_change_vals();
        var ctx={};
        if (this.props.active_id) {
            RPC.execute(this.props.model,"write",[[this.props.active_id],vals],{context:ctx},function(err,new_id) {
                if (err) {
                    alert("ERROR: "+err.message);
                    return;
                }
                this.back_reload();
            }.bind(this));
        } else {
            RPC.execute(this.props.model,"create",[vals],{context:ctx},function(err,new_id) {
                if (err) {
                    alert("ERROR: "+err.message);
                    return;
                }
                this.back_reload();
            }.bind(this));
        }
    }

    press_delete() {
        // TODO: add confirm
        var ctx={};
        RPC.execute(this.props.model,"delete",[[this.props.active_id]],{context:ctx},function(err) {
            if (err) {
                alert("ERROR: "+err.message);
                return;
            }
            this.back_reload();
        }.bind(this));
    }

    back_reload() {
        var routes=this.props.navigator.getCurrentRoutes();
        var route=routes[routes.length-2];
        if (route==null) route={name:"login"};
        route=Object.assign({},route);
        this.props.navigator.replacePrevious(route);
        this.props.navigator.pop();
    }
}

module.exports=Form;
