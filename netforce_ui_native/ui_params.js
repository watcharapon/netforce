'use strict';
import React, {
  AsyncStorage,
} from 'react-native';

var RPC=require("./RPC");

var _ui_params=null;

module.exports.set_ui_params=function(params) {
    _ui_params=params;
}

module.exports.load_ui_params=function(cb) {
    var ctx={mobile_only:true};
    RPC.execute("ui.params","load_ui_params",[],{context:ctx},function(err,data) {
        if (err) {
            cb(err);
            return;
        }
        _ui_params=data;
        console.log("got UI params");
        AsyncStorage.setItem("ui_params",JSON.stringify(data));
        cb(null);
    });
}

module.exports.get_action=function(name) {
    console.log("get_action",name);
    if (!name) throw "Missing action name";
    if (!_ui_params) throw "UI params not loaded";
    var action=_ui_params.actions[name];
    if (!action) throw "Action not found: "+name;
    return action;
}

module.exports.get_layout=function(name) {
    console.log("get_layout",name);
    if (!name) throw "Missing layout name";
    if (!_ui_params) throw "UI params not loaded";
    var layout=_ui_params.layouts[name];
    if (!layout) throw "Layout not found: "+name;
    return layout;
}
