'use strict';
import React, {
  AppRegistry,
  Component,
  StyleSheet,
  Text,
  TextInput,
  Picker,
  AsyncStorage,
  View
} from 'react-native';

var RPC=require("./RPC");
var Button=require("./button");

class Login extends Component {
    constructor(props) {
        super(props);
        this.state = {login:"",password:"",dbname:null,db_list:[]};
    }

    componentDidMount() {
        AsyncStorage.getItem("db_list",function(err,res) {
            var db_list=JSON.parse(res)||[];
            this.setState({db_list:db_list});
        }.bind(this));
    }

    render() {
        return <View>
            <Text>
                Database:
            </Text>
            <Picker selectedValue={this.state.dbname} onValueChange={(dbname) => this.setState({dbname})}> 
                {this.state.db_list.map(function(obj,i) {
                    return <Picker.Item label={obj.dbname} value={obj.dbname} key={i}/>
                }.bind(this))}
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
            <View style={{paddingTop:5}}>
                <Button onPress={this.manage_db.bind(this)}>
                    <View style={{height:50,backgroundColor:"#ccc",alignItems:"center",justifyContent:"center"}}>
                        <Text style={{color:"#fff"}}>Manage Databases</Text>
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

  manage_db() {
      this.props.navigator.push({name:"db_list"});
  }

  click_link(action) {
      this.props.navigator.push(action);
  }
}

module.exports=Login;
