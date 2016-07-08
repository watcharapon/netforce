React = require("react");
var ui_params=require("../ui_params");
var utils=require("../utils");

var FieldChar=React.createClass({
    getInitialState() {
        var f=ui_params.get_field(this.props.model,this.props.name);
        var val=this.props.data[this.props.name];
        var val_str=utils.fmt_field_val(val,f);
        var readonly=this.props.readonly?true:false;
        if (f.readonly) readonly=true;
        if (this.props.edit_focus) readonly=true;
        return {
            readonly: readonly,
            val_str: val_str,
        };
    },

    componentDidMount() {
    },

    render() {
        if (this.state.readonly) {
            return <a href="#" style={{color:"#333"}} onClick={this.click_readonly}>{this.state.val_str}</a>;
        } else {
            return <input className="form-control" ref={this.input_mounted} onBlur={this.on_blur} type="text" value={this.state.val_str} onChange={this.onchange}/>
        }
    },

    onchange(e) {
        var val_str=e.target.value;
        this.setState({val_str:val_str});
        this.props.data[this.props.name]=val_str;
    },

    click_readonly(e) {
        e.preventDefault();
        if (this.props.edit_focus) {
            this.setState({readonly:false});
        }
    },

    input_mounted(el) {
        if (this.props.edit_focus) {
            if (el) el.focus();
        }
    },

    on_blur() {
        if (this.props.edit_focus) {
            this.setState({readonly:true});
        }
    },
});

module.exports=FieldChar;
