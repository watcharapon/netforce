# Copyright (c) 2012-2015 Netforce Co. Ltd.
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
# OR OTHER DEALINGS IN THE SOFTWARE.

from netforce.controller import Controller
import base64
import os
from netforce.database import get_active_db


class Upload(Controller):
    _path = "/upload"

    def post(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        fname = self.get_argument("filename", None)
        print(">>> upload %s" % fname)
        if self.request.headers.get("Content-Type") == "image/jpeg":
            data = self.request.body
        else:
            info = self.request.files["file"]
            data = info[0]["body"]
            if not fname:
                fname = info[0]["filename"]
        print("data size: %s" % len(data))
        rand = base64.urlsafe_b64encode(os.urandom(8)).decode()
        res = os.path.splitext(fname)
        basename, ext = res
        fname2 = basename + "," + rand + ext
        dbname = get_active_db()
        fdir = os.path.join("static", "db", dbname, "files")
        if not os.path.exists(fdir):
            os.makedirs(fdir)
        path = os.path.join(fdir, fname2)
        open(path, "wb").write(data)
        self.write(fname2)
        if ext.lower() in (".jpg", ".jpeg", ".png", ".gif"):
            fname3 = basename + "-resize-256" + "," + rand + ext
            path_thumb = os.path.join(fdir, fname3)
            os.system(r"convert -resize 256x256\> '%s' '%s'" % (path, path_thumb))
            fname4 = basename + "-resize-512" + "," + rand + ext
            path_thumb2 = os.path.join(fdir, fname4)
            os.system(r"convert -resize 512x512\> '%s' '%s'" % (path, path_thumb2))
            fname5 = basename + "-resize-128" + "," + rand + ext
            path_thumb3 = os.path.join(fdir, fname5)
            os.system(r"convert -resize 128x128\> '%s' '%s'" % (path, path_thumb3))
        print("<<< upload %s" % fname)

    def options(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Methods", "POST")

Upload.register()
