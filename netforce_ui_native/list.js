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
var xpath = require('xpath');
var dom = require('xmldom').DOMParser;
var UIParams=require("./ui_params");
var utils=require("./utils");
var Button=require("./button");

var Icon = require('react-native-vector-icons/FontAwesome');

class List extends Component {
    constructor(props) {
        super(props);
        this.state = {
            dataSource: new ListView.DataSource({
                rowHasChanged: (row1, row2) => row1 !== row2,
            }),
        };
    }

    componentDidMount() {
        var layout=UIParams.get_layout("work_time_list_mobile");
        this.layout_doc=new dom().parseFromString(layout.layout);
        this.load_data();
    }

    load_data() {
        console.log("List.load_data");
        var cond=this.props.condition||[];
        var field_nodes=xpath.select("//field", this.layout_doc);
        var fields=[];
        field_nodes.forEach(function(el) {
            fields.push(el.getAttribute("name"));
        });
        console.log("fields",fields);
        RPC.execute(this.props.model,"search_read",[cond,fields],{},function(err,data) {
            if (err) {
                alert("ERROR: "+err);
                return;
            }
            this.setState({
                data: data,
                dataSource: this.state.dataSource.cloneWithRows(data),
            });
        }.bind(this));
    }

    render() {
        if (this.state.data==null) {
            return <Text>Loading...</Text>
        }
        if (this.state.data.length==0) return <Text>There are no items to display.</Text>
        var m=UIParams.get_model(this.props.model);
        return <View style={{flex:1}}>
            <ListView dataSource={this.state.dataSource} renderRow={this.render_row.bind(this)} style={{flex:1}}/>
            <View style={{paddingTop:5}}>
                <Button onPress={this.press_new.bind(this)}>
                    <View style={{height:50,backgroundColor:"#37b",alignItems:"center",justifyContent:"center"}}>
                        <Text style={{color:"#fff"}}><Icon name="plus" size={16} color="#eee"/> New {m.string}</Text>
                    </View>
                </Button>
            </View>
        </View>
    }

    render_row(obj) {
        var root=this.layout_doc.documentElement;
        var child_els=xpath.select("child::*", root);
        var cols=[];
        var rows=[];
        {child_els.forEach(function(el,i) {
            if (el.tagName=="newline") {
                rows.push(<View style={{flexDirection:"row", justifyContent: "space-between"}} key={rows.length}>{cols}</View>);
                cols=[];
                return;
            } else if (el.tagName=="field") {
                var name=el.getAttribute("name");
                var f=UIParams.get_field(this.props.model,name);
                var invisible=el.getAttribute("invisible");
                if (invisible) return;
                var val=obj[name];
                var val_str=utils.field_val_to_str(val,f);
                var col=<View key={cols.length} style={{flexDirection:"row"}}>
                    <Text style={{fontWeight:"bold",marginRight:5}}>{f.string}:</Text><Text>{val_str}</Text>
                </View>;
                cols.push(col);
            } else if (el.tagName=="text") {
                var tmpl=el.childNodes[0].nodeValue;
                var str=tmpl.replace(/\{(.*?)\}/g,function(a,b) {
                    var val_str=""+obj[b];
                    return val_str;
                }.bind(this));
                var col=<Text key={cols.length}>{str}</Text>;
                cols.push(col);
            } else {
                throw "Invalid tag name: "+el.tagName;
            }
        }.bind(this))}
        rows.push(<View style={{flexDirection:"row", justifyContent: "space-between"}} key={rows.length}>{cols}</View>);
        return <TouchableOpacity style={{borderBottomWidth:0.5,padding:5}} onPress={this.press_item.bind(this,obj.id)}>
            {rows}
        </TouchableOpacity>
    }

    press_item(active_id) {
        var action={
            view: "form_mobile",
            model: this.props.model,
            active_id: active_id,
        }
        this.props.navigator.push({name:"action",action:action});
    }

    press_new() {
        var action={
            view: "form_mobile",
            model: this.props.model,
        }
        this.props.navigator.push({name:"action",action:action});
    }
}

module.exports=List;
