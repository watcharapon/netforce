'use strict';
import React, {
  AppRegistry,
  Component,
  View,
  Text,
  Image,
  Platform,
  TouchableOpacity,
} from 'react-native';

class Navbar extends Component {
    render() {
        if (Platform.OS=="ios") {
            var status_height=20;
        } else {
            var status_height=0;
        }
        return <View style={{backgroundColor:"#258",height:44,marginTop:status_height,flexDirection:"row",justifyContent:"space-between"}}>
            <View style={{position:"absolute",left:0,right:0,bottom:0,top:0,alignItems:"center",flexDirection:"row",justifyContent:"center"}}>
                <View style={{flexDirection:"row",alignItems:"center",position:"relative",left:-10}}>
                    <Image source={require('./nf_logo_64.png')} style={{width:24}} resizeMode="contain"/>
                    <Text style={{fontSize:17,letterSpacing:0.5,color:"#eee",textAlign:"center",fontWeight:"500"}}>Netforce</Text>
                </View>
            </View>
            <View style={{alignItems:"center",flexDirection:"row"}}>
                {function() {
                    if (this.props.navigator.getCurrentRoutes().length < 2) return;
                    return <TouchableOpacity onPress={this.go_back.bind(this)} style={{}}>
                        <View style={{}}>
                            <Text style={{color:"#eee",fontSize:17,letterSpacing:0.5,marginLeft:8}}>Back</Text>
                        </View>
                    </TouchableOpacity>
                }.bind(this)()}
            </View>
      </View>
    }

    go_back() {
        this.props.navigator.pop();
    }
}

module.exports=Navbar;
