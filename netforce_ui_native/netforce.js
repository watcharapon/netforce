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
  AsyncStorage,
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
var SearchM2O=require("./search_m2o");
var UIParams=require("./ui_params");

var _nav;

class Netforce extends Component {
    constructor(props) {
        super(props);
        this.state = {};
    }

    componentDidMount() {
    }

    render() {
        return <Navigator renderScene={this.render_scene.bind(this)}/>
    }

    render_scene(route,navigator) {
        _nav=navigator;
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
                } else if (route.name=="action") {
                    var action;
                    if (typeof(route.action)=="object") {
                        action=route.action;
                    } else if (typeof(route.action)=="string") {
                        action=UIParams.get_action(route.action);
                    } else {
                        throw "Invalid action";
                    }
                    if (action.view=="menu_mobile") {
                        return <Menu navigator={navigator} layout={action.layout}/>
                    } else if (action.view=="list_mobile") {
                        return <List navigator={navigator} model={action.model} title={action.title} layout={action.layout}/>
                    } else if (action.view=="form_mobile") {
                        return <Form navigator={navigator} model={action.model} layout={action.layout} active_id={action.active_id}/>
                    } else if (action.view=="page_mobile") {
                        return <Page navigator={navigator} model={action.model} layout={action.layout} active_id={action.active_id}/>
                    }
                } else if (route.name=="search_m2o") {
                    return <SearchM2O navigator={navigator} model={route.model} on_select={route.on_select}/>
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
