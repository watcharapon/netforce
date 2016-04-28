var _rpc_base_url;
var _database;
var _schema;

module.exports.set_base_url=function(base_url) {
    _rpc_base_url=base_url;
    _database=null;
    _schema=null;
}

module.exports.set_database=function(dbname) {
    _database=dbname;
    _schema=null;
}

module.exports.set_schema=function(schema) {
    _schema=schema;
}

module.exports.execute=function(model,method,args,opts,cb) {
    console.log("rpc.execute",model,method,args,opts);
    if (!_rpc_base_url) throw "RPC base url is undefined";
    var params=[model,method];
    params.push(args);
    if (opts) {
        params.push(opts);
    }
    var headers={
        "Accept": "application/json",
        "Content-Type": "application/json",
    };
    if (_database) headers["X-Database"]=_database;
    if (_schema) headers["X-Schema"]=_schema;
    console.log("_rpc_base_url",_rpc_base_url);
    console.log("headers",headers);
    fetch(_rpc_base_url+"/json_rpc",{
        method: "POST",
        headers: headers,
        body: JSON.stringify({
            id: (new Date()).getTime(),
            method: "execute",
            params: params
        }),
    })
    .then((response) => response.json())
    .then((data) => {
        if (data.error) {
            if (cb) cb(data.error.message,null);
        } else {
            if (cb) cb(null,data.result);
        }
    })
    .catch((err) => {
        console.log("rpc error",err);
        if (cb) cb(err,null);
    })
    .done();
}

module.exports.upload_file=function(file,result_cb,progress_cb) {
    console.log("rpc.upload_file",file);
    if (!_rpc_base_url) throw "RPC base url is undefined";
    var data=new FormData();
    data.append("file",file);
    fetch(_rpc_base_url+"/upload?filename="+encodeURIComponent(file.name),{
        method: "POST",
        body: data,
    })
    .then((response) => response.text())
    .then((responseText) => {
        if (result_cb) result_cb(null,responseText);
    })
    .catch((err) => {
        alert("upload error: "+err);
        if (result_cb) result_cb(err,null);
    })
    .done();
}

module.exports.get_file_uri=function(filename) {
    if (!filename) return null;
    var url=_rpc_base_url+"/static/db/"+_database+"/files/"+filename;
    return url;
}

