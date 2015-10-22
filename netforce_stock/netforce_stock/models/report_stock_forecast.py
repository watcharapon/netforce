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


def get_periods(date, period_days, num_periods):
    periods = []
    d0 = datetime.strptime(date, "%Y-%m-%d")
    date_from = d0 + timedelta(days=0)
    date_to = d0 + timedelta(days=period_days - 1)
    period={
        "date_from": date_from.strftime("%Y-%m-%d"),
        "date_to": date_to.strftime("%Y-%m-%d"),
        "period_name": "%d-%d days" % ((date_from - d0).days, (date_to - d0).days),
    }
    periods.append(period)
    for i in range(num_periods - 1):
        date_from = date_from + timedelta(days=period_days)
        date_to = date_to + timedelta(days=period_days)
        period={
            "date_from": date_from.strftime("%Y-%m-%d"),
            "date_to": date_to.strftime("%Y-%m-%d"),
            "period_name": "%d-%d days" % ((date_from - d0).days, (date_to - d0).days),
        }
        periods.append(period)
    return periods


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


class ReportStockForecast(Model):
    _name = "report.stock.forecast"
    _transient = True
    _fields = {
        "date": fields.Date("Start Date", required=True),
        "location_id": fields.Many2One("stock.location", "Location", on_delete="cascade"),
        "categ_id": fields.Many2One("product.categ", "Product Category", on_delete="cascade"),
        "product_id": fields.Many2One("product", "Product", on_delete="cascade"),
        "period_days": fields.Integer("Period Days", required=True),
        "num_periods": fields.Integer("Number of Periods", required=True),
    }
    _defaults = {
        "date": lambda *a: date.today().strftime("%Y-%m-%d"),
        "period_days": 1,
        "num_periods": 28,
    }

    def get_report_data(self, ids, context={}):
        company_id = get_active_company()
        comp = get_model("company").browse(company_id)
        if ids:
            params = self.read(ids, load_m2o=False)[0]
        else:
            params = self.default_get(load_m2o=False, context=context)
        settings = get_model("settings").browse(1)
        date = params.get("date")
        if not date:
            return
        location_id = params.get("location_id")
        if location_id:
            location = get_model("stock.location").browse(location_id)
        else:
            location = None
        product_id = params.get("product_id")
        if product_id:
            product = get_model("product").browse(product_id)
        else:
            product = None
        categ_id = params.get("categ_id")
        period_days = params.get("period_days")
        if not period_days:
            return
        period_days = int(period_days)
        num_periods = params.get("num_periods")
        if not num_periods:
            return
        num_periods = int(num_periods)
        periods = get_periods(date, period_days, num_periods)
        date_to0 = (datetime.strptime(date, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
        qtys0 = get_total_qtys(product_id, location_id, None, date_to0, ["done"], categ_id)
        print("qtys0", qtys0)
        prod_locs = set([])
        for prod_id, loc_from_id, loc_to_id in qtys0:
            prod_locs.add((prod_id, loc_from_id))
            prod_locs.add((prod_id, loc_to_id))
        for period in periods:
            period["qtys"] = get_total_qtys(
                product_id, location_id, period["date_from"], period["date_to"], ["done", "pending"], categ_id)
            for prod_id, loc_from_id, loc_to_id in period["qtys"]:
                prod_locs.add((prod_id, loc_from_id))
                prod_locs.add((prod_id, loc_to_id))
        print("prod_locs", prod_locs)

        def get_balance_qty(prod_id, loc_id, qtys):
            bal = 0
            for (prod_id_, loc_from_id, loc_to_id), qty in qtys.items():
                if prod_id_ != prod_id:
                    continue
                if loc_to_id == loc_id and loc_from_id != loc_id:
                    bal += qty
                elif loc_from_id == loc_id and loc_to_id != loc_id:
                    bal -= qty
            return bal
        lines = []
        for prod_id, loc_id in prod_locs:
            loc = get_model("stock.location").browse(loc_id)
            if loc.type != "internal":
                continue
            prod = get_model("product").browse(prod_id)
            qty = get_balance_qty(prod_id, loc_id, qtys0)
            line = {
                "product_id": prod.id,
                "product_name": prod.name,
                "code": prod.code,
                "location_id": loc.id,
                "location_name": loc.name,
                "qty": qty,
                "periods": [],
            }
            for period in periods:
                period_qty = get_balance_qty(prod_id, loc_id, period["qtys"])
                qty += period_qty
                line["periods"].append({
                    "date_from": period["date_from"],
                    "date_to": period["date_to"],
                    "qty": qty,
                    "warning": qty < 0,
                })
            lines.append(line)
        lines.sort(key=lambda l: (l["product_name"], l["location_name"]))
        print("lines", lines)
        for period in periods:
            del period["qtys"]
        data = {
            "company_name": comp.name,
            "location_name": location and location.name or None,
            "product_name": product and product.name or None,
            "date": date,
            "periods": periods,
            "lines": lines,
            "period_days": period_days,
        }
        return data

ReportStockForecast.register()
