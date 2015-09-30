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


class PayItem(Model):
    _name = "hr.payitem"
    _string = "Pay Item"
    _fields = {
        "name": fields.Char("Name", required=True, search=True),
        "description": fields.Text("Description"),
        "type": fields.Selection([["wage", "Wages"], ["allow", "Allowances"], ["deduct", "Deductions"], ["tax", "Tax"], ["post_allow", "Non-taxable Allowances"], ["post_deduct", "Post-tax Deductions"], ["contrib", "Employer Contributions"]], "Pay Item Type", required=True, search=True),
        "account_id": fields.Many2One("account.account", "Account"),
        "show_default": fields.Boolean("Show as default for all employees"),
        "comments": fields.One2Many("message", "related_id", "Comments"),
        "active": fields.Boolean("Active"),
        "tax_type": fields.Selection([["thai", "Thai Personal Income Tax"]], "Tax Type"),
        "deduct_type": fields.Selection([["thai_social", "Thai Social Security Fund"], ["provident", "Provident Fund"]], "Deduction Type"),
        "wage_type": fields.Selection([["salary", "Salary"], ["overtime", "Overtime"], ["bonus", "Bonus"], ["commission", "Commission"], ['position', "Position Allowance"]], "Wage Type"),
        "times": fields.Decimal("Times"),
        "months": fields.Integer("Number of Month"),
    }
    _defaults = {
        "active": True,
    }
    _order = "name"

    def compute(self, ids, context={}):
        obj = self.browse(ids)[0]
        emp_id = context.get("employee_id")
        emp = get_model("hr.employee").browse(emp_id)
        # date=context.get("date")
        qty = 0
        rate = 0
        if obj.type == "wage":
            if obj.wage_type == "salary" and emp.salary:
                qty = 1
                salary = emp.salary or 0.0
                # XXX get total day woking for each month
                if emp.work_type == 'daily':
                    date_from = context.get("date_from")
                    date_to = context.get("date_to")
                    if date_from and date_to:
                        res = '%s-%s' % (int(date_to[8:10]), int(date_from[8:10]))
                        total_day = eval(res)
                        # cond=[['time','>=',date_from],['time','<=',date_to],['employee_id','=',emp.id]]
                        # att=get_model("hr.attendance").search_read(cond)
                        #if att: print(att)
                        print('total_day ', total_day)
                        qty = 30  # XXX
                rate = salary
            elif obj.wage_type == 'overtime' and emp.salary:
                qty = 0  # XXX
                if emp.work_type == 'daily':
                    rate = emp.salary / 8 * (obj.times or 0)
                else:
                    rate = emp.salary / 30 / 8 * (obj.times or 0)
            elif obj.wage_type == 'bonus' and emp.salary:
                qty = 1
                rate = emp.salary * (obj.months or 0)
        elif obj.type == "deduct":
            if obj.deduct_type == "thai_social":
                qty = 1
                rate = self.compute_thai_social(context=context)
            if obj.deduct_type == "provident":
                qty = 1
                rate = self.compute_provident(context=context)
        elif obj.type == "tax":
            if obj.tax_type == "thai":
                qty = 1
                rate = self.compute_thai_tax(context=context)["tax_month"]

        return qty, rate

    def compute_thai_social(self, context={}):
        emp_id = context.get("employee_id")
        if emp_id != 'null':
            emp_id = int(emp_id)
        emp = get_model("hr.employee").browse(emp_id)
        date = context.get("date")
        if not emp.social_register:
            return 0
        settings = get_model("hr.payroll.settings").browse(1)
        salary = emp.salary or 0
        if settings.social_min_wage is not None and salary < settings.social_min_wage:
            return 0
        if settings.social_max_wage is not None and salary > settings.social_max_wage:
            salary = settings.social_max_wage
        amt = salary * (settings.social_rate or 0) / 100
        return amt

    def compute_provident(self, context={}):
        emp_id = context.get("employee_id")
        emp = get_model("hr.employee").browse(emp_id)
        date = context.get("date")
        salary = emp.salary or 0
        amt = salary * (emp.prov_rate_employee or 0) / 100
        return amt

    def compute_thai_tax(self, context={}):
        emp_id = context.get("employee_id")
        if emp_id != 'null':
            emp_id = int(emp_id)
        emp = get_model("hr.employee").browse(emp_id)
        period = context.get("period", 12)
        date = context.get("date")
        vals = {}
        vals["B1"] = max(0, self.get_yearly_provident_fund(context=context) - 10000)
        #vals["B2"]=emp.gov_pension_fund or 0
        vals["B2"] = 0
        vals["B3"] = emp.teacher_fund or 0
        vals["B4"] = emp.old_disabled or 0
        vals["B5"] = emp.old_disabled_spouse or 0
        vals["B6"] = emp.severance_pay or 0
        vals["B7"] = vals["B1"] + vals["B2"] + vals["B3"] + vals["B4"] + vals["B5"] + vals["B6"]
        vals["C1"] = 30000
        vals["C2"] = 30000 if emp.spouse_filing_status in ("joint", "no_income") else 0
        vals["C3a"] = 15000 * (emp.num_child1 or 0)
        vals["C3b"] = 17000 * (emp.num_child2 or 0)
        vals["C4a"] = 30000 if emp.father_id_no else 0
        vals["C4b"] = 30000 if emp.mother_id_no else 0
        vals["C4c"] = 30000 if emp.spouse_father_id_no else 0
        vals["C4d"] = 30000 if emp.spouse_mother_id_no else 0
        vals["C5"] = emp.disabled_support or 0
        vals["C6"] = emp.parent_health_insurance or 0
        vals["C7"] = emp.life_insurance or 0
        vals["C8"] = min(10000, self.get_yearly_provident_fund(context=context))
        vals["C9"] = emp.retirement_mutual_fund or 0
        vals["C10"] = emp.long_term_equity_fund or 0
        vals["C11"] = emp.interest_residence or 0
        vals["C12"] = emp.other_deduct or 0
        vals["C13"] = self.get_yearly_social_security(context=context)
        vals["C14"] = vals["C1"] + vals["C2"] + vals["C3a"] + vals["C3b"] + vals["C4a"] + vals["C4b"] + vals["C4c"] + vals["C4d"] + \
            vals["C5"] + vals["C6"] + vals["C7"] + vals["C8"] + vals["C9"] + \
            vals["C10"] + vals["C11"] + vals["C12"] + vals["C13"]
        vals["A1"] = self.get_yearly_income(context=context) + vals["B6"]
        vals["A2"] = vals["B7"]
        vals["A3"] = vals["A1"] - vals["A2"]
        vals["A4"] = min(0.4 * vals["A3"], 60000)  # XXX: use settings
        vals["A5"] = vals["A3"] - vals["A4"]
        vals["A6"] = vals["C14"]
        vals["A7"] = vals["A5"] - vals["A6"]
        vals["A8"] = min(2 * (emp.education_donation or 0), 0.1 * vals["A7"])
        vals["A9"] = vals["A7"] - vals["A8"]
        vals["A10"] = min(emp.other_donation or 0, 0.1 * vals["A9"])
        vals["A11"] = vals["A9"] - vals["A10"]
        vals["A12"] = get_model("hr.tax.rate").compute_tax(vals["A11"])
        vals["A13"] = emp.house_deduct or 0
        vals["A14"] = max(0, vals["A12"] - vals["A13"])
        vals["A15"] = emp.wht_amount or 0
        vals["A16"] = vals["A14"] - vals["A15"]
        vals["A17"] = 0  # XXX
        vals["A18"] = 0
        vals["A19"] = 0
        vals["A20"] = vals["A16"]
        vals["A21"] = 0
        vals["A22"] = vals["A20"]
        vals["tax_month"] = vals["A12"] / period
        return vals

    def get_yearly_income(self, context={}):
        emp_id = context.get("employee_id")
        if emp_id != 'null':
            emp_id = int(emp_id)
        emp = get_model("hr.employee").browse(emp_id)
        year_income = context.get("year_income", 0)
        if not year_income:
            year_income = (emp.salary or 0) * 12
        return year_income

    def get_yearly_provident_fund(self, context={}):
        return 0

    def get_yearly_social_security(self, context={}):
        emp_id = context.get("employee_id")
        emp = get_model("hr.employee").browse(emp_id)
        amt = self.compute_thai_social(context=context)
        return amt * 12  # XXX

PayItem.register()
