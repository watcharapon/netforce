React = require("react");
var connect = require("react-redux").connect;
var ui_params=require("../ui_params");
var utils=require("../utils");
var rpc=require("../rpc");

var FieldMany2One=React.createClass({
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
            show_menu: false,
        };
    },

    componentDidMount() {
        window.addEventListener("click",this.click_page,false);
    },

    componentWillUnmount () {
        window.removeEventListener('click', this.click_page)
    },

    render() {
        if (this.state.readonly) {
            return <span onClick={this.click_readonly}>{this.state.val_str}</span>;
        } else {
            return <div>
                <div className="input-group">
                    <input className="form-control" ref={this.input_mounted} onBlur={this.on_blur} type="text" value={this.state.val_str} onChange={this.onchange_text}/>
                    <span className="input-group-btn">
                        <a href="#" target="_bank" className="btn btn-default" tabindex="-1"><span className="glyphicon glyphicon-arrow-right"></span></a>
                        <button type="button" className="btn btn-default" tabindex="-1" onClick={this.click_caret}><span className="caret"></span></button>
                    </span>
                </div>
            {function() {
                if (!this.state.show_menu) return;
                return <div style={{position:"relative"}}>
                    <ul style={{position:"absolute",top:0,left:0,zIndex:1000,backgroundColor:"#fff",border:"1px solid rgba(0,0,0,0.15)",maxHeight:250,overflow:"auto",minWidth:200,padding:"5px 0"}}>
                        {this.state.results.map(function(o,i) {
                            return <li key={i} style={{listStyle:"none"}}>
                                <a href="#" style={{display:"block",padding:"3px 20px",textDecoration:"none",color:"#333",fontSize:"14px"}} onClick={this.select_item.bind(this,o[0],o[1])}>{o[1]}</a>
                            </li>
                        }.bind(this))}
                    </ul>
                </div>
            }.bind(this)()}
            </div>
        }
    },

    click_caret(e) {
        e.preventDefault();
        if (this.state.show_menu) {
            this.setState({show_menu:false});
            return;
        }
        this.load_results("");
    },

    load_results(q) {
        var f=this.get_field(this.props.model,this.props.name);
        var cond=[];
        var ctx={};
        rpc.execute(f.relation,"name_search",[q,cond],{context:ctx,limit:100},function(err,res) {
            if (err) throw "ERROR: "+err;
            this.setState({
                show_menu: true,
                results: res,
            });
        }.bind(this));
    },

    select_item(record_id,record_name,e) {
        console.log("FieldMany2One.select_item",this.props.name);
        e.preventDefault();
        e.stopPropagation();
        this.setState({
            val_str: record_name,
            show_menu: false,
        });
        this.props.data[this.props.name]=[record_id,record_name];
    },

    click_page() {
        console.log("FieldMany2One.click_page",this.props.name);
        this.setState({show_menu:false});
    },

    onchange_text(e) {
        var val_str=e.target.value;
        this.setState({val_str:val_str});
        this.props.data[this.props.name]=null;
        this.load_results(val_str);
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
        var val=this.props.data[this.props.name];
        var val_str=utils.fmt_field_val(val,f);
        this.setState({val_str:val_str});
    },
});

var select=function(state) {
    return {
        ui_params: state.ui_params,
    }
}

module.exports=connect(select)(FieldMany2One);
