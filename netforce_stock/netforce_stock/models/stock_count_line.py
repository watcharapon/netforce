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


class StockCountLine(Model):
    _name = "stock.count.line"
    _fields = {
        "count_id": fields.Many2One("stock.count", "Stock Count", required=True, on_delete="cascade"),
        "product_id": fields.Many2One("product", "Product", condition=[["type", "=", "stock"]], required=True),
        "lot_id": fields.Many2One("stock.lot", "Lot / Serial Number"),
        "bin_location": fields.Char("Bin Location", readonly=True),
        "prev_qty": fields.Decimal("Previous Qty", required=True, readonly=True),
        "new_qty": fields.Decimal("New Qty", required=True),
        "uom_id": fields.Many2One("uom", "UoM", required=True, readonly=True),
        "unit_price": fields.Decimal("Cost Price", scale=6),
    }

StockCountLine.register()
