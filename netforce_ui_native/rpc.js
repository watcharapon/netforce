var _rpc_base_url;

module.exports.set_base_url=function(base_url) {
    _rpc_base_url=base_url;
}

module.exports.execute=function(model,method,args,opts,cb) {
    console.log("rpc.execute",model,method,args,opts);
    if (!_rpc_base_url) throw "RPC base url is undefined";
    var params=[model,method];
    params.push(args);
    if (opts) {
        params.push(opts);
    }
    fetch(_rpc_base_url+"/json_rpc",{
        method: "POST",
        headers: {
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            id: (new Date()).getTime(),
            method: "execute",
            params: params
        }),
    })
    .then((response) => response.json())
    .then((data) => {
        if (data.error) {
            if (cb) cb(data.error,null);
        } else {
            if (cb) cb(null,data.result);
        }
    })
    .catch((err) => {
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
