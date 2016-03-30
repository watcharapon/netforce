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
  AsyncStorage,
  View
} from 'react-native';

var cheerio=require("cheerio");

var RPC=require("./RPC");
var utils=require("./utils");
var Button=require("./button");
var UIParams=require("./ui_params");

class Menu extends Component {
    constructor(props) {
        super(props);
        this.state = {};
    }

    componentDidMount() {
    }

  render() {
      var layout=UIParams.get_layout(this.props.layout);
      var $layout=cheerio.load(layout.layout);
    return <View>
        <View style={{paddingTop:10}}>
            <Button onPress={this.click_link.bind(this,{name:"settings"})}>
                <View style={{height:50,alignItems:"center",justifyContent:"center",backgroundColor:"#aaa"}}>
                    <Text style={{color:"#fff"}}>Settings</Text>
                </View>
            </Button>
        </View>
    </View>
  }
}

module.exports=Menu;
