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


class StockLot(Model):
    _name = "stock.lot"
    _string = "Lot / Serial Number"
    _name_field = "number"
    _key = ["number"]
    _fields = {
        "number": fields.Char("Number", required=True, search=True),
        "received_date": fields.DateTime("Received Date", search=True),
        "expiry_date": fields.Date("Expiry Date", search=True),
        "description": fields.Text("Description", search=True),
        "weight": fields.Decimal("Weight"),
        "width": fields.Decimal("Width"),
        "length": fields.Decimal("Length"),
        "comments": fields.One2Many("message", "related_id", "Comments"),
        "service_item_id": fields.Many2One("service.item","Service Item"),
        "product_id": fields.Many2One("product","Product",search=True),
        "stock_balances": fields.One2Many("stock.balance","lot_id","Stock Quantities"),
    }
    _order = "number desc"

    def _get_number(self, context={}):
        seq_id = get_model("sequence").find_sequence("stock_lot")
        if not seq_id:
            return None
        while 1:
            num = get_model("sequence").get_next_number(seq_id)
            res = self.search([["number", "=", num]])
            if not res:
                return num
            get_model("sequence").increment_number(seq_id)

    _defaults = {
        "number": _get_number,
    }

StockLot.register()
