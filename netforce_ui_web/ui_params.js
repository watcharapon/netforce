module.exports={
    get_layout: function(name) {
        if (!this.props.ui_params) throw "UI params not found";
        var l=this.props.ui_params.layouts[name];
        if (!l) throw "Layout not found: "+name;
        return l;
    },

    find_layout: function(conds) {
        if (!this.props.ui_params) throw "UI params not found";
        var layouts=this.props.ui_params.layouts;
        var found=null;
        for (var n in layouts) {
            var l=layouts[n];
            if (l.model!=conds.model) continue;
            if (conds.type && l.type!=conds.type) continue;
            found=l;
        }
        return found;
    },

    get_model: function(model) {
        if (!this.props.ui_params) throw "UI params not found";
        var m=this.props.ui_params.models[model];
        if (!m) throw "Model not found: "+model;
        return m;
    },

    get_field: function(model,name) {
        var m=this.get_model(model);
        f=m.fields[name];
        if (!f) throw "Field not found: "+model+"."+name;
        return f;
    },
}
