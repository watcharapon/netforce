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
  Picker,
  Navigator,
  AsyncStorage,
  View
} from 'react-native';

var RPC=require("./RPC");
var Button=require("./button");

class DBForm extends Component {
    constructor(props) {
        super(props);
        this.state = {protocol:"http",port:"80"};
    }

    componentDidMount() {
        if (this.props.index==null) return;
        AsyncStorage.getItem("db_list",function(err,res) {
            var db_list=JSON.parse(res)||[];
            var vals=db_list[this.props.index];
            this.setState(vals);
        }.bind(this));
    }

    render() {
        return <View>
            <Text>
                Database Name:
            </Text>
            <TextInput style={{height:40, borderColor: 'gray', borderWidth: 1}} value={this.state.dbname} onChangeText={(val)=>this.setState({dbname:val})}/>
            <Text>
                Host Name:
            </Text>
            <TextInput style={{height:40, borderColor: 'gray', borderWidth: 1}} value={this.state.hostname} onChangeText={(val)=>this.setState({hostname:val})}/>
            <Text>
                Protocol:
            </Text>
            <Picker selectedValue={this.state.protocol} onValueChange={(val) => this.setState({protocol: val})}> 
                <Picker.Item label="HTTP" value="http"/>
                <Picker.Item label="HTTPS" value="https"/>
            </Picker>
            <Text>
                Port:
            </Text>
            <TextInput style={{height:40, borderColor: 'gray', borderWidth: 1}} value={this.state.port} onChangeText={(val)=>this.setState({port:val})}/>
            <View style={{paddingTop:5}}>
                <Button onPress={this.save.bind(this)}>
                    <View style={{height:50,backgroundColor:"#37b",alignItems:"center",justifyContent:"center"}}>
                        <Text style={{color:"#fff"}}>Save</Text>
                    </View>
                </Button>
            </View>
            <View style={{paddingTop:5}}>
                <Button onPress={this.delete_db.bind(this)}>
                    <View style={{height:50,backgroundColor:"#c33",alignItems:"center",justifyContent:"center"}}>
                        <Text style={{color:"#fff"}}>Delete</Text>
                    </View>
                </Button>
            </View>
        </View>
    }

    save() {
        AsyncStorage.getItem("db_list",function(err,res) {
            var db_list=JSON.parse(res)||[];
            if (this.props.index!=null) db_list[this.props.index]=this.state;
            else db_list.push(this.state);
            AsyncStorage.setItem("db_list",JSON.stringify(db_list),function(err) {
                this.props.navigator.pop();
                this.props.navigator.replace({name:"db_list"});
            }.bind(this));
        }.bind(this));
    }

    delete_db() {
        AsyncStorage.getItem("db_list",function(err,res) {
            var db_list=JSON.parse(res)||[];
            db_list.splice(this.props.index,1);
            AsyncStorage.setItem("db_list",JSON.stringify(db_list),function(err) {
                this.props.navigator.pop();
                this.props.navigator.replace({name:"db_list"});
            }.bind(this));
        }.bind(this));
    }
}

module.exports=DBForm;
