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
from netforce.database import get_connection


def get_totals(date_from, date_to, product_id=None, lot_id=None, location_id=None, container_id=None):
    q = "SELECT product_id,lot_id,location_from_id,container_from_id,location_to_id,container_to_id,uom_id,SUM(qty) AS total_qty,SUM(unit_price*qty) AS total_amt,SUM(qty2) AS total_qty2 FROM stock_move WHERE state='done'"
    q_args = []
    if date_from:
        q += " AND date>=%s"
        q_args.append(date_from + " 00:00:00")
    if date_to:
        q += " AND date<=%s"
        q_args.append(date_to + " 23:59:59")
    if product_id:
        q += " AND product_id=%s"
        q_args.append(product_id)
    if lot_id:
        q += " AND lot_id=%s"
        q_args.append(lot_id)
    if location_id:
        q += " AND (location_from_id=%s OR location_to_id=%s)"
        q_args += [location_id, location_id]
    if container_id:
        q += " AND (container_from_id=%s OR container_to_id=%s)"
        q_args += [container_id, container_id]
    q += " GROUP BY product_id,lot_id,location_from_id,container_from_id,location_to_id,container_to_id,uom_id"
    db = get_connection()
    res = db.query(q, *q_args)
    totals = {}
    for r in res:
        prod = get_model("product").browse(r.product_id)
        uom = get_model("uom").browse(r.uom_id)
        qty = r.total_qty * uom.ratio / prod.uom_id.ratio
        amt = r.total_amt or 0
        qty2 = r.total_qty2 or 0
        k = (r.product_id, r.lot_id, r.location_from_id, r.container_from_id, r.location_to_id, r.container_to_id)
        tot = totals.setdefault(k, [0, 0, 0])
        tot[0] += qty
        tot[1] += amt
        tot[2] += qty2
    return totals


class StockContainer(Model):
    _name = "stock.container"
    _string = "Container"
    _name_field = "number"
    _key = ["number"]
    _fields = {
        "number": fields.Char("Number", required=True, search=True),
        "description": fields.Text("Description", search=True),
        "comments": fields.One2Many("message", "related_id", "Comments"),
        "documents": fields.One2Many("document", "related_id", "Documents"),
        "pickings": fields.One2Many("stock.picking", "container_id", "Pickings"),
    }
    _order = "number desc"

    def _get_number(self, context={}):
        seq_id = get_model("sequence").find_sequence(type="stock_container")
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

    def get_contents(self, ids, context={}):
        obj = self.browse(ids)[0]
        date_to = context.get("date")
        tots = get_totals(None, date_to, container_id=obj.id)

        def get_sum(prod=None, lot=None, loc_from=None, loc_to=None, cont_from=None, cont_to=None):
            tot_qty = 0
            tot_amt = 0
            tot_qty2 = 0
            for (prod_id, lot_id, loc_from_id, cont_from_id, loc_to_id, cont_to_id), (qty, amt, qty2) in tots.items():
                if prod and prod_id != prod:
                    continue
                if (lot and lot_id != lot) or (not lot and lot_id):
                    continue
                if loc_from and loc_from_id != loc_from:
                    continue
                if loc_to and loc_to_id != loc_to:
                    continue
                if cont_from and cont_from_id != cont_from:
                    continue
                if cont_to and cont_to_id != cont_to:
                    continue
                tot_qty += qty
                tot_amt += amt
                tot_qty2 += qty2
            return tot_qty, tot_amt, tot_qty2
        prod_locs = set()
        for (prod_id, lot_id, loc_from_id, cont_from_id, loc_to_id, cont_to_id), (qty, amt, qty2) in tots.items():
            prod_locs.add((prod_id, lot_id, loc_from_id, cont_from_id))
            prod_locs.add((prod_id, lot_id, loc_to_id, cont_to_id))
        contents = {}
        for prod_id, lot_id, loc_id, cont_id in prod_locs:
            if cont_id != obj.id:
                continue
            qty_in, amt_in, qty2_in = get_sum(prod=prod_id, lot=lot_id, loc_to=loc_id, cont_to=cont_id)
            qty_out, amt_out, qty2_out = get_sum(prod=prod_id, lot=lot_id, loc_from=loc_id, cont_from=cont_id)
            qty = qty_in - qty_out
            amt = amt_in - amt_out
            qty2 = qty2_in - qty2_out
            if qty <= 0:
                continue
            contents[(prod_id, lot_id, loc_id)] = (qty, amt, qty2)
        return contents

StockContainer.register()
