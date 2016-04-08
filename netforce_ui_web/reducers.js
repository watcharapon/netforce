var $=require("jquery");

module.exports=function(state, action) {
    console.log("##################################");
    console.log("reducer",state,action);
    if (state==null) {
        return {};
    }
    var new_state=$.extend(true,{},state); // TODO: deep-copy
    switch (action.type) {
        case "UI_PARAMS_LOADED":
            new_state.ui_params=action.ui_params;
            break;
    }
    console.log("new_state",new_state);
    return new_state;
}
