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
  NativeModules,
  TouchableOpacity,
  View
} from 'react-native';

var UIParams=require("./ui_params");
var utils=require("./utils");
var moment=require("moment");

class FieldDate extends Component {
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
        var val_str=this.state.value;
        return <TouchableOpacity onPress={this.on_press.bind(this)} style={{borderBottomWidth:0.5,height:40}}>
            <Text>{val_str}</Text>
        </TouchableOpacity>
    }

    on_press() {
        NativeModules.DateAndroid.showDatepickerWithInitialDateInMilliseconds(""+moment(this.state.value).unix()*1000,function() {}, function(y,m,d) {
            var val=moment([y,m,d]).format("YYYY-MM-DD");
            this.setState({value:val});
            this.props.data[this.props.name]=val;
        }.bind(this));
    }
}

module.exports=FieldDate;
