var files_url="https://time.netforce.com/static/db/nftime/files/";

module.exports.get_image_url=function(filename) {
    if (!filename) return null;
    var url=files_url+filename;
    return url;
}

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
    } else if (field.type=="many2one") {
        return val?val[1]:"";
    } else if (field.type=="one2many") {
        return JSON.stringify(val);
    } else {
        throw "Invalid field type: "+field.type;
    }
}
