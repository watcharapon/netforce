var files_url="https://time.netforce.com/static/db/nftime/files/";

module.exports.get_image_url=function(filename) {
    if (!filename) return null;
    var url=files_url+filename;
    return url;
}
