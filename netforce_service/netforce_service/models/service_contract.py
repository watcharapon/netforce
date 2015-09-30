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
import time
from netforce.utils import get_data_path


class ServiceContract(Model):
    _name = "service.contract"
    _string = "Service Contract"
    _audit_log = True
    _name_field = "number"
    _fields = {
        "number": fields.Char("Number", required=True),
        "contact_id": fields.Many2One("contact", "Customer"),
        "project_id": fields.Many2One("project", "Project"),
        "comments": fields.One2Many("message", "related_id", "Comments"),
        "documents": fields.One2Many("document", "related_id", "Documents"),
        "start_date": fields.Date("Start Date", required=True),
        "end_date": fields.Date("End Date"),
        "lines": fields.One2Many("service.contract.line", "contract_id", "Lines"),
        "jobs": fields.One2Many("job", "contract_id", "Service Orders"),
        "state": fields.Selection([["draft", "Draft"], ["confirmed", "Confirmed"]], "Status", required=True),
        "invoices": fields.One2Many("account.invoice", "related_id", "Invoices"),
        "invoice_period": fields.Selection([["month", "Month"], ["3month", "3 Months"], ["6month", "6 Months"], ["year", "Year"]], "Invoice Period"),
        "num_periods": fields.Decimal("Number of Periods"),
        "amount_period": fields.Decimal("Amount per Period"),
        "next_invoice_date": fields.Date("Next Invoice Date"),
        "incl_labor": fields.Boolean("Include Labor"),
        "incl_part": fields.Boolean("Include Parts"),
        "incl_other": fields.Boolean("Include Other Costs"),
        "amount_labor": fields.Decimal("Labor Amount", function="get_total", function_multi=True),
        "amount_part": fields.Decimal("Parts Amount", function="get_total", function_multi=True),
        "amount_other": fields.Decimal("Other Amount", function="get_total", function_multi=True),
        "amount_total": fields.Decimal("Total Amount", function="get_total", function_multi=True),
        "amount_contract": fields.Decimal("Contract Amount", function="get_total", function_multi=True),
    }

    def _get_number(self, context={}):
        seq_id = get_model("sequence").find_sequence(type="service_contract")
        if not seq_id:
            return None
        while 1:
            num = get_model("sequence").get_next_number(seq_id, context=context)
            res = self.search([["number", "=", num]])
            if not res:
                return num
            get_model("sequence").increment_number(seq_id, context=context)

    _defaults = {
        "number": _get_number,
        "start_date": lambda *a: time.strftime("%Y-%m-%d"),
        "state": "draft",
    }

    def create_jobs(self, ids, context={}):
        obj = self.browse(ids)[0]
        for line in obj.lines:
            tmpl = line.template_id
            tmpl.create_jobs(contract_line_id=line.id)

    def get_total(self, ids, context={}):
        vals = {}
        for obj in self.browse(ids):
            amt_labor = sum([l.amount_labor or 0 for l in obj.lines])
            amt_part = sum([l.amount_part or 0 for l in obj.lines])
            amt_other = sum([l.amount_other or 0 for l in obj.lines])
            amt_total = amt_labor + amt_part + amt_other
            amt_contract = 0
            if obj.incl_labor:
                amt_contract += amt_labor
            if obj.incl_part:
                amt_contract += amt_part
            if obj.incl_other:
                amt_contract += amt_other
            vals[obj.id] = {
                "amount_labor": amt_labor,
                "amount_part": amt_part,
                "amount_other": amt_other,
                "amount_total": amt_total,
                "amount_contract": amt_contract,
            }
        return vals

    def onchange_period(self, context={}):
        data = context["data"]
        period = data["invoice_period"]
        start_date = data["start_date"]
        end_date = data["end_date"]
        days = (datetime.strptime(end_date, "%Y-%m-%d") - datetime.strptime(start_date, "%Y-%m-%d")).days
        if period == "month":
            num_periods = int(days / 30)
        elif period == "3month":
            num_periods = int(days / 90)
        elif period == "6month":
            num_periods = int(days / 180)
        elif period == "year":
            num_periods = int(days / 365)
        amount_period = data["amount_contract"] / num_periods
        data["num_periods"] = num_periods
        data["amount_period"] = amount_period
        return data

    def create_invoice(self, ids, context={}):
        obj = self.browse(ids)[0]
        if not obj.next_invoice_date:
            raise Exception("Missing next invoice date")
        inv_vals = {
            "type": "out",
            "inv_type": "invoice",
            "ref": obj.number,
            "related_id": "service.contract,%s" % obj.id,
            "contact_id": obj.contact_id.id,
            "due_date": obj.next_invoice_date,
            "lines": [],
        }
        if not obj.num_periods:
            raise Exception("Missing number of periods")
        for line in obj.lines:
            amt_contract = 0
            if obj.incl_labor:
                amt_contract += line.amount_labor or 0
            if obj.incl_part:
                amt_contract += line.amount_part or 0
            if obj.incl_other:
                amt_contract += line.amount_other or 0
            amt = amt_contract / obj.num_periods
            if not line.account_id:
                raise Exception("Missing account in service contract line")
            line_vals = {
                "description": line.service_item_id.name_get()[0][1],
                "account_id": line.account_id.id,
                "tax_id": line.account_id.tax_id.id,
                "amount": amt,
            }
            inv_vals["lines"].append(("create", line_vals))
        inv_id = get_model("account.invoice").create(inv_vals, {"type": "out", "inv_type": "invoice"})
        inv = get_model("account.invoice").browse(inv_id)
        d = datetime.strptime(obj.next_invoice_date, "%Y-%m-%d")
        if obj.invoice_period == "month":
            d += relativedelta(months=1)
        elif obj.invoice_period == "3month":
            d += relativedelta(months=3)
        elif obj.invoice_period == "6month":
            d += relativedelta(months=6)
        elif obj.invoice_period == "year":
            d += relativedelta(months=12)
        obj.write({"next_invoice_date": d.strftime("%Y-%m-%d")})
        return {
            "flash": "Invoice %s created for service contract %s" % (inv.number, obj.number),
        }

    def onchange_template(self, context={}):
        data = context["data"]
        path = context["path"]
        line = get_data_path(data, path, parent=True)
        tmpl_id = line["template_id"]
        tmpl = get_model("service.contract.template").browse(tmpl_id)
        line["amount_labor"] = tmpl.amount_labor
        line["amount_part"] = tmpl.amount_part
        line["amount_other"] = tmpl.amount_other
        return data

ServiceContract.register()
