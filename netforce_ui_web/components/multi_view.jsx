React = require("react");
var List=require("./list")
var Form=require("./form")

var MultiView=React.createClass({
    getInitialState() {
        var mode="list";
        return {
            mode: mode,
        };
    },

    componentDidMount() {
    },

    render() {
        if (this.state.mode=="list") {
            return <List title={this.props.title} model={this.props.model} tabs={this.props.tabs} on_new={this.on_new} on_select={this.on_select}/>
        } else if (this.state.mode=="form") {
            return <Form model={this.props.model} active_id={this.state.active_id} bread_title={this.props.title} on_bread={this.on_bread}/>
        } else {
            throw "Invalid view mode: "+this.state.mode;
        }
    },

    on_new() {
        this.setState({
            mode: "form",
            active_id: null,
        });
    },

    on_select(active_id) {
        this.setState({
            mode: "form",
            active_id: active_id,
        });
    },

    on_bread() {
        this.setState({
            mode: "list",
        });
    },
});

module.exports=MultiView;
