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

from operator import itemgetter

from netforce.model import Model, fields, get_model
from datetime import *
from dateutil.relativedelta import *
from netforce.access import get_active_company
from decimal import Decimal

balance_sheet = ["cash","cheque","bank","receivable","cur_asset","fixed_asset","noncur_asset",
                 "payable","cust_deposit","cur_liability","noncur_liability",
                 "equity"]
class ReportGLDetails(Model):
    _name = "report.gl.details"
    _transient = True
    _fields = {
        "date_from": fields.Date("From"),
        "date_to": fields.Date("To"),
        "select_type": fields.Selection([["all", "All"], ["range", "Account Range"], ["list", "Account List"]], "Select Accounts"),
        "account_from_id": fields.Many2One("account.account", "From Account", condition=[['type','!=','view']]),
        "account_to_id": fields.Many2One("account.account", "To Account", condition=[['type','!=','view']]),
        "accounts": fields.Text("Account List"),
        "contact_id": fields.Many2One("contact", "Contact"),
        "track_id": fields.Many2One("account.track.categ", "Tracking-1", condition=[["type", "=", "1"]]),
        "track2_id": fields.Many2One("account.track.categ", "Tracking-2", condition=[["type", "=", "2"]]),
        "hide_zero": fields.Boolean("Hide zero lines"),
        "show_amount_cur": fields.Boolean("Show Currency Amount"),
    }

    _defaults = {
        "date_from": lambda *a: date.today().strftime("%Y-%m-01"),
        "date_to": lambda *a: (date.today() + relativedelta(day=31)).strftime("%Y-%m-%d"),
        "select_type": "all",
    }

    def get_report_data(self, ids, context={}):
        company_id = get_active_company()
        comp = get_model("company").browse(company_id)
        if ids:
            params = self.read(ids, load_m2o=False)[0]
        else:
            params = self.default_get(load_m2o=False, context=context)
        settings = get_model("settings").browse(1)
        date_from = params.get('date_from')
        date_to = params.get('date_to')
        contact_id = params.get("contact_id") or None
        if contact_id:
            contact_id = int(contact_id)
        track_id = params.get("track_id") or None
        track = None
        if track_id:
            track_id = int(track_id)
            track = get_model('account.track.categ').browse(track_id)
        track2_id = params.get("track2_id") or None
        track2 = None
        if track2_id:
            track2_id = int(track2_id)
            track2 = get_model('account.track.categ').browse(track2_id)
        hide_zero = params.get("hide_zero")
        select_type = params.get("select_type")
        condition = [["type", "!=", "view"]]
        if select_type == "range":
            account_from_id = params.get("account_from_id")
            if account_from_id:
                account_from_id = int(account_from_id)
                account_from = get_model("account.account").browse(account_from_id)
                condition.append(["code", ">=", account_from.code])
            account_to_id = params.get("account_to_id")
            if account_to_id:
                account_to_id = int(account_to_id)
                account_to = get_model("account.account").browse(account_to_id)
                condition.append(["code", "<=", account_to.code])
        elif select_type == "list":
            codes = params.get("accounts") or ""
            acc_ids = []
            for code in codes.split(","):
                code = code.strip()
                if not code:
                    continue
                res = get_model("account.account").search([["code", "=", code]])
                if not res:
                    raise Exception("Account code not found: %s" % code)
                acc_id = res[0]
                acc_ids.append(acc_id)
            if acc_ids:
                condition.append(["id", "in", acc_ids])

        data = {
            "company_name": comp.name,
            "date_from": date_from,
            "date_to": date_to,
            "accounts": [],
            "track_name": track.name if track else None,
            "track_code": track.code if track else None,
            "track2_name": track2.name if track2 else None,
            "track2_code": track2.code if track2 else None,
            "show_amount_cur": params.get("show_amount_cur"),
        }

        ctx = {
            "date_to": datetime.strptime(date_from, '%Y-%m-%d').strftime('%Y-%m-%d'),
            "excl_date_to": True,
            "contact_id": contact_id,
            "track_id": track_id,
            "track2_id": track2_id,
        }
        accs = get_model("account.account").search_browse(condition, context=ctx)
        for acc in accs:
            debit_total = Decimal("0.00")
            credit_total = Decimal("0.00")
            bg_bal = Decimal(acc.balance) or Decimal("0")
            acc_vals = {
                "code_name": (acc.code or '') + ' ' + (acc.name or ''),
                "code": acc.code,
                "name": acc.name,
                "bg_bal": acc.balance or 0.00,
                "lines": [],
                "debit_total": 0.00,
                "credit_total": 0.00,
            }
            cond = [["account_id", "=", acc.id], ["move_id.date", ">=", date_from],
                   ["move_id.date", "<=", date_to], ["move_id.state", "=", "posted"]]
            if contact_id:
                cond.append(["contact_id", "=", contact_id])
            if track_id:
                cond.append(["track_id", "=", track_id])
            if track2_id:
                cond.append(["track2_id", "=", track2_id])
            lines = get_model("account.move.line").search_browse(cond, order="move_date, move_number")
            for line in lines:
                if hide_zero and not line.debit and not line.credit:
                    continue
                bg_bal += (line.debit - line.credit)
                line_vals = {
                    "id": line.id,
                    "date": line.move_date,
                    "number": line.move_number,
                    "description": line.description,
                    "debit": line.debit,
                    "credit": line.credit,
                    "amount_cur": line.amount_cur,
                    "balance": bg_bal,
                    "contact_name": line.contact_id.name,
                    "track_code": line.track_id.code,
                    "track2_code": line.track2_id.code,
                    "tax_no": line.tax_no,
                }
                if not line_vals['contact_name'] and line.move_id.related_id:
                    # FIXME USE TRY EXPRESSION TO CHECK if RELATED FIELD  EXISTED (TEMPORALY)
                    try:
                        contact=line.move_id.related_id.contact_id
                    except Exception as e:
                        print("ERROR ", e)
                        continue
                    if contact:
                        line_vals['contact_name']=contact.name
                debit_total += line.debit or Decimal("0")
                credit_total += line.credit or Decimal("0")
                acc_vals["lines"].append(line_vals)
            acc_vals['lines'].sort(key = itemgetter("date","number"))
            acc_vals["debit_total"] = debit_total
            acc_vals["credit_total"] = credit_total
            if acc.type in balance_sheet:
                data["accounts"].append(acc_vals)
            elif acc_vals["lines"]:
                data["accounts"].append(acc_vals)
        return data

ReportGLDetails.register()
