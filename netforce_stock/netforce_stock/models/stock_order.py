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

class StockOrder(Model):
    _name = "stock.order"
    _fields = {
        "lines": fields.One2Many("stock.order.line","order_id","Lines"),
        "confirm_orders": fields.Boolean("Confirm Orders"),
    }

    def _get_lines(self,context={}):
        if not context.get("product_ids"):
            return
        lines=self.get_product_order_qtys(context=context)
        return lines

    _defaults={
        "lines": _get_lines,
    }

    def get_product_order_qtys(self,context={}):
        print("StockOrder.get_product_order_qtys")
        loc_types={}
        for loc in get_model("stock.location").search_browse([]):
            loc_types[loc.id]=loc.type
        min_qtys={}
        for op in get_model("stock.orderpoint").search_browse([]):
            prod_id=op.product_id.id
            min_qtys.setdefault(prod_id,0)
            min_qtys[prod_id]+=op.min_qty
        print("min_qtys",min_qtys)
        res = get_total_qtys(None, None, None, None, ["done","pending","approved"], None)
        qtys_unlim={}
        for (prod_id,loc_from_id,loc_to_id),qty in res.items():
            qtys_unlim.setdefault(prod_id,0)
            if loc_types[loc_from_id]=="internal":
                qtys_unlim[prod_id]-=qty
            if loc_types[loc_to_id]=="internal":
                qtys_unlim[prod_id]+=qty
        print("qtys_unlim",qtys_unlim)
        if context.get("product_ids"):
            product_ids=context["product_ids"]
        else:
            product_ids=[]
            for prod_id,qty in qtys_unlim.items():
                min_qty=min_qtys.get(prod_id,0)
                if qty<min_qty:
                    product_ids.append(prod_id)
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
            res = get_total_qtys(None, None, None, date_to, ["done","pending","approved"], None)
            for (prod_id,loc_from_id,loc_to_id),qty in res.items():
                qtys_horiz[n].setdefault(prod_id,0)
                if loc_types[loc_from_id]=="internal":
                    qtys_horiz[n][prod_id]-=qty
                if loc_types[loc_to_id]=="internal":
                    qtys_horiz[n][prod_id]+=qty
        lines=[]
        product_ids.sort() # TODO: sort by code
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
                "qty": order_qty,
                "uom_id": order_uom.id,
                "supply_method": prod.supply_method,
                "supplier_id": prod.suppliers[0].supplier_id.id if prod.suppliers else None,
            }
            lines.append(line_vals)
        print("lines",lines)
        return lines

    def fill_products(self,ids,context={}):
        obj=self.browse(ids[0])
        obj.write({"lines":[("delete_all",)]})
        lines=self.get_product_order_qtys()
        n=0
        for line in lines:
            vals={
                "order_id": obj.id,
                "product_id": line["product_id"],
                "qty": line["qty"],
                "uom_id": line["uom_id"],
            }
            get_model("stock.order.line").create(vals)
            n+=1
        return {
            "flash": "%d lines added"%n,
        }

    def create_orders(self,ids,context={}):
        print("create_orders",ids)
        obj=self.browse(ids[0])
        res=obj.create_po()
        num_po=res["num_orders"]
        res=obj.create_mo()
        num_mo=res["num_orders"]
        return {
            "flash": "%d purchase orders and %s production orders created"%(num_po,num_mo),
        }

    def create_po(self,ids,context={}):
        obj=self.browse(ids[0])
        supplier_lines = {}
        for line in obj.lines:
            if line.supply_method!="purchase":
                continue
            supplier_id=line.supplier_id.id
            supplier_lines.setdefault(supplier_id,[]).append(line.id)
        n=0
        for supplier_id,line_ids in supplier_lines.items():
            vals={
                "contact_id": supplier_id,
                "lines": [],
            }
            for line in get_model("stock.order.line").browse(line_ids):
                prod=line.product_id
                if prod.purchase_uom_id and prod.purchase_uom_id.id!=prod.uom_id.id:
                    if not prod.purchase_to_stock_uom_factor:
                        raise Exception("Missing purchase to stock UoM factor for product %s"%prod.code)
                    qty_stock=line.qty*prod.purchase_to_stock_uom_factor
                else:
                    qty_stock=None
                if not prod.purchase_price:
                    raise Exception("Missing purchase price for product %s"%prod.code)
                if not prod.locations:
                    raise Exception("Missing stock locations for product %s"%prod.code)
                loc_id=prod.locations[0].location_id.id
                line_vals={
                    "product_id": prod.id,
                    "description": prod.description,
                    "qty": line.qty,
                    "uom_id": line.uom_id.id,
                    "unit_price": prod.purchase_price,
                    "qty_stock": qty_stock,
                    "location_id": loc_id,
                }
                vals["lines"].append(("create",line_vals))
            order_id=get_model("purchase.order").create(vals)
            if obj.confirm_orders:
                get_model("purchase.order").confirm([order_id])
            n+=1
        return {
            "num_orders": n,
        }

    def create_mo(self,ids,context={}):
        obj=self.browse(ids[0])
        n=0
        for line in obj.lines:
            if line.supply_method!="production":
                continue
            prod = line.product_id
            res=get_model("bom").search([["product_id","=",prod.id]])
            if not res:
                raise Exception("BoM not found for product '%s'" % prod.name)
            bom_id = res[0]
            bom = get_model("bom").browse(bom_id)
            loc_id = bom.location_id.id
            if not loc_id:
                raise Exception("Missing FG location in BoM %s" % bom.number)
            routing = bom.routing_id
            if not routing:
                raise Exception("Missing routing in BoM %s" % bom.number)
            loc_prod_id = routing.location_id.id
            if not loc_prod_id:
                raise Exception("Missing production location in routing %s" % routing.number)
            uom = prod.uom_id
            order_date=time.strftime("%Y-%m-%d")
            if not prod.mfg_lead_time:
                raise Exception("Missing manufacturing lead time in product %s"%prod.code)
            due_date=(datetime.strptime(order_date,"%Y-%m-%d")+timedelta(days=prod.mfg_lead_time)).strftime("%Y-%m-%d")
            order_vals = {
                "product_id": prod.id,
                "qty_planned": line.qty,
                "uom_id": line.uom_id.id,
                "bom_id": bom_id,
                "routing_id": routing.id,
                "production_location_id": loc_prod_id,
                "location_id": loc_id,
                "order_date": order_date,
                "due_date": due_date,
                "state": "waiting_confirm",
            }
            order_id = get_model("production.order").create(order_vals)
            get_model("production.order").create_components([order_id])
            get_model("production.order").create_operations([order_id])
            if obj.confirm_orders:
                get_model("production.order").confirm([order_id])
            n+=1
        return {
            "num_orders": n,
        }

StockOrder.register()
