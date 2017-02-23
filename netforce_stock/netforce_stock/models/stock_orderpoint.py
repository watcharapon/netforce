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
from datetime import *
import time


class OrderPoint(Model):
    _name = "stock.orderpoint"
    _string = "Minimum Stock Rule"
    _fields = {
        "location_id": fields.Many2One("stock.location", "Warehouse", required=True, search=True),
        "product_id": fields.Many2One("product", "Product", required=True, search=True),
        "min_qty": fields.Decimal("Min Qty", required=True),
        "max_qty": fields.Decimal("Max Qty", required=True),
        "uom_id": fields.Many2One("uom", "UoM", required=True),
        "min_qty2": fields.Decimal("Min Qty2"),
        "max_qty2": fields.Decimal("Max Qty2"),
        "comments": fields.One2Many("message", "related_id", "Comments"),
    }

    def create(self, vals, **kw):
        id = super().create(vals, **kw)
        prod_id = vals["product_id"]
        get_model("product").write([prod_id], {"update_balance": True})
        return id

    def write(self, ids, vals, **kw):
        prod_ids = []
        for obj in self.browse(ids):
            prod_ids.append(obj.product_id.id)
        super().write(ids, vals, **kw)
        prod_id = vals.get("product_id")
        if prod_id:
            prod_ids.append(prod_id)
        get_model("product").write(prod_ids, {"update_balance": True})

    def delete(self, ids, **kw):
        prod_ids = []
        for obj in self.browse(ids):
            prod_ids.append(obj.product_id.id)
        super().delete(ids, **kw)
        get_model("product").write(prod_ids, {"update_balance": True})

    def onchange_product(self, context={}):
        data=context['data']
        product_id=data['product_id']
        product=get_model('product').browse(product_id)
        data['uom_id']=product.uom_id.id
        return data

OrderPoint.register()
