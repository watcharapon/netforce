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

var rpc=require("./rpc");
var Button=require("./button");
var ui_params=require("./ui_params");

class Login extends Component {
    constructor(props) {
        super(props);
        this.state = {login:"",password:"",dbname:null,db_list:[],loading:true};
    }

    componentDidMount() {
        AsyncStorage.getItem("db_list",function(err,res) {
            var db_list=JSON.parse(res)||[];
            var dbname=db_list.length>0?db_list[0].dbname:null;
            this.setState({db_list:db_list,dbname:dbname});
        }.bind(this));
        AsyncStorage.getItem("base_url",function(err,res) {
            if (!res) {
                this.setState({loading:false});
                return;
            }
            rpc.set_base_url(res);
            AsyncStorage.getItem("user_id",function(err,res) {
                if (!res) {
                    this.setState({loading:false});
                    return;
                }
                ui_params.load_ui_params_local(function(err) {
                    if (!res) {
                        this.setState({loading:false});
                        return;
                    }
                    var login_action={name:"action",action:"main_menu_mobile"};
                    this.props.navigator.replace(login_action);
                });
            }.bind(this));
        }.bind(this));
    }

    render() {
        if (this.state.loading) return <Text>Loading...</Text>
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
            if (!this.state.dbname) throw "Missing database"; 
            if (!this.state.login) throw "Missing login"; 
            if (!this.state.password) throw "Missing password"; 
        } catch (e) {
            alert("Error: "+e);
            return;
        }
        AsyncStorage.getItem("db_list",function(err,res) {
            var db_list=JSON.parse(res)||[];
            var db_vals=db_list.find(function(obj) {return obj.dbname==this.state.dbname}.bind(this));
            var base_url=db_vals.protocol+"://"+db_vals.hostname+":"+db_vals.port;
            rpc.set_base_url(base_url);
             var ctx={
                  data: {
                      db_name: this.state.dbname,
                      login: this.state.login,
                      password: this.state.password,
                  }
              };
              rpc.execute("login","login",[],{context:ctx},function(err,res) {
                  if (err) {
                      alert("Error: "+err);
                      return;
                  }
                  var user_id=res.cookies.user_id;
                  var user_name=res.cookies.user_name;
                  var company_name=res.cookies.company_name;
                  AsyncStorage.setItem("user_id",""+user_id);
                  AsyncStorage.setItem("user_name",user_name);
                  AsyncStorage.setItem("company_name",company_name);
                  AsyncStorage.setItem("base_url",base_url);
                  var login_action={name:"action",action:"main_menu_mobile"};
                  ui_params.load_ui_params(function(err) {
                      if (err) {
                          alert("Error: "+err);
                          return;
                      }
                      this.props.navigator.replace(login_action);
                  }.bind(this));
              }.bind(this));
        }.bind(this));
  }

  manage_db() {
      this.props.navigator.push({name:"db_list"});
  }

  click_link(action) {
      this.props.navigator.push(action);
  }
}

module.exports=Login;
