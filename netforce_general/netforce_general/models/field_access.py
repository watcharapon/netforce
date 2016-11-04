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

from netforce.model import Model, fields
from netforce import access


class FieldAccess(Model):
    _name = "field.access"
    _string = "Field Access"
    _key = ["profile","field_id"]
    _fields = {
        "profile_id": fields.Many2One("profile", "Profile", required=True, on_delete="cascade", search=True),
        "field_id": fields.Many2One("field", "Field", required=True, on_delete="cascade", search=True),
        "perm_read": fields.Boolean("Read"),
        "perm_write": fields.Boolean("Write"),
    }
    _order = "field_id.model_id.string,field_id.string,profile_id.name"
    _defaults = {
        "perm_read": True,
        "perm_write": True,
    }

FieldAccess.register()
