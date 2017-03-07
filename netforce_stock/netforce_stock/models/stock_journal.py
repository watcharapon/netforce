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
from netforce.access import get_active_company


class StockJournal(Model):
    _name = "stock.journal"
    _string = "Stock Journal"
    _key = ["name"]
    _multi_company = True
    _fields = {
        "name": fields.Char("Name", required=True, search=True),
        "code": fields.Char("Code", search=True),
        "sequence_id": fields.Many2One("sequence", "Sequence", multi_company=True),
        "location_from_id": fields.Many2One("stock.location", "Location From", search=True, multi_company=True),
        "location_to_id": fields.Many2One("stock.location", "Location To", search=True, multi_company=True),
        "comments": fields.One2Many("message", "related_id", "Comments"),
        "company_id": fields.Many2One("company","Company"),
    }
    _order = "name"

    _defaults = {
        "company_id": lambda *a: get_active_company(),
    }

StockJournal.register()
