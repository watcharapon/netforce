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

from netforce.model import Model, fields, get_model
import time
import http.client
import urllib.request
uth_handler = urllib.request.HTTPBasicAuthHandler()


class AttendanceConfig(Model):
    _name = "hr.attendance.config"
    _string = "Attendance Config"

    _fields = {
        "name": fields.Char("Attendance Config Name"),
        "ip_address": fields.Char("IP address"),
        "url_download": fields.Char("Url Download"),
        "port": fields.Integer("Port"),
        "user": fields.Char("Username"),
        "password": fields.Char("Password"),
        "comments": fields.One2Many("message", "related_id", "Comments"),
    }

    # FIXME cannot download file
    def test(self, ids, context={}):
        for obj in self.browse(ids):
            # Create an OpenerDirector with support for Basic HTTP Authentication...
            try:
                auth_handler = urllib.request.HTTPBasicAuthHandler()

                auth_handler.add_password(realm='Basic Authentication Application',
                                          uri="http://" + obj.ip_address,
                                          user=obj.user,
                                          passwd=obj.password)
                opener = urllib.request.build_opener(auth_handler)
                urllib.request.install_opener(opener)
                urllib.request.urlopen('http://' + obj.ip_address)
                # download_url=obj.url_download# POST target
                # post_data={'uid':'extlog.dat'} # POST data for download attendance log
                conn = http.client.HTTPConnection(obj.ip_address, obj.port, timeout=10)
                if conn != None:
                    conn.close()  # close connection with server
                    return {
                        "next": {
                            "name": "attend_config",
                            "mode": "form",
                            "active_id": obj.id
                        },
                        "flash": "Device connected."
                    }

            except Exception as e:
                raise Exception("Error! Cannot connection (%s)" % (e))

AttendanceConfig.register()
