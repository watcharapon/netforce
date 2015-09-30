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

import re
from datetime import *
from dateutil.relativedelta import *

from netforce.model import Model, fields, get_model
from netforce.utils import get_data_path, get_file_path
from netforce.access import get_active_company
from netforce.database import get_connection


class PaySlip(Model):
    _name = "hr.payslip"
    _string = "Pay Slip"
    _multi_company = True
    _name_field = "employee_id"

    _fields = {
        "run_id": fields.Many2One("hr.payrun", "Pay Run", search=True),
        "employee_id": fields.Many2One("hr.employee", "Employee", required=True, search=True),
        "date": fields.Date("Date", required=True, search=True),
        "due_date": fields.Date("Due Date"),
        "amount_wage": fields.Decimal("Wages", function="get_total", function_multi=True),
        "amount_allow": fields.Decimal("Allowances", function="get_total", function_multi=True),
        "amount_deduct": fields.Decimal("Deductions", function="get_total", function_multi=True),
        "amount_tax": fields.Decimal("Taxes", function="get_total", function_multi=True),
        "amount_post_allow": fields.Decimal("Non-taxable Allowances", function="get_total", function_multi=True),
        "amount_post_deduct": fields.Decimal("Post-tax Deductions", function="get_total", function_multi=True),
        "amount_net": fields.Decimal("Net Pay", function="get_total", function_multi=True),
        "amount_pay_other": fields.Decimal("Other Payments", function="get_total", function_multi=True),
        "amount_salary": fields.Decimal("Salary", function="get_total_details", function_multi=True),
        "amount_bonus": fields.Decimal("Bonus", function="get_total_details", function_multi=True),
        "amount_overtime": fields.Decimal("Overtime", function="get_total_details", function_multi=True),
        "amount_social": fields.Decimal("Soc. Fund", function="get_total_details", function_multi=True),
        "amount_provident": fields.Decimal("Prov. Fund", function="get_total_details", function_multi=True),
        "amount_other_expense": fields.Decimal("Other Expense", function="get_total_details", function_multi=True),
        "lines": fields.One2Many("hr.payslip.line", "slip_id", "Lines"),
        "comments": fields.One2Many("message", "related_id", "Comments"),
        "state": fields.Selection([["draft", "Draft"], ["approved", "Approved"], ['paid', 'Paid'], ['posted', 'Posted']], "Status", required=True),
        "company_id": fields.Many2One("company", "Company"),
        "move_id": fields.Many2One("account.move", "Journal Entry"),
    }

    _defaults = {
        "state": "draft",
        "date": lambda *a: date.today().strftime("%Y-%m-%d"),
        "due_date": lambda *a: (date.today() + relativedelta(day=31)).strftime("%Y-%m-%d"),
        "company_id": lambda *a: get_active_company(),
    }
    _order = "run_id.number,employee_id.first_name"

    def get_total(self, ids, context={}):
        all_vals = {}
        for obj in self.browse(ids):
            totals = {}
            total_pay_other = 0
            for line in obj.lines:
                item = line.payitem_id
                t = item.type
                if t not in totals:
                    totals[t] = 0
                totals[t] += line.amount
                if t in ("deduct", "post_deduct"):
                    total_pay_other += line.amount  # FIXME
            vals = {
                "amount_wage": totals.get("wage", 0),
                "amount_allow": totals.get("allow", 0),
                "amount_deduct": totals.get("deduct", 0),
                "amount_tax": totals.get("tax", 0),
                "amount_post_allow": totals.get("post_allow", 0),
                "amount_post_deduct": totals.get("post_deduct", 0),
                "amount_pay_other": total_pay_other,
            }
            vals["amount_net"] = vals["amount_wage"] + vals["amount_allow"] - vals["amount_deduct"] - \
                vals["amount_tax"] + vals["amount_post_allow"] - vals["amount_post_deduct"]
            all_vals[obj.id] = vals
        return all_vals

    def get_total_details(self, ids, context={}):
        all_vals = {}
        for obj in self.browse(ids):
            amt_salary = 0
            amt_bonus = 0
            amt_overtime = 0
            amt_other_expense = 0
            amt_social = 0
            amt_provident = 0
            for line in obj.lines:
                item = line.payitem_id
                if item.type == "wage":
                    if item.wage_type == "salary":
                        amt_salary += line.amount
                    elif item.wage_type == "overtime":
                        amt_overtime += line.amount
                    elif item.wage_type == "bonus":
                        amt_bonus += line.amount
                elif item.type == "deduct":
                    if item.deduct_type == "thai_social":
                        amt_social += line.amount
                    elif item.deduct_type == "provident":
                        amt_provident += line.amount
                elif item.type == "post_deduct":
                    amt_other_expense += line.amount  # XXX
            vals = {
                "amount_salary": amt_salary,
                "amount_bonus": amt_bonus,
                "amount_overtime": amt_overtime,
                "amount_other_expense": amt_other_expense,
                "amount_social": amt_social,
                "amount_provident": amt_provident,
            }
            all_vals[obj.id] = vals
        return all_vals

    def onchange_item(self, context={}):
        data = context["data"]
        emp_id = data.get("employee_id")
        if not emp_id:
            return
        date = data.get("date")
        emp = get_model("hr.employee").browse(emp_id)
        path = context["path"]
        line = get_data_path(data, path, parent=True)
        item_id = line["payitem_id"]
        if not item_id:
            return
        item = get_model("hr.payitem").browse(item_id)
        qty, rate = item.compute(context={"employee_id": emp_id, "date": date})
        line["qty"] = qty
        line["rate"] = rate
        line["amount"] = qty * rate
        self.update_amounts(context=context)
        return data

    def update_amounts(self, context={}):
        data = context["data"]
        lines = data['lines']
        totals = {}
        for line in lines:
            if not line:
                continue
            qty = line.get("qty", 0)
            rate = line.get("rate", 0)
            line["amount"] = qty * rate
            item_id = line.get("payitem_id")
            if not item_id:
                continue
            item = get_model("hr.payitem").browse(item_id)
            if item.type == 'tax':
                self.update_tax(context=context)
                line['amount'] = line['qty'] * line['rate']
            t = item.type
            if t not in totals:
                totals[t] = 0
            totals[t] += line["amount"]
        data["amount_wage"] = totals.get("wage", 0)
        data["amount_allow"] = totals.get("allow", 0)
        data["amount_deduct"] = totals.get("deduct", 0)
        data["amount_tax"] = totals.get("tax", 0)
        data["amount_post_allow"] = totals.get("post_allow", 0)
        data["amount_post_deduct"] = totals.get("post_deduct", 0)
        data["amount_net"] = data["amount_wage"] + data["amount_allow"] - data["amount_deduct"] - \
            data["amount_tax"] + data["amount_post_allow"] - data["amount_post_deduct"]
        return data

    def get_income(self, context):
        income = 0
        if context.get('end_period', 0):
            date_from = "2013-01-01"
            date_to = "2013-12-31"
            employee_id = context['data']['employee_id']
            for obj in self.search_browse([['date', '>=', date_from], ['date', '<=', date_to], ['employee_id', '=', employee_id], ['state', '=', 'approved']]):
                for line in obj.lines:
                    qty = line.qty or 0
                    rate = line.rate or 0
                    amt = qty * rate
                    item = line.payitem_id
                    if item.type in ("wage", "allow"):
                        income += amt
                    elif item.type == "deduct":
                        if item.deduct_type in ("thai_social", "provident"):
                            continue
                        income -= amt
        return income

    def update_tax(self, context={}):
        data = context["data"]
        employee_id = data["employee_id"]
        lines = data["lines"]
        date = data['date']
        month = int(date[5:7])
        ctx = context.copy()
        ctx.update({'end_period': 1})

        period = 12
        cr_year = datetime.now().year
        hire_date = get_model("hr.employee").browse(employee_id).hire_date
        start_month = 0
        if hire_date:
            year_hire = int(hire_date[0:4])
            month_hire = int(hire_date[5:7])
            start_month = month_hire
            if year_hire == cr_year:
                period = (period - month_hire) + 1

        income = 0
        salary = 0
        for line in lines:
            if not line:
                continue
            qty = line.get("qty", 0)
            rate = line.get("rate", 0)
            amt = qty * rate
            item_id = line.get("payitem_id")

            if not item_id:
                continue

            item = get_model("hr.payitem").browse(item_id)
            if item.type in ("wage", "allow"):
                if item.wage_type and item.wage_type in ("salary"):
                    salary = amt
                else:
                    income += amt
            elif item.type == "deduct":
                if item.deduct_type in ("thai_social", "provident"):
                    continue
                income -= amt

        for line in lines:
            if not line:
                continue
            item_id = line.get("payitem_id")
            if not item_id:
                continue
            item = get_model("hr.payitem").browse(item_id)
            if item.type == "tax":
                if item.tax_type == "thai":
                    # Compute normal rate
                    ctx = {
                        "employee_id": employee_id,
                        "year_income": salary * period,
                        "period": period,
                    }
                    qty, rate = item.compute(context=ctx)

                    if income < 1:
                        line["qty"] = qty
                        line["rate"] = rate
                        break

                    # Init salary for each month
                    number_month = 12
                    salary_line = [n >= start_month and salary or 0 for n in list(range(number_month + 1))]
                    irr_line = [0 for s in salary_line]
                    irr_line[month] = income

                    # Init tax_year for each month
                    tax_line = [0 for s in salary_line]
                    # Store regular tax
                    tax_line[0] = rate * period

                    # cr_year=datetime.now().year
                    start_date = str(cr_year) + '-01-01'
                    stop_date = str(cr_year) + '-12-31'

                    condition = [
                        ['date', '>=', start_date],
                        ['date', '<=', stop_date],
                        ['employee_id', '=', employee_id],
                    ]

                    # January
                    count = start_month or 1
                    for obj in self.search_browse(condition, order="date"):
                        if count > 12:
                            continue
                        obj_month = int(obj.date[5:7])
                        # compute only previous month
                        if obj_month >= month:
                            print('skip %s' % (month))
                            break
                        for obj_line in obj.lines:
                            obj_item = obj_line.payitem_id
                            amt = obj_line.qty * obj_line.rate
                            if obj_item.type in ('wage', 'allowance'):
                                wage_type = obj_item.wage_type or ""
                                if wage_type and wage_type in ('salary'):
                                    salary_line[count] = amt
                                else:
                                    irr_line[count] += amt
                            elif obj_item.type in ('deduct'):
                                if obj_item.deduct_type in ("thai_social", "provident"):
                                    continue
                                irr_line[count] -= amt
                        count += 1

                    def get_salary_year(line):
                        period = len(line)
                        for i in range(period):
                            # jan-dec
                            if i > 0:
                                bf = sum(line[1:i])
                                it = line[i] * (period - i)
                                yield bf + it

                    salary_line = [0] + list(get_salary_year(salary_line))
                    # Total of income & irr income for each month
                    income_line = list(map(lambda x: sum(x), list(zip(salary_line, irr_line))))
                    count = 0
                    irr_amt = 0
                    ctx['period'] = period
                    for income in income_line:
                        if count > 0:
                            irr_amt += irr_line[count - 1]
                            ctx["year_income"] = income and income + irr_amt or -1  # FIXME get_yearly_income
                            qty, rate = item.compute(context=ctx)
                            tax_line[count] = (rate * period)
                        count += 1

                    regular_tax = tax_line[0] / period
                    rate = tax_line[month] - tax_line[month - 1] + regular_tax

                    line["qty"] = 1
                    line["rate"] = rate
        return data

    def onchange_employee(self, context={}):
        data = context["data"]
        emp_id = data.get("employee_id")
        if not emp_id:
            return
        date = data.get("date")
        if not date:
            return
        lines = []
        for item in get_model("hr.payitem").search_browse([]):
            ctx = {
                "employee_id": emp_id,
                "date": date,
            }
            qty, rate = item.compute(context=ctx)
            if not item.show_default:
                continue
            line = {
                "payitem_id": item.id,
                "qty": qty,
                "rate": rate,
            }
            lines.append(line)
        emp = get_model('hr.employee').browse(emp_id)
        if emp.profile_id:
            lines = []
            for item in emp.profile_id.pay_items:
                ctx = {
                    "employee_id": emp_id,
                    "date": date,
                }
                qty, rate = item.compute(context=ctx)
                line = {
                    "payitem_id": item.id,
                    "qty": qty,
                    "rate": rate,
                }
                lines.append(line)
        data["lines"] = lines
        self.update_amounts(context=context)
        return data

    def approve(self, ids, context={}):
        for obj in self.browse(ids):
            obj.write({"state": "approved"})
        flash = 'Payslip has been approved'
        if len(ids) > 1:
            flash = 'payslips has been approved'
        return {
            "action": {
                "name": "payslip"
            },
            "flash": flash,
        }

    def merge_lines(self, lines=[]):
        account = {}
        for line in lines:
            desc = line['description']
            acc_id = line['account_id']
            debit = line['debit'] or 0
            credit = line['credit'] or 0
            if acc_id not in account.keys():
                account[acc_id] = {
                    'account_id': acc_id,
                    'description': desc,
                    'debit': debit,
                    'credit': credit,
                }
                continue
            account[acc_id]['debit'] += debit
            account[acc_id]['credit'] += credit
        nlines = []
        for acc_id, vals in account.items():
            nlines.append(vals)
        return nlines

    def get_move_lines(self, ids, context={}):
        # step
        # 1. set debit/credit amount
        # 2. group account code
        # 3. order by debit, credit
        lines = []
        for obj in self.browse(ids):
            total_credit = 0
            total_debit = 0
            for line in obj.lines:
                item = line.payitem_id
                account = item.account_id
                amount = line.amount or 0
                if account and amount:
                    vals = {
                        'description': item.name or "",
                        'account_id': account.id,
                        'debit': 0,
                        'credit': 0,
                    }
                    start_code = int(account.code[0])
                    if start_code in (1, 5):
                        vals['debit'] = amount
                        total_debit += amount
                    elif start_code in (2, 6):
                        vals['credit'] = amount
                        total_credit += amount
                    lines.append(vals)
            pst = get_model("hr.payroll.settings").browse(1)
            bank_account_id = pst.bank_account_id
            if bank_account_id:
                if total_debit > total_credit:
                    vals = {
                        'description': bank_account_id.name or "",
                        'account_id': bank_account_id.id,
                        'debit': 0,
                        'credit': total_debit - total_credit,
                    }
                    lines.append(vals)
                elif total_credit > total_debit:
                    vals = {
                        'description': bank_account_id.name or "",
                        'account_id': bank_account_id.id,
                        'debit': total_credit - total_debit,
                        'credit': 0,
                    }
                    lines.append(vals)
        return sorted(self.merge_lines(lines), key=lambda x: x['credit'])

    def pay(self, ids, context={}):
        # payrun_id=context.get('payrun_id')
        for obj in self.browse(ids):
            obj.write({
                "state": "paid",
            })
            flash = "Payslip has been paid"
            if len(ids) > 1:
                flash = "Payslips has been paid"
        return {
            "action": {
                "name": "payslip"
            },
            "flash": flash,
        }

    def get_pit(self, context={}):
        if not context.get('refer_id'):
            return {}
        payslip_id = int(context['refer_id'])
        payslip = self.browse(payslip_id)
        employee = payslip.employee_id
        # get personal income tax from database
        taxes = get_model('hr.payslip.tax').search([['payslip_id', '=', payslip_id]])
        if taxes and payslip.state in ('approved'):
            no = 1
            lines = []
            for tax in get_model('hr.payslip.tax').search_browse([['payslip_id', '=', payslip_id]]):
                lines.append({
                    'no': "%s." % (no),
                    'code': tax.code or '',
                    'item': tax.name or '',
                    'amount': tax.amount or 0.0,
                })
                no += 1
            return {
                'employee': ' '.join(s for s in [(employee.title and employee.title + '.' or ''), (employee.first_name or ''), (employee.last_name or '')]),
                'number': payslip.run_id.number,
                'date': payslip.date,
                'lines': lines,
            }

        income = 0
        # FIXME for December, need sum(income from jan-dec)
        date = payslip.date
        month = int(date[5:7])
        december = 1 if month == 12 else 0
        if december:
            ctx = {
                'end_period': 1,
                'data': {
                    'employee_id': payslip.employee_id.id,
                }
            }
            income = self.get_income(ctx)

        for line in payslip.lines:
            if not line:
                continue
            qty = line.qty or 0
            rate = line.rate or 0
            amt = qty * rate
            item = line.payitem_id
            if not item:
                continue
            if item.type in ("wage", "allow"):
                if item.wage_type and item.wage_type in ("salary"):
                    income += amt * 12 if not december else amt
                else:
                    income += amt
            elif item.type == "deduct":
                if item.deduct_type in ("thai_social", "provident"):
                    continue
                income -= amt

        context['employee_id'] = employee.id
        context['year_income'] = income
        line = get_model("hr.payitem").compute_thai_tax(context=context)
        del line['tax_month']

        vals = {}
        vals["B1"] = "not defined"
        vals["B2"] = 'Contribution to government pension fund'
        vals["B3"] = 'Contribution to private school teacher fund'
        vals["B4"] = 'Taxpaper age over 65 years of age with 190,000 baht income exemption'
        vals["B4a"] = ""
        vals["B4b"] = ""
        vals["B5"] = 'Spouse age over 65 years of age with 190,000 baht income exemption'
        vals[
            "B6"] = 'Serverance pay received under the Labor Law(In case taxpayer chooses to include in tax computation)'
        vals["B7"] = 'Total (1. to 6.) to be filled in A2'
        vals["C1"] = 'Taxpayer'
        vals[
            "C2"] = "Spouse (30,000 Baht for spouse with income that is combined with taxpayer's income in tax computation or spouse with no income)"
        vals["C3a"] = "Child : 15,000 Baht per child"
        vals["C3b"] = "Child : 17,000 Baht per child"
        vals["C4a"] = "Father of taxpayer"
        vals["C4b"] = "Mother of taxpayer"
        vals[
            "C4c"] = "Father of Spouse with income that is combined with taxpayer's income in computation or of Spouse with no income"
        vals[
            "C4d"] = "Mother of Spouse with income that is combined with taxpayer's income in computation or of Spouse with no income"
        vals["C5"] = "Disabled care expense allowance"
        vals["C6"] = "Health Insurance Premium for Taxpayer's and Spouse's Parent"
        vals["C7"] = "Life Insurance Premium"
        vals["C7a"] = ""
        vals["C7b"] = ""
        vals["C8"] = "Contribution to Provident Fund (The part that dose not exceed 10,000 baht)"
        vals["C9"] = "Payment for purchase of shares retirement mutual fund"
        vals["C10"] = "Payment for purchase of long-term equity fund"
        vals["C11"] = "Interest paid on loans for purchase, hire purchase, or construction of residence building"
        vals["C12"] = "Building Purchase cost"
        vals["C13"] = "Contribution to social security fund"
        vals["C14"] = "Total (1. to 13.) to be filled in A6"
        vals["A1"] = "Salary, wage,pension etc. (Plus exempted income from B6)"
        vals["A2"] = "Less exempted income (from B7)"
        vals["A3"] = "Income after deduction of exempted income (1. - 2.)"
        vals["A4"] = "Less expense(40% of 3. but not exceeding legal limit)"
        vals["A5"] = "Income affter deduction of expense (3. - 4.)"
        vals["A6"] = "Less allowances (from C14.)"
        vals["A7"] = "Income after deduction of allowances (5. - 6.)"
        vals["A8"] = "Less contribution to education (2 times of the contribution paid but not exceeding 10% of 7.)"
        vals["A9"] = "Income after deduction of contribution to education (7. - 8.)"
        vals["A10"] = "Less donation (not exceed 10% of 9.)"
        vals["A11"] = "Net Income (9. - 10.)"
        vals["A12"] = "Tax computed from Net Income in 11."
        vals["A13"] = "Less Withholding Income Tax"
        vals["A14"] = "(Total attached documents for 8. ,10. and 13. .......page(s))"
        vals["A15"] = "Plus additional tax payment (from C 6. of continued page (s)(if any))"
        vals["A16"] = "Less excess tax payment (from C 7. of continued page (s) (if any))"
        vals["A17"] = "Less tax payment from P.N.D.91 (In the case of additional filing)"
        vals["A18"] = "Tax additional Payment or Excess Payment"
        vals["A19"] = "Plus surcharge (if any)"
        vals["A20"] = ""
        vals["A21"] = ""
        vals["A22"] = ""

        # reorder code
        def key(item):
            key_pat = re.compile(r"(\D+)(\d+)")
            m = key_pat.match(item[0])
            if m:
                return m.group(1), int(m.group(2))
            else:
                return ('', 0)
        no = 1
        lines = []
        for k, v in sorted(line.items(), key=key):
            lines.append({
                'no': "%s." % (no),
                'code': k,
                'item': vals.get(k, ''),
                'amount': v,
            })
            no += 1
        data = {
            'employee': ' '.join(s for s in [(employee.title and employee.title + '.' or ''), (employee.first_name or ''), (employee.last_name or '')]),
            'number': payslip.run_id.number,
            'date': payslip.date,
            'lines': lines,
        }
        return data

    def onchange_payrun(self, context={}):
        # copy date from/to from payrun to payslip
        data = context["data"]
        payrun_id = int(data.get('run_id'))
        date_from = get_model('hr.payrun').browse(payrun_id).date_from
        date_to = get_model('hr.payrun').browse(payrun_id).date_to
        data['date'] = date_from
        data['due_date'] = date_to
        return data

    def to_draft(self, ids, context):
        if not any(ids):
            return
        for obj in self.browse(ids):
            obj.write({
                "state": "draft",
            })
            if obj.move_id:
                obj.move_id.to_draft()
        flash = "Payslip has been set to draft"
        if len(ids) > 1:
            flash = "All Payslips has been set to draft"
        return {
            "action": {
                "name": "payslip",
                "mode": "form",
                "active_id": obj.id,
            },
            "flash": flash,
        }

    def copy(self, ids, context):
        obj = self.browse(ids)[0]
        vals = {
            "run_id": obj.run_id.id,
            "employee_id": obj.employee_id.id,
            "date": obj.date,
            "due_date": obj.due_date,
            "state": 'draft',
            "lines": [],
        }
        for line in obj.lines:
            line_vals = {
                "slip_id": line.slip_id.id,
                "sequence": line.sequence,
                "payitem_id": line.payitem_id.id,
                "qty": line.qty,
                "rate": line.rate,
                "amount": line.amount,
            }
            vals["lines"].append(("create", line_vals))
        new_id = self.create(vals)
        # new_obj=self.browse(new_id)
        return {
            "next": {
                "name": "payslip",
                "mode": "form",
                "active_id": new_id,
            },
            "flash": "Payslip is copied",
        }

    def post_journal(self, ids, context={}):
        settings = get_model("hr.payroll.settings").browse(1)
        if not settings.intg_acc:
            return
        journal_id = settings.journal_id
        bank_account_id = settings.bank_account_id
        sso_account_id = settings.sso_account_id
        sso_comp_support = settings.sso_comp_support or False
        if not journal_id:
            raise Exception("Not found journal (Setting-> Payroll Settings-> Tab Accounting")
        if not bank_account_id:
            raise Exception("Not found Bank Account (Setting-> Payroll Settings-> Tab Accounting")
        if not sso_account_id:
            raise Exception("Not found SSO Account (Setting-> Payroll Settings-> Tab Accounting")
        company_id = get_active_company()
        company = get_model("company").browse(company_id)
        for obj in self.browse(ids):
            total_debit = 0.0
            total_credit = 0.0
            employee_id = obj.employee_id
            emp_name = '%s %s' % (employee_id.first_name, employee_id.last_name)
            move_vals = {
                "journal_id": journal_id.id,
                "number": obj.number,
                "date": obj.date,
                "narration": '%s - %s' % (obj.run_id.number, emp_name),
                "related_id": "account.payment,%s" % obj.id,
                "company_id": obj.company_id.id,
            }
            move = obj.move_id
            move_id = move.id
            if move:
                for line in move.lines:
                    line.delete()
            else:
                move_id = get_model('account.move').create(move_vals)
            obj.write({
                'move_id': move_id,
            })
            lines = []
            for line in obj.lines:
                item = line.payitem_id
                amt = line.amount
                debit = 0.0
                credit = 0.0
                desc = '%s - %s %s' % (item.name, employee_id.first_name, employee_id.last_name)
                if item.type in ("wage"):
                    if item.wage_type == 'salary':
                        pass
                    debit = amt
                elif item.type in ("deduct"):
                    if item.deduct_type == 'thai_social':
                        credit = amt
                        if sso_comp_support:
                            lines.append({
                                'move_id': move_id,
                                'description': '%s - %s' % (item.name, company.name or ""),
                                'account_id': sso_account_id.id,
                                'debit': debit,
                                'credit': credit * 2,
                            })
                            total_credit += credit * 2
                        debit = credit
                        credit = 0
                    elif item.deduct_type == 'provident':
                        credit = amt
                elif item.type in ("tax"):
                    if item.tax_type == 'thai':
                        pass
                    credit = amt
                elif item.type in ('allow'):
                    debit = amt
                else:
                    print(item.name, " type ", item.type, " ", amt)
                line = {
                    'move_id': move_id,
                    'description': desc,
                    'account_id': item.account_id.id,
                    'debit': debit,
                    'credit': credit,
                }
                if amt:
                    lines.append(line)
                    total_credit += credit
                    total_debit += debit

            credit, debit = 0, 0
            if total_credit > total_debit:
                debit = total_credit - total_debit
            else:
                credit = total_debit - total_credit
            line = {
                'move_id': move_id,
                'description': '%s - %s' % (bank_account_id.name, company.name or ""),
                'account_id': bank_account_id.id,
                'debit': debit,
                'credit': credit,
            }
            lines.append(line)
            move = get_model('account.move').browse(move_id)
            # order by debit, credit
            move.write({
                'lines': [('create', line) for line in sorted(lines, key=lambda x: x['debit'], reverse=True)],
            })

    def get_net_fund(self, ids, context={}):
        amt_fund = 0
        for obj in self.browse(ids):
            for line in obj.lines:
                item = line.payitem_id
                if item.type in ["contrib", "deduct"]:
                    amt_fund += line.amount
        return amt_fund

    def delete(self, ids, context={}):
        if not ids:
            return
        db = get_connection()
        ids = [x['id']
               for x in db.query("select id from hr_payslip where id in (%s)" % ','.join([str(id) for id in ids]))]
        for obj in self.browse(ids):
            if obj.state != 'draft':
                emp_name = '%s %s' % (obj.employee_id.first_name, obj.employee_id.last_name)
                raise Exception("Payslip's %s has been %s." % (emp_name, obj.state))
            if obj.move_id:
                obj.move_id.to_draft()
                obj.move_id.delete()
        super().delete(ids)

    def view_journal(self, ids, context={}):
        obj = self.browse(ids)[0]
        move = obj.move_id
        if not move:
            raise Exception("#TODO Journal Entry not create yet.")
        return {
            'next': {
                'name': 'journal_entry',
                'mode': 'form',
                'active_id': move.id,
            },

        }

    def compute(self, ids, context={}):
        pass

    def get_payslip(self, context={}):
        if not context.get('refer_id'):
            return {}
        payslip_id = int(context['refer_id'])
        payslip = self.browse(payslip_id)
        employee = payslip.employee_id
        title = employee.title or ""
        employee_name = "%s. %s %s" % (title.title(), employee.first_name or '', employee.last_name or '')
        employee_address = get_model('hr.employee').get_address([employee.id])
        lines = []
        income = []
        deduct = []
        for line in payslip.lines:
            type = line.payitem_id.type
            if type in ('wage', 'allow'):
                income.append({
                    'income': 1,
                    'item': line.payitem_id.name,
                    'amount': line.amount,
                })
            else:
                deduct.append({
                    'income': 0,
                    'item': line.payitem_id.name,
                    'amount': line.amount,
                })

        range_amt = len(income) if len(income) > len(deduct) else len(deduct)
        total_deduct = 0.0
        total_income = 0.0
        for i in range(range_amt):
            line = {}
            if i < len(income):
                item = income[i]
                total_income += item['amount']
                line.update({
                    'income_description': item['item'],
                    'income_amt': item['amount'],
                    'income_no': i + 1,
                })
            if i < len(deduct):
                item = deduct[i]
                total_deduct += item['amount']
                line.update({
                    'deduct_description': item['item'],
                    'deduct_amt': item['amount'],
                    'deduct_no': i + 1,
                })
            lines.append(line)
        data = {
            'ref': payslip.run_id.number,
            'date': payslip.date,
            'employee_name': employee_name,
            'employee_address': employee_address or "Empty Address",
            'amount_net': payslip.amount_net,
            'total_deduct': total_deduct,
            'total_income': total_income,
            'lines': lines
        }
        comp = get_model('settings').browse(1)
        if comp.logo:
            data['logo'] = get_file_path(comp.logo)
        return data

    def get_data(self, ids, context={}):
        settings = get_model("settings").browse(1)
        pages = []
        for obj in self.browse(ids):
            context['refer_id'] = obj.id
            data = self.get_payslip(context=context)
            pages.append(data)
        if pages:
            pages[-1]["is_last_page"] = True
        return {
            "pages": pages,
            "logo": get_file_path(settings.logo),
        }

PaySlip.register()
