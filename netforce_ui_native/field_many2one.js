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
  View
} from 'react-native';

var UIParams=require("./ui_params");
var utils=require("./utils");
var Icon = require('react-native-vector-icons/FontAwesome');

class FieldMany2One extends Component {
    constructor(props) {
        super(props);
        this.state = {};
    }

    componentDidMount() {
        var val=this.props.data[this.props.name];
        this.setState({value:val});
    }

    load_data() {
    }

    render() {
        var f=UIParams.get_field(this.props.model,this.props.name);
        var val_str=utils.field_val_to_str(this.state.value,f);
        return <View style={{flexDirection:"row",borderBottomWidth:0.5,marginBottom:5,height:40}}>
            <TouchableOpacity style={{flex:1}} onPress={this.search.bind(this)}>
                <Text style={{flex:1}}>{val_str}</Text>
            </TouchableOpacity>
            <TouchableOpacity style={{padding:5}} onPress={this.clear.bind(this)}><Icon name="remove" size={16} color="#333"/></TouchableOpacity>
        </View>
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
}

module.exports=FieldMany2One;
