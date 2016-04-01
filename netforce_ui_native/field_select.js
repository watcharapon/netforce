/**
 * Sample React Native App
 * https://github.com/facebook/react-native
 */
'use strict';
import React, {
  AppRegistry,
  Component,
  StyleSheet,
  TextInput,
  Picker,
  View
} from 'react-native';

var UIParams=require("./ui_params");
var utils=require("./utils");

class FieldSelect extends Component {
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
        return <Picker selectedValue={this.state.value} onValueChange={this.onchange.bind(this)} style={{height:40}}>
            {f.selection.map(function(o,i) {
                return <Picker.Item label={o[1]} value={o[0]} key={i}/>
            }.bind(this))}
        </Picker>
    }

    onchange(val) {
        this.setState({value:val});
        this.props.data[this.props.name]=val;
    }
}

module.exports=FieldSelect;
