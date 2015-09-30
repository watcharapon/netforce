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
from calendar import monthrange

from netforce.access import get_active_company
from netforce.utils import get_file_path

MONTHS = [
    ['1', 'January'],
    ['2', 'February'],
    ['3', 'March'],
    ['4', 'April'],
    ['5', 'May'],
    ['6', 'June'],
    ['7', 'July'],
    ['8', 'August'],
    ['9', 'September'],
    ['10', 'October'],
    ['11', 'November'],
    ['12', 'December'],
]


class PayRun(Model):
    _name = "hr.payrun"
    _string = "Pay Run"
    _name_field = "number"
    _multi_company = True

    _fields = {
        "number": fields.Char("Number", required=True, search=True),
        "date_from": fields.Date("From Date", required=True),
        "date_to": fields.Date("To Date", required=True),
        "date_pay": fields.Date("Pay Date", search=True),
        'month': fields.Selection(MONTHS, "Month"),
        "num_employees": fields.Integer("Employees", function="get_total", function_multi=True),
        "amount_employee": fields.Decimal("Employee Payments", function="get_total", function_multi=True),
        "amount_other": fields.Decimal("Other Payments", function="get_total", function_multi=True),
        "amount_total": fields.Decimal("Total", function="get_total", function_multi=True),
        "payslips": fields.One2Many("hr.payslip", "run_id", "Payslips"),
        "comments": fields.One2Many("message", "related_id", "Comments"),
        "company_id": fields.Many2One("company", "Company"),
        "move_id": fields.Many2One("account.move", "Journal Entry"),
        "state": fields.Selection([["draft", "Draft"], ["approved", "Approved"], ['paid', 'Paid'], ['posted', 'Posted']], "Status", required=True),
    }

    def _get_number(self, context={}):
        count = 0
        while 1:
            num = get_model("sequence").get_number("payrun")
            if not num:
                return None
            res = self.search([["number", "=", num]])
            if not res:
                return num
            get_model("sequence").increment("payrun")
            count += 1
            if count > 10:
                return "/"

    _defaults = {
        "number": _get_number,
        "date": lambda *a: date.today().strftime("%Y-%m-01"),
        "date_from": lambda *a: date.today().strftime("%Y-%m-01"),
        "date_to": lambda *a: (date.today() + relativedelta(day=31)).strftime("%Y-%m-%d"),
        "date_pay": lambda *a: (date.today() + relativedelta(day=31)).strftime("%Y-%m-%d"),
        "company_id": lambda *a: get_active_company(),
        'state': 'draft',
    }

    _sql_constraints = ("hr_payrun_key_uniq", "unique(number,company_id)", "number should be unique"),

    def get_total(self, ids, context={}):
        vals = {}
        for obj in self.browse(ids):
            num_emp = 0
            amt_emp = 0
            amt_other = 0
            for slip in obj.payslips:
                num_emp += 1
                amt_emp += slip.amount_net
                amt_other += slip.amount_pay_other
            vals[obj.id] = {
                "num_employees": num_emp,
                "amount_employee": amt_emp,
                "amount_other": amt_other,
                "amount_total": amt_emp + amt_other,
            }
        return vals

    def gen_payslips(self, ids, context={}):
        print("gen_payslips", ids)
        obj = self.browse(ids)[0]
        date = obj.date_from
        emp_ids = get_model("hr.employee").search([["work_status", "=", "working"]])
        for emp in get_model("hr.employee").browse(emp_ids):
            period = 12
            res = get_model("hr.payslip").search([["run_id", "=", obj.id], ["employee_id", "=", emp.id]])
            # TODO: check if payslip exists already
            if res:
                continue
            vals = {
                "employee_id": emp.id,
                "date": date,
                "run_id": obj.id,
                'company_id': get_active_company(),
            }
            lines = []
            ctx = {
                "employee_id": emp.id,
                "date": date,
                "date_from": obj.date_from,
                "date_to": obj.date_to,
            }
            for item in get_model("hr.payitem").search_browse([]):  # XXX
                if item.tax_type == "thai":
                    ctx["year_income"] = (emp.salary or 0.0) * period

                qty, rate = item.compute(context=ctx)

                if not item.show_default:
                    continue

                line_vals = {
                    "payitem_id": item.id,
                    "qty": qty,
                    "rate": rate,
                }
                lines.append(line_vals)

            if emp.profile_id:
                lines = []
                for item in emp.profile_id.pay_items:
                    if item.tax_type == "thai":
                        ctx["year_income"] = (emp.salary or 0.0) * period
                    qty, rate = item.compute(context=ctx)
                    line_vals = {
                        "payitem_id": item.id,
                        "qty": qty,
                        "rate": rate,
                    }
                    lines.append(line_vals)

            vals["lines"] = [("create", line_vals) for line_vals in lines]
            get_model("hr.payslip").create(vals)

    def copy(self, ids, context):
        obj = self.browse(ids)[0]
        vals = {
            "number": obj.number + "(Copy)",
            "date_from": obj.date_from,
            "month": obj.month,
            "date_to": obj.date_to,
            "date_pay": obj.date_pay,
            "payslips": [],
        }
        for payslip in obj.payslips:
            payslip_vals = {
                "run_id": payslip.run_id.id,
                "employee_id": payslip.employee_id.id,
                "date": payslip.date,
                "due_date": payslip.due_date,
                "state": 'draft',
                "lines": [],
            }
            for line in payslip.lines:
                line_vals = {
                    "slip_id": line.slip_id.id,
                    "sequence": line.sequence,
                    "payitem_id": line.payitem_id.id,
                    "qty": line.qty,
                    "rate": line.rate,
                    "amount": line.amount,
                }
                payslip_vals["lines"].append(("create", line_vals))

            vals["payslips"].append(("create", payslip_vals))
        new_id = self.create(vals)
        new_obj = self.browse(new_id)
        return {
            "next": {
                "name": "payrun",
                "mode": "form",
                "active_id": new_id,
            },
            "flash": "PayRun %s copied to %s" % (obj.number, new_obj.number),
        }

    def get_bank_data(self, context={}):
        ref_id = int(context.get("refer_id", "0"))
        lines = []
        obj = self.browse(ref_id)
        settings = get_model("settings").browse(1)
        symbol = settings.currency_id.code or ""
        for payslip in obj.payslips:
            vals = {
                'bank_account': payslip.employee_id.bank_account,
                'paid_amount': payslip.amount_net or 0,
            }
            lines.append(vals)
        data = {
            'lines': lines,
            'symbol': symbol
        }
        return data

    def pay(self, ids, context={}):
        for obj in self.browse(ids):
            context['payrun_id'] = obj.id
            for payslip in obj.payslips:
                payslip.pay(context=context)
        obj.write({"state": "paid"})

    def approve(self, ids, context={}):
        for obj in self.browse(ids):
            for payslip in obj.payslips:
                payslip.write({
                    'state': 'approved',
                })
            obj.write({
                'state': 'approved',
            })

    def delete(self, ids, context={}):
        for obj in self.browse(ids):
            if obj.state != 'draft':
                raise Exception("%s has been %s." % (obj.number, obj.state))
            slip_ids = [slip.id for slip in obj.payslips]
            get_model("hr.payslip").delete(slip_ids)
            if obj.move_id:
                obj.move_id.to_draft()
                for line in obj.move_id.lines:
                    line.delete()
                obj.move_id.delete()
        super().delete(ids)
        return {
            'next': {
                'name': 'payrun',
                'mode': 'form',
                'active_id': obj.id,
            },
            'flash': 'Delete succesfully'
        }

    def view_journal(self, ids, context={}):
        obj = self.browse(ids)[0]
        move_id = obj.move_id
        if not move_id:
            raise Exception("#TODO Journal Entry not create yet.")
        return {
            'next': {
                'name': 'journal_entry',
                'mode': 'form',
                'active_id': move_id.id,
            },

        }

    def to_draft(self, ids, context={}):
        for obj in self.browse(ids):
            for payslip in obj.payslips:
                payslip.to_draft(context=context)
            move = obj.move_id
            if move:
                move.to_draft()
                for line in move.lines:
                    line.delete()
            obj.write({
                'state': 'draft',
            })

    def get_data(self, ids, context={}):
        settings = get_model("settings").browse(1)
        pages = []
        for obj in self.browse(ids):
            for payslip in obj.payslips:
                context['refer_id'] = payslip.id
                data = get_model('hr.payslip').get_payslip(context=context)
                pages.append(data)
        if pages:
            pages[-1]["is_last_page"] = True
        return {
            "pages": pages,
            "logo": get_file_path(settings.logo),
        }

    def onchange_month(self, context={}):
        data = context['data']
        month = int(data['month'])
        year = int(date.today().strftime("%Y"))
        weekday, total_day = monthrange(int(year), int(month))
        data['number'] = '%s/%s' % (year, (data['month'] or "").zfill(2))
        data['date_from'] = "%s-%s-01" % (year, month)
        data['date_to'] = "%s-%s-%s" % (year, month, total_day)
        data['date_pay'] = "%s-%s-%s" % (year, month, total_day)
        return data

PayRun.register()
