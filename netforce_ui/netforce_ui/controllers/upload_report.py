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
import os
import json
import requests
import re


class UploadReport(Controller):
    _path = "/upload_report"

    def get(self):
        state = json.loads(self.get_argument("state"))
        path = state["path"]
        code = self.get_argument("code")
        url = "https://accounts.google.com/o/oauth2/token"
        params = {
            "code": code,
            "client_id": "659737773479.apps.googleusercontent.com",
            "client_secret": "vCWWS51YEW8T0gLTQ43fiCKc",
            "redirect_uri": "http://%s/upload_report" % self.request.host,
            "grant_type": "authorization_code",
        }
        res = requests.post(url, data=params)
        print("XXX", str(res))
        data = json.loads(res.text)
        access_token = data["access_token"]

        url = "https://docs.google.com/feeds/upload/create-session/default/private/full"
        f = open(path, "rb")
        buf = f.read()
        f.close()
        os.unlink(path)
        data = """<?xml version="1.0" encoding="UTF-8"?>
<entry xmlns="http://www.w3.org/2005/Atom" xmlns:docs="http://schemas.google.com/docs/2007">
    <category scheme="http://schemas.google.com/g/2005#kind" term="http://schemas.google.com/docs/2007#spreadsheet"/>
    <title>%s</title>
</entry>""" % state["filename"]
        headers = {
            "Authorization": "Bearer " + access_token,
            "Content-Type": "application/atom+xml",
            "X-Upload-Content-Type": "application/vnd.ms-excel",
            #"X-Upload-Content-Type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "X-Upload-Content-Length": str(len(buf)),
            "GData-Version": "3.0",
        }
        res = requests.post(url, headers=headers, data=data)
        print("YYY", str(res), res.headers, res.text)
        url = res.headers["location"]
        print("url", url)
        chunk_size = 512 * 1024
        sent = 0
        while sent < len(buf):
            data = buf[sent:sent + chunk_size]
            headers = {
                "Authorization": "Bearer " + access_token,
                "Content-Type": "application/vnd.ms-excel",
                #"Content-Type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "Content-Range": "bytes %d-%d/%s" % (sent, sent + len(data) - 1, len(buf)),
            }
            print("headers", headers)
            res = requests.put(url, headers=headers, data=data)
            print("ZZZ", str(res), res.headers, res.text)
            sent += len(data)
        key = re.search("sheet%3A(.*?)<", res.text).group(1)
        url = "https://docs.google.com/spreadsheet/ccc?key=" + key
        self.redirect(url)

UploadReport.register()
