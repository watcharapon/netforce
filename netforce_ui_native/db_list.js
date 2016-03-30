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
  TouchableOpacity,
  AsyncStorage,
  View
} from 'react-native';

var RPC=require("./RPC");
var Button=require("./button");

class DBList extends Component {
    constructor(props) {
        super(props);
        this.state = {};
    }

    componentDidMount() {
        this.load_data();
    }

    load_data() {
        AsyncStorage.getItem("db_list",function(err,res) {
            this.setState({
                db_list: JSON.parse(res)||[],
            });
        }.bind(this));
    }

    render() {
        if (!this.state.db_list) return <Text>Loading...</Text>;
        return <View style={{flex:1}}>
            <View style={{flex:1}}>
                {function() {
                    if (this.state.db_list.length==0) return <Text>There are no items to display.</Text>
                    return <View>
                        {this.state.db_list.map(function(obj,index) {
                            return <TouchableOpacity key={index} onPress={this.edit_db.bind(this,index)}>
                                <View style={{borderBottomWidth:0.5,padding:5,height:50,justifyContent:"center"}}>
                                    <Text>{obj?obj.dbname:""}</Text>
                                </View>
                            </TouchableOpacity>
                        }.bind(this))}
                    </View>
                }.bind(this)()}
            </View>
            <View style={{paddingTop:5}}>
                <Button onPress={this.add_db.bind(this)}>
                    <View style={{height:50,backgroundColor:"#37b",alignItems:"center",justifyContent:"center"}}>
                        <Text style={{color:"#fff"}}>Add Database</Text>
                    </View>
                </Button>
            </View>
        </View>
    }

    add_db() {
        this.props.navigator.push({name:"db_form"});
    }

    edit_db(index) {
        this.props.navigator.push({name:"db_form",index:index});
    }
}

module.exports=DBList;
