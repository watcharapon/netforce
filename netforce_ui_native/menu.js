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

var RPC=require("./RPC");
var utils=require("./utils");

var Button=require("./button");

class Menu extends Component {
    constructor(props) {
        super(props);
        this.state = {};
    }

    componentDidMount() {
        AsyncStorage.getItem("login",(err,login)=>{
            this.setState({login});
        });
    }

  render() {
    var actions=[
        {title: "Logout"},
    ];
    return <View>
        {function() {
            if (!this.state.login) return;
            return <View style={{padding:10}}>
                <Text>Welcome, {this.state.login}.</Text>
            </View>
        }.bind(this)()}
        <View style={{paddingTop:10}}>
            <Button onPress={this.click_link.bind(this,{name:"times"})}>
                <View style={{height:50,alignItems:"center",justifyContent:"center",backgroundColor:"#aaa"}}>
                    <Text style={{color:"#fff"}}>Work Time</Text>
                </View>
            </Button>
        </View>
        <View style={{paddingTop:10}}>
            <Button onPress={this.click_link.bind(this,{name:"settings"})}>
                <View style={{height:50,alignItems:"center",justifyContent:"center",backgroundColor:"#aaa"}}>
                    <Text style={{color:"#fff"}}>Settings</Text>
                </View>
            </Button>
        </View>
    </View>
  }

  click_link(action) {
      this.props.navigator.push(action);
  }

  action_selected(pos) {
    AsyncStorage.setItem("user_id",null);
    AsyncStorage.setItem("login",null);
    if (pos==0) {
        this.click_link({name:"login"});
    }
  }
}

module.exports=Menu;
