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
  ScrollView,
  View
} from 'react-native';

var xpath = require('xpath');
var dom = require('xmldom').DOMParser;

var rpc=require("./rpc");
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
var FieldOne2Many=require("./field_one2many");

class Form extends Component {
    constructor(props) {
        super(props);
        this.state = {};
    }

    componentDidMount() {
        var layout_name=this.props.layout||"work_time_form_mobile";
        var layout=UIParams.get_layout(layout_name);
        this.layout_doc=new dom().parseFromString(layout.layout);
        this.load_data();
    }

    load_data() {
        console.log("Form.load_data");
        var cond=this.props.condition||[];
        var root_el=this.layout_doc.documentElement;
        var field_nodes=xpath.select("field", root_el);
        var fields=[];
        field_nodes.forEach(function(el) {
            fields.push(el.getAttribute("name"));
        });
        console.log("fields",fields);
        //alert("fields "+JSON.stringify(fields))
        var ctx={};
        if (this.props.context) {
            if (typeof(this.props.context)=="string") {
                ctx=JSON.parse(this.props.context);
            } else if (typeof(this.props.context)=="object") {
                ctx=this.props.context;
            }
        }
        if (this.props.active_id) {
            rpc.execute(this.props.model,"read",[[this.props.active_id],fields],{context:ctx},function(err,res) {
                if (err) {
                    alert("ERROR: "+err);
                    return;
                }
                var data=res[0];
                data._orig_data=Object.assign({},data);
                this.setState({
                    data: data,
                });
            }.bind(this));
        } else {
            rpc.execute(this.props.model,"default_get",[fields],{context:ctx},function(err,res) {
                if (err) {
                    alert("ERROR: "+err);
                    return;
                }
                var data=res;
                data._orig_data=Object.assign({},data);
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
                } else if (f.type=="one2many") {
                    var res=xpath.select("list",el);
                    var list_layout_el=res.length>0?res[0]:null;
                    var res=xpath.select("form",el);
                    var form_layout_el=res.length>0?res[0]:null;
                    field_component=<FieldOne2Many navigator={this.props.navigator} model={this.props.model} name={name} data={this.state.data} list_layout_el={list_layout_el} form_layout_el={form_layout_el}/>
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
        return <ScrollView style={{flex:1}}>
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
        </ScrollView>
    }

    get_change_vals(data,model) {
        console.log("get_change_vals");
        var change={};
        for (var name in data) {
            if (name=="id") continue;
            if (name=="_orig_data") continue;
            var v=data[name];
            var orig_v;
            if (data.id) {
                if (!data._orig_data) throw "Missing _orig_data";
                orig_v=data._orig_data[name];
            } else {
                orig_v=null;
            }
            var f=UIParams.get_field(model,name);
            if (f.type=="char") {
                if (v!=orig_v) change[name]=v;
            } else if (f.type=="text") {
                if (v!=orig_v) change[name]=v;
            } else if (f.type=="integer") {
                if (v!=orig_v) change[name]=v;
            } else if (f.type=="float") {
                if (v!=orig_v) change[name]=v;
            } else if (f.type=="decimal") {
                if (v!=orig_v) change[name]=v;
            } else if (f.type=="select") {
                if (v!=orig_v) change[name]=v;
            } else if (f.type=="many2one") {
                var v1=v?v[0]:null;
                var v2=orig_v?orig_v[0]:null;
                if (v1!=v2) change[name]=v1;
            } else if (f.type=="one2many") {
                if (orig_v==null) orig_v=[];
                var ops=[];
                var new_ids={};
                v.forEach(function(rdata) {
                    if (typeof(rdata)!="object") throw "Invalid O2M data";
                    var rchange=this.get_change_vals(rdata,f.relation);
                    if (Object.keys(rchange).length>0) {
                        if (rdata.id) {
                            ops.push(["write",[rdata.id],rchange]);
                        } else {
                            ops.push(["create",rchange]);
                        }
                    }
                    if (rdata.id) new_ids[rdata.id]=true;
                }.bind(this));
                var del_ids=[];
                orig_v.forEach(function(id) {
                    if (!new_ids[id]) del_ids.push(id);
                }.bind(this));
                if (del_ids.length>0) ops.push(["delete",del_ids]);
                if (ops.length>0) change[name]=ops;
            }
        }
        return change;
    }

    press_save() {
        var vals=this.get_change_vals(this.state.data,this.props.model);
        //alert("vals "+JSON.stringify(vals));
        if (Object.keys(vals).length==0) {
            alert("There are no changes to save.");
            return;
        }
        var ctx={};
        if (this.props.context) {
            if (typeof(this.props.context)=="string") {
                ctx=JSON.parse(this.props.context);
            } else if (typeof(this.props.context)=="object") {
                ctx=this.props.context;
            }
        }
        if (this.props.active_id) {
            rpc.execute(this.props.model,"write",[[this.props.active_id],vals],{context:ctx},function(err,new_id) {
                if (err) {
                    alert("ERROR: "+err.message);
                    return;
                }
                this.back_reload();
            }.bind(this));
        } else {
            rpc.execute(this.props.model,"create",[vals],{context:ctx},function(err,new_id) {
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
        rpc.execute(this.props.model,"delete",[[this.props.active_id]],{context:ctx},function(err) {
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
