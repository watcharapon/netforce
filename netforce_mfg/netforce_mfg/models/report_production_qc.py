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
from dateutil.relativedelta import *
from datetime import *


class ReportProductionQC(Model):
    _name = "report.production.qc"
    _transient = True
    _fields = {
        "date_from": fields.Date("Order Date From"),
        "date_to": fields.Date("Order Date To"),
        "product_id": fields.Many2One("product", "Product"),
        "result": fields.Selection([["yes", "Pass"], ["no", "Not Pass"], ["na", "N/A"]], "Result"),
        "production_location_id": fields.Many2One("stock.location", "Production Location"),
    }

    def default_get(self, field_names={}, context={}, **kw):
        defaults = context.get("defaults", {})
        date_from = defaults.get("date_from")
        date_to = defaults.get("date_to")
        if not date_from and not date_to:
            date_from = date.today().strftime("%Y-%m-01")
            date_to = (date.today() + relativedelta(day=31)).strftime("%Y-%m-%d")
            defaults["date_from"] = date_from
            defaults["date_to"] = date_to
        elif not date_from and date_to:
            date_from = get_model("settings").get_fiscal_year_start(date=date_to)
            defaults["date_from"] = date_from
        return defaults

    def get_report_data(self, ids, context={}):
        if ids:
            params = self.read(ids, load_m2o=False)[0]
        else:
            params = self.default_get(load_m2o=False, context=context)
        condition = []
        if params.get("date_from"):
            date_from = params.get("date_from") + " 00:00:00"
            condition.append(["order_id.order_date", ">=", date_from])
        if params.get("date_to"):
            date_to = params.get("date_to") + " 23:59:59"
            condition.append(["order_id.order_date", "<=", date_to])
        if params.get("product_id"):
            condition.append(["order_id.product_id", "=", params.get("product_id")])
        if params.get("result"):
            condition.append(["result", "=", params.get("result")])
        if params.get("production_location"):
            condition.append(["order_id.production_location_id", "=", params.get("production_location_id")])
        prod_qc_list = get_model("production.qc").search_browse(condition)
        lines = []
        item_no = 0
        result_map = {
            "yes": "Pass",
            "no": "Not Pass",
            "na": "N/A",
        }
        for prod_qc in prod_qc_list:
            item_no += 1
            line = self.get_line_data(context={"prod_qc": prod_qc})
            line["result"] = result_map[line["result"]] if line["result"] in result_map else line["result"]
            line["_item_no"] = item_no
            lines.append(line)
        return {"lines": lines}

    def get_line_data(self, context={}):
        obj = context["prod_qc"]
        vals = {}
        vals["order_date"] = obj.order_id.order_date
        vals["number"] = obj.order_id.number
        vals["product_code"] = obj.order_id.product_id.code
        vals["product_name"] = obj.order_id.product_id.name
        vals["sale_order_number"] = obj.order_id.sale_id.number
        vals["test"] = obj.test_id.name
        vals["sample_qty"] = obj.sample_qty
        vals["min_value"] = obj.min_value
        vals["max_value"] = obj.max_value
        vals["value"] = obj.value
        vals["result"] = obj.result
        return vals

ReportProductionQC.register()
