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
from dateutil.relativedelta import *
from netforce.access import get_active_company
from netforce.database import get_connection
import math

def get_total_qtys(prod_id, loc_id, date_from, date_to, states, categ_id):
    db = get_connection()
    q = "SELECT " \
        " t1.product_id,t1.location_from_id,t1.location_to_id,t1.uom_id,SUM(t1.qty) AS total_qty " \
        " FROM stock_move t1 " \
        " LEFT JOIN product t2 on t1.product_id=t2.id " \
        " WHERE t1.state IN %s"
    q_args = [tuple(states)]
    if date_from:
        q += " AND t1.date>=%s"
        q_args.append(date_from + " 00:00:00")
    if date_to:
        q += " AND t1.date<=%s"
        q_args.append(date_to + " 23:59:59")
    if prod_id:
        q += " AND t1.product_id=%s"
        q_args.append(prod_id)
    if loc_id:
        q += " AND (t1.location_from_id=%s OR t1.location_to_id=%s)"
        q_args += [loc_id, loc_id]
    if categ_id:
        q += " AND t2.categ_id=%s"
        q_args.append(categ_id)
    company_id = get_active_company()
    if company_id:
        q += " AND t1.company_id=%s"
        q_args.append(company_id)
    q += " GROUP BY t1.product_id,t1.location_from_id,t1.location_to_id,t1.uom_id"
    print("q",q)
    print("q_args",q_args)
    res = db.query(q, *q_args)
    totals = {}
    for r in res:
        prod = get_model("product").browse(r.product_id)
        uom = get_model("uom").browse(r.uom_id)
        qty = r.total_qty * uom.ratio / prod.uom_id.ratio
        k = (r.product_id, r.location_from_id, r.location_to_id)
        totals.setdefault(k, 0)
        totals[k] += qty
    return totals

class ReportStockPlan(Model):
    _name = "report.stock.plan"
    _transient = True
    _fields = {
        "product_id": fields.Many2One("product", "Product", on_delete="cascade"),
        "product_categ_id": fields.Many2One("product.categ", "Product Category", on_delete="cascade"),
        "supplier_id": fields.Many2One("contact","Supplier"),
    }

    def get_report_data(self, ids, context={}):
        settings = get_model("settings").browse(1)
        company_id = get_active_company()
        comp = get_model("company").browse(company_id)
        if ids:
            params = self.read(ids, load_m2o=False)[0]
        else:
            params = self.default_get(load_m2o=False, context=context)
        product_id=params.get("product_id")
        categ_id=params.get("product_categ_id")
        supplier_id=params.get("supplier_id")
        loc_types={}
        for loc in get_model("stock.location").search_browse([]):
            loc_types[loc.id]=loc.type
        min_qtys={}
        for op in get_model("stock.orderpoint").search_browse([]):
            prod_id=op.product_id.id
            min_qtys.setdefault(prod_id,0)
            min_qtys[prod_id]+=op.min_qty
        print("min_qtys",min_qtys)
        res = get_total_qtys(product_id, None, None, None, ["done","pending","approved"], categ_id)
        qtys_unlim={}
        for (prod_id,loc_from_id,loc_to_id),qty in res.items():
            qtys_unlim.setdefault(prod_id,0)
            if loc_types[loc_from_id]=="internal":
                qtys_unlim[prod_id]-=qty
            if loc_types[loc_to_id]=="internal":
                qtys_unlim[prod_id]+=qty
        print("qtys_unlim",qtys_unlim)
        product_ids=[]
        for prod_id,qty in qtys_unlim.items():
            min_qty=min_qtys.get(prod_id,0)
            if qty<min_qty:
                product_ids.append(prod_id)
        if supplier_id:
            prod_ids2=[]
            for prod in get_model("product").browse(product_ids):
                if prod.suppliers and prod.suppliers[0].supplier_id.id==supplier_id:
                    prod_ids2.append(prod.id)
            product_ids=prod_ids2
        print("product_ids",product_ids)
        horizons={}
        for prod in get_model("product").browse(product_ids):
            if prod.stock_plan_horizon is None:
                continue
            horizons.setdefault(prod.stock_plan_horizon,[]).append(prod.id)
        qtys_horiz={}
        for n,prod_ids in horizons.items():
            print("calc horizon %s"%n)
            qtys_horiz[n]={}
            date_to=(date.today()+timedelta(days=n)).strftime("%Y-%m-%d")
            res = get_total_qtys(product_id, None, None, date_to, ["done","pending","approved"], categ_id)
            for (prod_id,loc_from_id,loc_to_id),qty in res.items():
                qtys_horiz[n].setdefault(prod_id,0)
                if loc_types[loc_from_id]=="internal":
                    qtys_horiz[n][prod_id]-=qty
                if loc_types[loc_to_id]=="internal":
                    qtys_horiz[n][prod_id]+=qty
        lines=[]
        for prod in get_model("product").browse(product_ids):
            plan_days=prod.stock_plan_horizon
            qty_unlim=qtys_unlim.get(prod.id,0)
            if plan_days is not None:
                qty_horiz=qtys_horiz[plan_days].get(prod.id)
            else:
                qty_horiz=qty_unlim
            min_qty=min_qtys.get(prod.id,0)
            req_qty=min_qty-qty_horiz
            if prod.supply_method=="purchase":
                supply_method="Purchase"
                if prod.purchase_uom_id and prod.purchase_uom_id.id!=prod.uom_id.id:
                    order_uom=prod.purchase_uom_id
                    if not prod.purchase_to_stock_uom_factor:
                        raise Exception("Missing purchase to stock UoM factor for product %s"%prod.code)
                    order_qty=req_qty/prod.purchase_to_stock_uom_factor
                    if prod.purchase_min_qty and order_qty<prod.purchase_min_qty:
                        order_qty=prod.purchase_min_qty
                    if prod.purchase_qty_multiple:
                        n=math.ceil(order_qty/prod.purchase_qty_multiple)
                        order_qty=n*prod.purchase_qty_multiple
                else:
                    order_uom=prod.uom_id
                    order_qty=req_qty
            elif prod.supply_method=="production":
                supply_method="Production"
                order_uom=prod.uom_id
                order_qty=req_qty
            else:
                raise Exception("Invalid supply method")
            line_vals={
                "product_id": prod.id,
                "product_code": prod.code,
                "product_name": prod.name,
                "plan_days": plan_days,
                "plan_qty_horiz": qty_horiz,
                "plan_qty_unlim": qty_unlim,
                "min_qty": min_qty,
                "req_qty": req_qty,
                "stock_uom_name": prod.uom_id.name,
                "order_qty": order_qty,
                "order_uom_name": order_uom.name,
                "below_min": qty_horiz<min_qty,
                "supply_method": supply_method,
                "supplier_name": prod.suppliers and prod.suppliers[0].supplier_id.name or None,
            }
            lines.append(line_vals)
        lines.sort(key=lambda l: l["product_code"])
        print("lines",lines)
        data = {
            "company_name": comp.name,
            "lines": lines,
        }
        return data

ReportStockPlan.register()
