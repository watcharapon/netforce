React = require("react");
var connect = require("react-redux").connect;
var actions=require("../actions")
var Menu=require("./menu")
var Loading=require("./loading")
var MultiView=require("./multi_view")

var Root=React.createClass({
    getInitialState() {
        return {};
    },

    componentDidMount() {
        this.props.dispatch(actions.load_ui_params());
    },

    render() {
        if (!this.props.ui_params) return <Loading/>; 
        return <div>
            <p>blablabla</p>
            <MultiView title="Work Time" model="work.time" tabs={[["All",[]],["Draft",[["state","=","draft"]]]]}/>
        </div>
    },
});

var select=function(state) {
    return {
        ui_params: state.ui_params,
    }
}

module.exports=connect(select)(Root);
