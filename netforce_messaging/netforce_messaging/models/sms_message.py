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
import uuid
import time
from urllib.request import urlopen
from urllib.parse import urlencode
import re


class SmsMessage(Model):
    _name = "sms.message"
    _string = "SMS Message"
    _name_field = "sender"
    _fields = {
        "account_id": fields.Many2One("sms.account", "SMS Account"),
        "date": fields.DateTime("Date", required=True, search=True),
        "phone": fields.Char("Phone Number", required=True, size=256, search=True),
        "body": fields.Text("Body", search=True),
        "state": fields.Selection([["draft", "Draft"], ["to_send", "To Send"], ["sent", "Sent"], ["error", "Error"]], "Status", required=True),
        "uuid": fields.Char("UUID"),
    }
    _order = "date desc"
    _defaults = {
        "state": "draft",
        "uuid": lambda *a: str(uuid.uuid4()),
        "date": lambda *a: time.strftime("%Y-%m-%d %H:%M:%S"),
    }

    def to_send(self, ids, context={}):
        for obj in self.browse(ids):
            obj.write({"state": "to_send"})

    def send_messages(self, context={}):
        ids = self.search([["state", "=", "to_send"]])
        for obj in self.browse(ids):
            try:
                acc = obj.account_id
                if not acc:
                    res = get_model("sms.account").search([["type", "=", "thaibulksms"]])
                    if res:
                        acc = get_model("sms.account").browse(res[0])
                        obj.write({"account_id": acc.id})
                if not acc:
                    raise Exception("Missing SMS account")
                params = {
                    'username': acc.username,
                    'password': acc.password,
                    'msisdn': obj.phone,
                    'message': obj.body[:160].encode('tis-620'),
                    'sender': acc.sender
                }
                url = "https://secure.thaibulksms.com/sms_api.php?" + urlencode(params)
                res = urlopen(url, timeout=10).read().decode()
                if res.find("<Status>1</Status>") == -1:
                    raise Exception(res)
                obj.write({"state": "sent"})
            except Exception as e:
                print("Failed to send SMS: %s" % e)
                import traceback
                traceback.print_exc()
                obj.write({"state": "error"})
                get_model("log").log("Failed to send SMS", str(e))

SmsMessage.register()
