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
  TouchableOpacity,
  Picker,
  View
} from 'react-native';

var UIParams=require("./ui_params");
var utils=require("./utils");
var rpc=require("./rpc");
var Icon = require('react-native-vector-icons/FontAwesome');
var _=require("underscore");

class FieldMany2One extends Component {
    constructor(props) {
        super(props);
        this.state = {};
    }

    componentDidMount() {
        var val=this.props.data[this.props.name];
        this.setState({value:val});
        if (this.props.select) this.load_items();
    }

    load_items() {
        var ctx={};
        rpc.execute(this.props.relation,"name_search",[""],{context:ctx},(err,data)=>{
            if (err) {
                alert("Error: "+err);
                return;
            }
            this.setState({items:data});
        });
    }

    render() {
        var val=this.state.value;
        var val_str=val?val[1]:null;
        var val_id=val?val[0]:null;
        if (this.props.select) {
            if (!this.state.items) return <Text>Loading...</Text>
            var items=[null].concat(this.state.items);
            return <Picker selectedValue={val_id} onValueChange={this.select_item.bind(this)}>
                    {items.map((obj,i)=>{
                        return <Picker.Item key={i} label={obj?obj[1]:""} value={obj?obj[0]:null}/>
                    })}
            </Picker>
        } else {
            return <View style={{flexDirection:"row",borderBottomWidth:0.5,marginBottom:5,height:40}}>
                <TouchableOpacity style={{flex:1}} onPress={this.search.bind(this)}>
                    <Text style={{flex:1}}>{val_str}</Text>
                </TouchableOpacity>
                <TouchableOpacity style={{padding:5}} onPress={this.clear.bind(this)}><Icon name="remove" size={16} color="#333"/></TouchableOpacity>
            </View>
        }
    }

    search() {
        var f=UIParams.get_field(this.props.model,this.props.name);
        this.props.navigator.push({name:"search_m2o",model:f.relation,on_select:this.on_select.bind(this)});
    }

    clear() {
        this.setState({value:null});
    }

    on_select(val) {
        this.setState({value:val});
        this.props.data[this.props.name]=val;
    }

    select_item(val_id,pos) {
        console.log("select_item",val_id);
        var val;
        if (val_id) {
            val=_.find(this.state.items,function(obj) {return obj[0]==val_id});
            if (!val) throw "Item not found";
        } else {
            val=null;
        }
        console.log("val",val);
        this.setState({value:val});
        this.props.data[this.props.name]=val;
    }
}

module.exports=FieldMany2One;
