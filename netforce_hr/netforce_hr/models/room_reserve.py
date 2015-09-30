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
from netforce.access import get_active_user


class RoomReserve(Model):
    _name = "room.reserve"
    _string = "Room Reservation"
    _fields = {
        "request_date": fields.Date("Request Date", required=True, readonly=True),
        "user_id": fields.Many2One("base.user", "Requested By", required=True, readonly=True),
        "contact_id": fields.Many2One("contact", "Contact"),
        "room_id": fields.Many2One("room", "Room", required=True, search=True),
        "date": fields.Date("Reserve Date", required=True),
        "from_time": fields.Char("From Time", required=True),
        "to_time": fields.Char("To Time", required=True),
        "details": fields.Text("Details"),
        "comments": fields.One2Many("message", "related_id", "Comments"),
        "state": fields.Selection([["draft", "Draft"], ["waiting_approval", "Waiting Approval"], ["approved", "Approved"], ["canceled", "Canceled"]], "Status", required=True),
    }
    _order = "request_date desc,id desc"

    _defaults = {
        "request_date": lambda *a: time.strftime("%Y-%m-%d"),
        "user_id": lambda *a: get_active_user(),
        "date": lambda *a: time.strftime("%Y-%m-%d"),
        "state": "draft",
    }

    def submit(self, ids, context={}):
        obj = self.browse(ids)[0]
        obj.write({"state": "waiting_approval"})

    def approve(self, ids, context={}):
        user_id = get_active_user()
        user = get_model("base.user").browse(user_id)
        obj = self.browse(ids)[0]
        obj.write({"state": "approved"})
        vals = {
            "related_id": "room.reserve,%s" % obj.id,
            "body": "Approved by %s" % user.name,
        }
        get_model("message").create(vals)

    def reject(self, ids, context={}):
        user_id = get_active_user()
        user = get_model("base.user").browse(user_id)
        obj = self.browse(ids)[0]
        obj.write({"state": "canceled"})
        vals = {
            "related_id": "room.reserve,%s" % obj.id,
            "body": "Rejected by %s" % user.name,
        }
        get_model("message").create(vals)

RoomReserve.register()
