module.exports.field_val_to_str=function(val,field) {
    if (field.type=="char") {
        return val||"";
    } else if (field.type=="text") {
        return val||"";
    } else if (field.type=="float") {
        return val==null?"":""+val;
    } else if (field.type=="decimal") {
        return val==null?"":""+val;
    } else if (field.type=="integer") {
        return val==null?"":""+val;
    } else if (field.type=="date") {
        return val||"";
    } else if (field.type=="datetime") {
        return val||"";
    } else if (field.type=="selection") {
        if (val!=null) {
            var opt=field.selection.find(function(o) {return o[0]==val});
            str=opt?opt[1]:"";
        } else {
            str="";
        }
        return str;
    } else if (field.type=="file") {
        return val||"";
    } else if (field.type=="many2one") {
        return val?val[1]:"";
    } else if (field.type=="one2many") {
        return JSON.stringify(val);
    } else {
        throw "Invalid field type: "+field.type;
    }
}

module.exports.get_change_vals=function(data) {
    console.log("get_change_vals",data);
    var change={};
    for (var name in data) {
        if (name=="id") continue;
        if (name=="_orig_data") continue;
        var v=data[name];
        var orig_v;
        if (data.id) {
            if (!data._orig_data) throw "Missing _orig_data";
            orig_v=data._orig_data[name];
        } else {
            orig_v=null;
        }
        if (v && typeof(v)=="object") v=v[0]; // XXX
        if (orig_v && typeof(orig_v)=="object") orig_v=orig_v[0]; // XXX
        if (v!=orig_v) change[name]=v;
    }
    console.log("=> change",change);
    return change;
}
