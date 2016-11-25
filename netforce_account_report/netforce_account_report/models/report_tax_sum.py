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
from netforce import database
from netforce.access import get_active_company

class ReportTaxSum(Model):
    _name = "report.tax.sum"
    _transient = True
    _fields = {
        "date_from": fields.Date("From"),
        "date_to": fields.Date("To"),
        "by_rate": fields.Boolean("Show by Tax Rate"),
        "by_comp": fields.Boolean("Show by Tax Component"),
    }

    _defaults = {
        "date_from": lambda *a: date.today().strftime("%Y-%m-01"),
        "date_to": lambda *a: (date.today() + relativedelta(day=31)).strftime("%Y-%m-%d"),
        "by_comp": True,
    }

    def group_items(self, items, group_field="", sum_field="",context={}):
        res=[]
        ctx = context or {}
        sum_fields = sum_field.split(",")
        groups = {}
        group_list = []
        for item in items:
            v = item.get(group_field)
            group = groups.get(v)
            if not group:
                group = {}
                group[group_field] = v
                group["group_items"] = []
                group["context"] = ctx
                group["sum"] = {}
                for f in sum_fields:
                    group["sum"][f] = 0
                groups[v] = group
                group_list.append(v)
            group["group_items"].append(item)
            for f in sum_fields:
                v = item.get(f)
                if v:
                    group["sum"][f] += v
        if group_list:
            for v in group_list:
                group = groups[v]
                data = group.copy()
                res.append(data)
        return res

    def get_report_data(self, ids, context={}):
        company_id = get_active_company()
        company_ids = get_model("company").search([["id", "child_of", company_id]])
        comp = get_model("company").browse(company_id)
        if ids:
            params = self.read(ids, load_m2o=False)[0]
        else:
            params = self.default_get(load_m2o=False, context=context)
        settings = get_model("settings").browse(1)
        date_from = params.get("date_from")
        if not date_from:
            date_from = date.today().strftime("%Y-%m-01")
        date_to = params.get("date_to")
        if not date_to:
            date_to = (date.today() + relativedelta(day=31)).strftime("%Y-%m-%d")
        data = {
            "company_name": comp.name,
            "date_from": date_from,
            "date_to": date_to,
            "by_rate": params.get("by_rate"),
            "by_comp": params.get("by_comp"),
        }
        db = database.get_connection()
        if params.get("by_comp"):
            res = db.query("SELECT c.id AS comp_id,c.name AS comp_name,c.rate AS comp_rate,r.name AS rate_name,SUM(l.credit-l.debit) AS tax_total,SUM(l.tax_base*sign(l.credit-l.debit)) AS base_total,c.type AS tax_comp_type, SUM(l.tax_base) AS base_total_exempt FROM account_move_line l,account_move m,account_tax_component c,account_tax_rate r WHERE m.id=l.move_id AND m.state='posted' AND m.date>=%s AND m.date<=%s AND c.id=l.tax_comp_id AND r.id=c.tax_rate_id AND m.company_id IN %s GROUP BY comp_id,comp_name,comp_rate,rate_name ORDER BY comp_name,rate_name",
                           date_from, date_to, tuple(company_ids))
            data["comp_taxes"] = []
            ## get tax base only if type = vat_exempt
            for r in res:
                if r.tax_comp_type == "vat_exempt":
                   r["base_total"] = r["base_total_exempt"]
                data["comp_taxes"].append(dict(r))
        if params.get("by_rate"):
            res = db.query("SELECT c.id AS comp_id,c.name AS comp_name,c.rate AS comp_rate,r.name AS rate_name,SUM(l.credit-l.debit) AS tax_total,SUM(l.tax_base*sign(l.credit-l.debit)) AS base_total,c.type AS tax_comp_type, SUM(l.tax_base) AS base_total_exempt FROM account_move_line l,account_move m,account_tax_component c,account_tax_rate r WHERE m.id=l.move_id AND m.state='posted' AND m.date>=%s AND m.date<=%s AND c.id=l.tax_comp_id AND r.id=c.tax_rate_id AND m.company_id IN %s GROUP BY comp_id,comp_name,comp_rate,rate_name ORDER BY rate_name,comp_name",
                           date_from, date_to, tuple(company_ids))
            data["rate_taxes"] = []
            ## get tax base only if type = vat_exempt
            for r in res:
                if r.tax_comp_type == "vat_exempt":
                   r["base_total"] = r["base_total_exempt"]
                data["rate_taxes"].append(dict(r))

        items=data.get("rate_taxes") or []
        rate_taxes=self.group_items(items=items,group_field="comp_name",sum_field="base_total,tax_total", context={})

        items=data.get("comp_taxes") or []
        comp_taxes=self.group_items(items=items,group_field="comp_name",sum_field="base_total,tax_total", context={})

        data['options']={
            'rate_taxes': rate_taxes,
            'comp_taxes': comp_taxes,
        }
        return data

ReportTaxSum.register()
