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
from netforce.utils import get_data_path
import time
from netforce.access import get_active_company
from netforce import database


class StockCount(Model):
    _name = "stock.count"
    _string = "Stock Count"
    _audit_log = True
    _name_field = "number"
    _multi_company = True
    _fields = {
        "number": fields.Char("Number", required=True, search=True),
        "location_id": fields.Many2One("stock.location", "Warehouse", condition=[["type", "=", "internal"]], required=True, search=True),
        "date": fields.Date("Date", required=True, search=True),
        "description": fields.Char("Description"),
        "state": fields.Selection([("draft", "Draft"), ("done", "Completed"), ("voided", "Voided")], "Status", required=True),
        "lines": fields.One2Many("stock.count.line", "count_id", "Lines"),
        "moves": fields.One2Many("stock.move", "related_id", "Stock Movements"),
        "comments": fields.One2Many("message", "related_id", "Comments"),
        "company_id": fields.Many2One("company", "Company"),
        "journal_id": fields.Many2One("stock.journal", "Journal"),
    }

    def _get_number(self, context={}):
        while 1:
            num = get_model("sequence").get_number("stock_count")
            if not num:
                return None
            res = self.search([["number", "=", num]])
            if not res:
                return num
            get_model("sequence").increment("stock_count")

    _defaults = {
        "state": "draft",
        "date": lambda *a: time.strftime("%Y-%m-%d"),
        "number": _get_number,
        "company_id": lambda *a: get_active_company(),
    }

    def fill_products(self, ids, context={}):
        obj = self.browse(ids)[0]
        if obj.lines:
            line_ids = [l.id for l in obj.lines]
            get_model("stock.count.line").delete(line_ids)
        loc_id = obj.location_id.id
        bal_ids = get_model("stock.balance").search([["location_id", "=", loc_id]])
        for bal in get_model("stock.balance").browse(bal_ids):
            if bal.qty_phys == 0:
                continue
            vals = {
                "count_id": obj.id,
                "product_id": bal.product_id.id,
                "lot_id": bal.lot_id.id,
                "bin_location": bal.product_id.bin_location,
                "prev_qty": bal.qty_phys,
                "new_qty": 0,
                "uom_id": bal.product_id.uom_id.id,
            }
            get_model("stock.count.line").create(vals)

    def onchange_product(self, context):
        data = context["data"]
        loc_id = data["location_id"]
        path = context["path"]
        line = get_data_path(data, path, parent=True)
        prod_id = line.get("product_id")
        if not prod_id:
            return {}
        prod = get_model("product").browse(prod_id)
        lot_id = line.get("lot_id")
        qty = get_model("stock.balance").get_qty_phys(loc_id, prod_id, lot_id)
        unit_price = get_model("stock.balance").get_unit_price(loc_id, prod_id)
        line["bin_location"] = prod.bin_location
        line["prev_qty"] = qty
        line["new_qty"] = qty
        line["unit_price"] = unit_price
        line["uom_id"] = prod.uom_id.id
        return data

    def validate(self, ids, context={}):
        obj = self.browse(ids)[0]
        settings = get_model("settings").browse(1)
        res = get_model("stock.location").search([["type", "=", "inventory"]])
        if not res:
            raise Exception("Inventory loss location not found")
        invent_loc_id = res[0]
        move_ids = []
        prod_ids = []
        line_no=0
        num_lines=len(obj.lines)
        db=database.get_connection()
        for line in obj.lines:
            line_no+=1
            print("line %s/%s"%(line_no,num_lines))
            prod_ids.append(line.product_id.id)
            if line.new_qty < line.prev_qty:
                qty = line.prev_qty - line.new_qty
                loc_from_id = obj.location_id.id
                loc_to_id = invent_loc_id
            elif line.new_qty > line.prev_qty:
                qty = line.new_qty - line.prev_qty
                loc_from_id = invent_loc_id
                loc_to_id = obj.location_id.id
            else:
                continue
            vals = {
                "journal_id": obj.journal_id.id or settings.stock_count_journal_id.id,
                "date": obj.date,
                "ref": obj.number,
                "product_id": line.product_id.id,
                "lot_id": line.lot_id.id,
                "location_from_id": loc_from_id,
                "location_to_id": loc_to_id,
                "qty": qty,
                "uom_id": line.uom_id.id,
                "cost_price": (line.unit_price or 0),
                "cost_amount": (line.unit_price or 0) * qty,
                "related_id": "stock.count,%d" % obj.id,
            }
            #move_id = get_model("stock.move").create(vals)
            number="%s/%s"%(obj.number,line_no)
            res=db.get("INSERT INTO stock_move (journal_id,date,ref,product_id,location_from_id,location_to_id,qty,uom_id,cost_price,cost_amount,related_id,state,number) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'draft',%s) RETURNING id",vals["journal_id"],vals["date"],vals["ref"],vals["product_id"],vals["location_from_id"],vals["location_to_id"],vals["qty"],vals["uom_id"],vals["cost_price"],vals["cost_amount"],vals["related_id"],number)
            move_id=res.id
            move_ids.append(move_id)
        get_model("stock.move").set_done(move_ids)
        obj.write({"state": "done"})
        prod_ids = list(set(prod_ids))
        if prod_ids:
            get_model("stock.compute.cost").compute_cost([], context={"product_ids": prod_ids})

    def void(self, ids, context={}):
        obj = self.browse(ids)[0]
        prod_ids = []
        for line in obj.lines:
            prod_ids.append(line.product_id.id)
        obj.moves.delete()
        obj.write({"state": "voided"})
        if prod_ids:
            get_model("stock.compute.cost").compute_cost([], context={"product_ids": prod_ids})

    def to_draft(self, ids, context={}):
        obj = self.browse(ids)[0]
        prod_ids = []
        for line in obj.lines:
            prod_ids.append(line.product_id.id)
        obj.moves.delete()
        obj.write({"state": "draft"})
        if prod_ids:
            get_model("stock.compute.cost").compute_cost([], context={"product_ids": prod_ids})

    def copy(self, ids, context={}):
        obj = self.browse(ids)[0]
        vals = {
            "location_id": obj.location_id.id,
            "date": obj.date,
            "lines": [],
        }
        for line in obj.lines:
            line_vals = {
                "product_id": line.product_id.id,
                "lot_id": line.lot_id.id,
                "bin_location": line.bin_location,
                "prev_qty": line.prev_qty,
                "new_qty": line.new_qty,
                "unit_price": line.unit_price,
                "uom_id": line.uom_id.id,
            }
            vals["lines"].append(("create", line_vals))
        new_id = self.create(vals)
        new_obj = self.browse(new_id)
        return {
            "next": {
                "name": "stock_count",
                "mode": "form",
                "active_id": new_id,
            },
            "flash": "Stock count %s copied from %s" % (new_obj.number, obj.number),
        }

    def delete(self, ids, **kw):
        move_ids = []
        for obj in self.browse(ids):
            for move in obj.moves:
                move_ids.append(move.id)
        get_model("stock.move").delete(move_ids)
        super().delete(ids, **kw)

StockCount.register()
