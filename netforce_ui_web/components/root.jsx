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
            <p>HELLO</p>
            {/*<MultiView title="Invoices" model="account.invoice" list_layout="cust_invoice_list" form_layout="cust_invoice_form" tabs={[["All",[]],["Draft",[["state","=","draft"]]],["Approved",[["state","=","approved"]]]]}/>*/}
            <MultiView title="Audit Log" model="log"/>
        </div>
    },
});

var select=function(state) {
    return {
        ui_params: state.ui_params,
    }
}

module.exports=connect(select)(Root);
