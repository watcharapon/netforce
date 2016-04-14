React = require("react");
var connect = require("react-redux").connect;
var ui_params=require("../ui_params");
var utils=require("../utils");

var FieldSelect=React.createClass({
    mixins: [ui_params],

    getInitialState() {
        var f=this.get_field(this.props.model,this.props.name);
        var val=this.props.data[this.props.name];
        var val_str=utils.fmt_field_val(val,f);
        var readonly=this.props.readonly?true:false;
        if (this.props.edit_focus) readonly=true;
        return {
            readonly: readonly,
            val_str: val_str,
        };
    },

    componentDidMount() {
    },

    render() {
        var f=this.get_field(this.props.model,this.props.name);
        if (this.state.readonly) {
            return <span onClick={this.click_readonly}>{this.state.val_str}</span>;
        } else {
            return <select className="form-control" ref={this.input_mounted} onBlur={this.on_blur} type="text" value={this.state.val_str} onChange={this.onchange}>
                <option value=""></option>
                {f.selection.map(function(o) {
                    return <option value={o[0]}>{o[1]}</option>
                }.bind(this))}
            </select>
        }
    },

    onchange(e) {
        var val_str=e.target.value;
        this.setState({val_str:val_str});
        this.props.data[this.props.name]=val_str;
    },

    click_readonly() {
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

var select=function(state) {
    return {
        ui_params: state.ui_params,
    }
}

module.exports=connect(select)(FieldSelect);
