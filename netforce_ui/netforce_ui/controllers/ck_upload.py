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


class CKUpload(Controller):
    _path = "/ck_upload"

    def post(self):
        info = self.request.files["upload"]
        fname = info[0]["filename"]
        print(">>> ck_upload %s" % fname)
        data = info[0]["body"]
        print("data size: %s" % len(data))
        rand = base64.urlsafe_b64encode(os.urandom(8)).decode()
        res = os.path.splitext(fname)
        fname2 = res[0] + "," + rand + res[1]
        dbname = get_active_db()
        fdir = os.path.join("static", "db", dbname, "files")
        if not os.path.exists(fdir):
            os.makedirs(fdir)
        open(os.path.join(fdir, fname2), "wb").write(data)
        func = self.get_argument("CKEditorFuncNum")
        url = "/static/db/%s/files/%s" % (dbname, fname2)
        self.write("<script>window.parent.CKEDITOR.tools.callFunction(%s,\"%s\");</script>" % (func, url))
        print("<<< ck_upload %s" % fname)

CKUpload.register()
