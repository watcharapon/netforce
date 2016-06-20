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


class CopyPR2POLine(Model):
    _name="copy.pr2po.line"
    _trasient=True
    _fields={
        'pr2po_id': fields.Many2One("copy.pr2po","PR2PO", required=True, on_delete="cascade"),
        "product_id": fields.Many2One("product", "Product"),
        "description": fields.Text("Description", required=True),
        "qty": fields.Decimal("Qty", required=True),
        "unit_price": fields.Decimal("Unit Price", required=True),
        "uom_id": fields.Many2One("uom", "UoM", required=True),
        'amount': fields.Decimal("Amount",readonly=True),
        "location_id": fields.Many2One("stock.location", "Location", required=True, condition=[["type", "=", "internal"]]),
    }

CopyPR2POLine.register()
