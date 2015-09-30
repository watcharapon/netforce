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


class ContactCateg(Model):
    _name = "contact.categ"
    _string = "Contact Category"
    _key = ["code"]
    _name_field = "name"
    _fields = {
        "name": fields.Char("Category Name", required=True, search=True),
        "code": fields.Char("Category Code", search=True),
        "parent_id": fields.Many2One("contact.categ", "Parent", search=True),
        "description": fields.Text("Description"),
        "comments": fields.One2Many("message", "related_id", "Comments"),
        "full_name": fields.Char("Full Name", function="get_full_name"),
    }
    _order = "code"

    def get_full_name(self, ids, context={}):
        vals = {}
        for obj in self.browse(ids):
            n = obj.name
            p = obj.parent_id
            while p:
                n = p.name + " / " + n
                p = p.parent_id
            vals[obj.id] = n
        return vals

ContactCateg.register()
