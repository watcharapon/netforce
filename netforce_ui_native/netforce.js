'use strict';
import React, {
  AppRegistry,
  Component,
  StyleSheet,
  Text,
  TextInput,
  TouchableNativeFeedback,
  TouchableHighlight,
  Navigator,
  StatusBar,
  Platform,
  BackAndroid,
  View
} from 'react-native';

var NavBar=require("./navbar");
var Login=require("./login");
var DBList=require("./db_list");
var DBForm=require("./db_form");
var Menu=require("./menu");
var List=require("./list");
var Form=require("./form");
var Page=require("./page");

var _nav;

class Netforce extends Component {
    render() {
        return <Navigator renderScene={this.render_scene.bind(this)}/>
    }

    render_scene(route,navigator) {
        _nav=navigator;
        if (!navigator.scene_no) navigator.scene_no=1;
        else navigator.scene_no+=1;
        return <View style={{ flex: 1, }}>
            <NavBar navigator={navigator}/>
            {function() {
                if (!route) route={name:"login"};
                if (route.name=="login") {
                    return <Login navigator={navigator}/>
                } else if (route.name=="db_list") {
                    return <DBList navigator={navigator}/>
                } else if (route.name=="db_form") {
                    return <DBForm navigator={navigator} index={route.index}/>
                } else {
                    alert("Invalid route: "+route.name);
                }
            }.bind(this)()}
        </View>
  }
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#F5FCFF',
  },
  instructions: {
    textAlign: 'center',
    color: '#333333',
    marginBottom: 5,
  },
  button: {
      borderWidth: 1,
      borderStyle: "solid",
      padding: 10,
  },
  fieldLabel: {
      color: "#333",
  },
});

if (Platform.OS=="android") {
    BackAndroid.addEventListener('hardwareBackPress', function() {
        if (_nav && _nav.getCurrentRoutes().length > 1) {
            _nav.pop();
            return true;
        }
        return false;
    });
}

module.exports=Netforce;
