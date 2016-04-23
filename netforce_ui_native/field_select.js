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
        if (this.props.selection) {
            this.selection=this.props.selection;
        } else {
            var f=UIParams.get_field(this.props.model,this.props.name);
            this.selection=f.selection;
        }
        this.state = {};
    }

    componentDidMount() {
        var val=this.props.data[this.props.name];
        this.setState({value:val});
    }

    load_data() {
    }

    render() {
        var items=[null].concat(this.selection);
        return <Picker selectedValue={this.state.value} onValueChange={this.onchange.bind(this)} style={{height:40}}>
            {items.map(function(o,i) {
                return <Picker.Item label={o?o[1]:""} value={o?o[0]:null} key={i}/>
            }.bind(this))}
        </Picker>
    }

    onchange(val) {
        this.setState({value:val});
        this.props.data[this.props.name]=val;
    }
}

module.exports=FieldSelect;
