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
  ToolbarAndroid,
  TouchableNativeFeedback,
  Navigator,
  AsyncStorage,
  View
} from 'react-native';

var RPC=require("./RPC");
var Button=require("./button");

class Form extends Component {
    constructor(props) {
        super(props);
        this.state = {login:"",password:""};
    }

  render() {
    var actions=[
        {title: "Login"},
    ];
    return <View>
        <Text>
            Username:
        </Text>
        <TextInput style={{height:40, borderColor: 'gray', borderWidth: 1}} value={this.state.login} onChangeText={(login)=>this.setState({login})}/>
        <Text>
            Password:
        </Text>
        <TextInput style={{height:40, borderColor: 'gray', borderWidth: 1}} secureTextEntry={true} value={this.state.password} onChangeText={(password)=>this.setState({password})}/>
        <Text>
            Confirm Password:
        </Text>
        <TextInput style={{height:40, borderColor: 'gray', borderWidth: 1}} secureTextEntry={true} value={this.state.confirm_password} onChangeText={(confirm_password)=>this.setState({confirm_password})}/>
        <View style={{paddingTop:5}}>
            <Button onPress={this.sign_up.bind(this)}>
                <View style={{height:50,backgroundColor:"#37b",alignItems:"center",justifyContent:"center"}}>
                    <Text style={{color:"#fff"}}>Sign Up</Text>
                </View>
            </Button>
        </View>
    </View>
  }

  sign_up() {
      try {
        if (!this.state.login) throw "Missing login"; 
        if (!this.state.password) throw "Missing password"; 
        if (this.state.confirm_password!=this.state.password) throw "Passwords not the same"; 
      } catch (e) {
          alert("Error: "+e);
          return;
      }
      RPC.execute("ds.interface","sign_up",[this.state.login,this.state.password],{},function(err,user_id) {
          if (err) {
              alert("Error: "+err.message);
              return;
          }
          AsyncStorage.setItem("user_id",""+user_id);
          AsyncStorage.setItem("login",this.state.login);
          this.props.navigator.push({
              name: "menu",
          });
      }.bind(this));
  }

  click_link(action) {
      this.props.navigator.push(action);
  }

  action_selected(pos) {
      if (pos==0) {
        this.click_link({name:"login"});
      }
  }
}

module.exports=Form;
