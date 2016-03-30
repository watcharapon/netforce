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

var RPC=require("./RPC");
var Button=require("./button");

class Login extends Component {
    constructor(props) {
        super(props);
        this.state = {login:"",password:"",dbname:null};
    }

  render() {
    return <View>
        <Text>
            Database:
        </Text>
        <Picker selectedValue={this.state.dbname} onValueChange={(dbname) => this.setState({dbname})}> 
            <Picker.Item label="test1" value="test1"/>
            <Picker.Item label="test2" value="test2"/>
        </Picker>
        <Text>
            Username:
        </Text>
        <TextInput style={{height:40, borderColor: 'gray', borderWidth: 1}} value={this.state.login} onChangeText={(login)=>this.setState({login})}/>
        <Text>
            Password:
        </Text>
        <TextInput style={{height:40, borderColor: 'gray', borderWidth: 1}} secureTextEntry={true} value={this.state.password} onChangeText={(password)=>this.setState({password})}/>
        <View style={{paddingTop:5}}>
            <Button onPress={this.login.bind(this)}>
                <View style={{height:50,backgroundColor:"#37b",alignItems:"center",justifyContent:"center"}}>
                    <Text style={{color:"#fff"}}>Login</Text>
                </View>
            </Button>
        </View>
    </View>
  }

  login() {
      try {
        if (!this.state.login) throw "Missing login"; 
        if (!this.state.password) throw "Missing password"; 
      } catch (e) {
          alert("Error: "+e);
          return;
      }
      this.props.navigator.push({
          name: "menu",
      });
  }

  click_link(action) {
      this.props.navigator.push(action);
  }
}

module.exports=Login;
