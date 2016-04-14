var rpc=require("./rpc");

var _ui_params=null;

module.exports={
    load_ui_params: function(modules,cb) {
        var ctx={modules:modules};
        rpc.execute("ui.params","load_ui_params",[],{context:ctx},function(err,data) {
            if (err) {
                cb(err);
                return;
            }
            _ui_params=data;
            cb();
        });
    },

    get_layout: function(name) {
        if (!_ui_params) throw "UI params not found";
        var l=_ui_params.layouts[name];
        if (!l) throw "Layout not found: "+name;
        return l;
    },

    find_layout: function(conds) {
        if (!_ui_params) throw "UI params not found";
        var layouts=_ui_params.layouts;
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
        if (!_ui_params) throw "UI params not found";
        var m=_ui_params.models[model];
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
