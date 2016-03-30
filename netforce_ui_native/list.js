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
  TouchableOpacity,
  Navigator,
  ListView,
  AsyncStorage,
  View
} from 'react-native';

var RPC=require("./RPC");

class List extends Component {
    constructor(props) {
        super(props);
        this.state = {
            dataSource: new ListView.DataSource({
                rowHasChanged: (row1, row2) => row1 !== row2,
            }),
            loaded: false,
        };
    }

    componentDidMount() {
    }

    load_data() {
        var cond=this.props.condition||[];
        var fields=["date","actual_hours","bill_hours","description","state"];
        RPC.execute("nf.time","search_read_path",[cond,fields],{},function(err,data) {
            if (err) {
                alert("Failed to get data: "+err.message);
                return;
            }
            this.setState({
                data: data,
                dataSource: this.state.dataSource.cloneWithRows(data),
                loaded: true,
                scene_no: this.props.navigator.scene_no,
            });
        }.bind(this));
    }

    render() {
        if (this.state.data==null || this.state.scene_no!=this.props.navigator.scene_no) {
            this.load_data();
            return <Text>Loading...</Text>
        }
        if (this.state.data.length==0) return <Text>There are no items to display.</Text>
        return <ListView dataSource={this.state.dataSource} renderRow={this.render_row.bind(this)}/>
    }

  render_row(obj) {
      return <TouchableOpacity onPress={this.show_details.bind(this,obj.id)}>
        <View style={{borderBottomWidth:0.5,padding:5}}>
            <View style={{flexDirection:"row"}}>
                <Text style={{fontSize:16,fontWeight:"bold",color:"#333"}}>{obj.actual_hours} hours</Text>
                <Text style={{flex:1,textAlign:"right"}}>{obj.date}</Text>
            </View>
            <View>
                <Text>{obj.description}</Text>
            </View>
        </View>
      </TouchableOpacity>
  }

  show_details(active_id) {
      this.props.navigator.push({
          name: "time_details",
          active_id: active_id,
      });
  }
}

module.exports=List;
