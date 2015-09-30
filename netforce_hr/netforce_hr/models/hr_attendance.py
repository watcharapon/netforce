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
from netforce import access


class Attendance(Model):
    _name = "hr.attendance"
    _string = "Attendance Event"
    _audit_log = True

    _fields = {
        "employee_id": fields.Many2One("hr.employee", "Employee", required=True, search=True),
        "time": fields.DateTime("Time", required=True, search=True),
        "action": fields.Selection([["sign_in", "Sign In"], ["sign_out", "Sign Out"]], "Action", required=True, search=True),
        "comments": fields.One2Many("message", "related_id", "Comments"),
    }
    _order = "time desc"
    _defaults = {
        "time": lambda *a: time.strftime("%Y-%m-%d %H:%M:S"),
        "user_id": lambda *a: access.get_active_user(),
    }

Attendance.register()
