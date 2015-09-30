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
from netforce import config
from netforce import database
from netforce import access

OL_MAX_COMPANIES = {
    "demo": 2,
    "free": 1,
    "starter": 5,
    "business": 6,
    "enterprise": None,
}

DL_MAX_COMPANIES = {
    "demo": 2,
    "free": 1,
    "starter": 5,
    "business": 6,
    "enterprise": None,
}


class Company(Model):
    _name = "company"
    _string = "Company"
    _key = ["name"]
    _fields = {
        "name": fields.Char("Company Name", required=True, search=True, translate=True),
        "code": fields.Char("Company Code", search=True),
        "parent_id": fields.Many2One("company", "Parent"),
        "description": fields.Text("Description"),
        "comments": fields.One2Many("message", "related_id", "Comments"),
        "contact_id": fields.Many2One("contact","Contact"),
    }
    _order = "name"

    def get_max_companies(self):
        settings = get_model("settings").browse(1)
        if settings.package == None:
            package = "demo"
        else:
            package = settings.package
        if config.get("sub_server"):
            max_companies = OL_MAX_COMPANIES[package]
        else:
            max_companies = DL_MAX_COMPANIES[package]
        return max_companies

    def check_max_companies(self):
        max_companies = self.get_max_companies()
        if max_companies is None:
            return
        db = database.get_connection()
        #num_company=db.get("SELECT COUNT(*) FROM company WHERE active").count
        num_companies = db.get("SELECT COUNT(*) FROM company").count
        if num_companies > max_companies:
            raise Exception("Maximum number of companies exceeded. Please upgrade your package.")

    def create(self, vals, **kw):
        res = super().create(vals, **kw)
        db = database.get_connection()
        self.check_max_companies()
        return res

Company.register()
