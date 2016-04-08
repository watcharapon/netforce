rpc=require("./rpc")

module.exports.load_ui_params=function() {
    return function(dispatch,get_state) {
        rpc.execute("ui.params","load_ui_params",[],{},function(err,data) {
            dispatch({
                type: "UI_PARAMS_LOADED",
                ui_params: data,
            });
        });
    }
}
