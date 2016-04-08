var $=require("jquery");

_base_url=null;

module.exports.set_base_url=function(url) {
    _base_url=url;
}

module.exports.execute=function (model,method,args,opts,cb) {
    console.log("RPC",model,method,args,opts);
    if (!_base_url) throw "RPC base url not set";
    var params=[model,method];
    params.push(args);
    if (opts) {
        params.push(opts);
    }
    $.ajax({
        url: _base_url+"/json_rpc",
        method: "POST",
        data: JSON.stringify({
            id: (new Date()).getTime(),
            method: "execute",
            params: params
        }),
        dataType: "json",
        contentType: "application/x-www-form-urlencoded; charset=UTF-8",
        success: function(data) {
            if (data.error) {
                console.log("RPC ERROR",model,method,data.error.message);
            } else {
                console.log("RPC OK",model,method,data.result);
            }
            if (cb) {
                cb(data.error?data.error.message:null,data.result);
            }
        },
        error: function() {
            console.log("RPC ERROR",model,method);
        }
    });
}

module.exports.upload_file=function(file,result_cb,progress_cb) {
    console.log("upload_file",file);
    if (!_base_url) throw "RPC base url not set";
    var file_data=new FormData();
    file_data.append("file",file);
    $.ajax({
        url: _base_url+"/upload?filename="+encodeURIComponent(file.name),
        type: "POST",
        data: file_data,
        contentType: false,
        processData: false,
        success: function(res) {
            console.log("upload_file success",res);
            if (result_cb) result_cb(null,res);
        },
        xhr: function() {
            var xhr=jQuery.ajaxSettings.xhr();
            xhr.upload.addEventListener("progress",function(evt) {
                if (!evt.lengthComputable) return;
                if (progress_cb) progress_cb(evt.loaded,evt.total);
            },false);
            return xhr;
        }
    });
}
