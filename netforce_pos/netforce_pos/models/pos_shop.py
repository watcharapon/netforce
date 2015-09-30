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


class Shop(Model):
    _name = "pos.shop"
    _string = "Shop"

    _fields = {
        "name": fields.Char("Name", required=True),
        "categ_id": fields.Many2One("product.categ", "Product Category"),
        "cash_account_id": fields.Many2One("account.account", "Cash Account", required=True, condition=[["type", "in", ("bank", "cash", "cheque")]]),
        "disc_account_id": fields.Many2One("account.account", "Discount Account", required=True),
        "location_id": fields.Many2One("stock.location", "Stock Location", condition=[['type', '=', 'internal']], required=True),
        "registers": fields.One2Many("pos.register", "shop_id", "Registers"),
        "comments": fields.One2Many("message", "related_id", "Comments"),
        "addresses": fields.One2Many("address", "shop_id", "Address"),
        "company_id": fields.Many2One("company", "Company"),
    }

    def get_address_str(self, ids, context={}):
        obj = self.browse(ids[0])
        if not obj.addresses:
            return ""
        addr = obj.addresses[0]
        return addr.name_get()[0][1]

Shop.register()
