var $=require("jquery");

module.exports=function(state, action) {
    console.log("##################################");
    console.log("reducer",state,action);
    if (state==null) {
        return {};
    }
    var new_state=$.extend(true,{},state); // TODO: deep-copy
    switch (action.type) {
    }
    console.log("new_state",new_state);
    return new_state;
}
