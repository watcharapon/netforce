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

import time

from netforce.model import Model, fields, get_model
from netforce import database
from netforce.access import get_active_company


class Employee(Model):
    _name = "hr.employee"
    _string = "Employee"
    _name_field = "first_name"  # XXX
    _multi_company = True
    _key = ["code","company_id"]
    _export_field = "code"

    _fields = {
        "code": fields.Char("Employee Code", search=True),
        "department_id": fields.Many2One("hr.department", "Department", search=True),
        "title": fields.Selection([["mr", "Mr."], ["mrs", "Mrs."], ["miss", "Miss"], ["ms", "Ms."]], "Title"),
        "first_name": fields.Char("First Name", search=True, translate=True),
        "last_name": fields.Char("Last Name", required=True, search=True, translate=True),
        "hire_date": fields.Date("Hire Date"),
        "work_status": fields.Selection([["working", "Working"], ["dismissed", "Dismissed"], ["resigned", "Resigned"], ["died", "Died"]], "Work Status"),
        "work_type": fields.Selection([["monthly", "Monthly"], ["daily", "Daily"], ["hourly", "Job"]], "Work Type"),
        "resign_date": fields.Date("Resign Date"),
        "position": fields.Char("Position", search=True),
        "birth_date": fields.Date("Birth Date"),
        "age": fields.Integer("Age", function="get_age"),
        "gender": fields.Selection([["male", "Male"], ["female", "Female"]], "Gender"),
        "marital_status": fields.Selection([["single", "Single"], ["married", "Married"], ["divorced", "Divorced"], ["widowed", "Widowed"]], "Marital Status"),
        "addresses": fields.One2Many("address", "employee_id", "Address"),
        "id_no": fields.Char("ID No."),
        "drive_license_type": fields.Selection([["car", "Car"], ['motorcycle', 'Motorcycle']], "Driving License"),
        "drive_license_no": fields.Char("Driving License No."),
        "country_id": fields.Many2One("country", "Country"),
        "bank_account": fields.Char("Bank Account"),
        "salary": fields.Decimal("Salary"),
        "picture": fields.File("Picture"),
        "tax_no": fields.Char("Taxpayer ID No."),
        "spouse_first_name": fields.Char("Spouse First Name"),
        "spouse_last_name": fields.Char("Spouse Last Name"),
        "spouse_title": fields.Selection([["mr", "Mr."], ["ms", "Ms."]], "Spouse Title"),
        "spouse_birth_date": fields.Date("Spouse Birth Date"),
        "spouse_tax_no": fields.Char("Spouse Tax ID No"),
        "spouse_status": fields.Selection([["married", "Married existed throughout this tax year"], ["married_new", "Married during this tax year"], ["divorced", "Divorced during tax year"], ["deceased", "Deceased during tax year"]], "Spouse Status"),
        "spouse_filing_status": fields.Selection([["joint", "Has income and file joint return"], ["separate", "Has income and file separate tax return"], ["no_income", "Has no income"]], "Spouse Filing Status"),
        "num_child1": fields.Integer("No. of Children #1 (C3)"),
        "num_child2": fields.Integer("No. of Children #2 (C3)"),
        "social_no": fields.Char("Social No."),
        "social_register": fields.Boolean("Register Soc. Secur."),
        "social_calc_method": fields.Selection([["regular", "Regular Rate"], ["none", "Not Participate"], ["special", "Special Rate"]], "Calc. Method"),
        "prov_fund_no": fields.Char("Prov. Fund No."),
        "prov_open_date": fields.Char("Opened Prov. Fund A/C Date"),
        "prov_rate_employer": fields.Decimal("Employer Contribution (%)"),
        "prov_rate_employee": fields.Decimal("Employee Contribution (%)"),
        "gov_pension_fund": fields.Decimal("Gov. Pension Fund Amount (B2)"),
        "teacher_fund": fields.Decimal("Teacher Aid Fund Amount (B3)"),
        "old_disabled": fields.Decimal("Older than 65 or disabled (personal, B4)"),
        "old_disabled_spouse": fields.Decimal("Older than 65 or disabled (spouse, B5)"),
        "severance_pay": fields.Decimal("Severance Pay (B6)"),
        "education_donation": fields.Decimal("Education Donations (A8)"),
        "other_donation": fields.Decimal("Other Donations (A10)"),
        "house_deduct": fields.Decimal("Exemption for home buyer (A13)"),
        "wht_amount": fields.Decimal("Withholding Tax Amount (A15)"),
        "father_id_no": fields.Char("Father ID No. (C4)"),
        "mother_id_no": fields.Char("Mother ID No. (C4)"),
        "spouse_father_id_no": fields.Char("Father of spouse ID No. (C4)"),
        "spouse_mother_id_no": fields.Char("Mother of spouse ID No. (C4)"),
        "disabled_support": fields.Decimal("Disabled person support (C5)"),
        "parent_health_insurance": fields.Decimal("Parent Health Insurance (C6)"),
        "life_insurance": fields.Decimal("Life Insurance (C7)"),
        "retirement_mutual_fund": fields.Decimal("Retirement Mutual Fund (C9)"),
        "long_term_equity_fund": fields.Decimal("Long Term Equity Fund (C10)"),
        "interest_residence": fields.Decimal("Interest paid for residence (C11)"),
        "other_deduct": fields.Decimal("Other Deductions (C12)"),
        "comments": fields.One2Many("message", "related_id", "Comments"),
        "active": fields.Boolean("Active"),
        "time_in": fields.DateTime("Last Sign In", function="get_attend", function_multi=True),
        "time_out": fields.DateTime("Last Sign Out", function="get_attend", function_multi=True),
        "attend_state": fields.Selection([["absent", "Absent"], ["present", "Present"]], "Status", function="get_attend", function_multi=True),
        "user_id": fields.Many2One("base.user", "User", search=True),
        "payslips": fields.One2Many("hr.payslip", "employee_id", "Payslips"),
        "documents": fields.One2Many("document", "related_id", "Documents"),
        "phone": fields.Char("Phone", search=True),
        "approver_id": fields.Many2One("base.user", "Approver"),
        "company_id": fields.Many2One("company", "Company"),
        "leave_types": fields.Many2Many("hr.leave.type", "Leave Types"),
        "attendance_id": fields.Integer("Attendance ID"),
        "email": fields.Char("Email", search=True),
        'profile_id': fields.Many2One("hr.payitem.profile", "Pay Item Profile"),
        'schedule_id': fields.Many2One("hr.schedule", "Working Schedule"),
        'leaves': fields.One2Many('hr.leave', 'employee_id', 'Leaves'),
    }

    def _get_code(self, context={}):
        while 1:
            code = get_model("sequence").get_number("employee")
            if not code:
                return None
            res = self.search([["code", "=", code]])
            if not res:
                return code
            get_model("sequence").increment("employee")

    _defaults = {
        "active": True,
        "work_status": "working",
        "code": _get_code,
        "company_id": lambda *a: get_active_company(),
    }
    _order = "code,first_name,last_name"

    def name_get(self, ids, context={}):
        vals = []
        for obj in self.browse(ids):
            if obj.first_name:
                name = obj.first_name + " " + obj.last_name
            else:
                name = obj.last_name
            if obj.code:
                name += " [%s]" % obj.code
            vals.append((obj.id, name))
        return vals

    def name_search(self, name, condition=[], limit=None, context={}):
        cond = [["or", ["first_name", "ilike", "%" + name + "%"],
                 ["last_name", "ilike", "%" + name + "%"], ["code", "ilike", "%" + name + "%"]], condition]
        ids = self.search(cond, limit=limit)
        return self.name_get(ids, context)

    def get_age(self, ids, context={}):
        vals = {}
        cr_year = int(time.strftime('%Y'))
        for obj in self.browse(ids):
            if obj.birth_date:
                age = cr_year - int(obj.birth_date[0:4])
            else:
                age = 0
            vals[obj.id] = age
        return vals

    def get_attend(self, ids, context={}):
        vals = {}
        for obj in self.browse(ids):
            # user_id=obj.user_id.id
            # if user_id:
                # db=database.get_connection()
                #res=db.get("SELECT MAX(time) AS time_in FROM hr_attendance WHERE user_id=%s AND action='sign_in'",user_id)
                # time_in=res.time_in
                #res=db.get("SELECT MAX(time) AS time_out FROM hr_attendance WHERE user_id=%s AND action='sign_out'",user_id)
                # time_out=res.time_out
            # else:
                # time_in=None
                # time_out=None
            db = database.get_connection()
            res = db.get(
                "SELECT MAX(time) AS time_in FROM hr_attendance WHERE employee_id=%s AND action='sign_in'", obj.id)
            time_in = res.time_in
            res = db.get(
                "SELECT MAX(time) AS time_out FROM hr_attendance WHERE employee_id=%s AND action='sign_out'", obj.id)
            time_out = res.time_out
            if time_in:
                if time_out and time_out > time_in:
                    state = "absent"
                else:
                    today = time.strftime("%Y-%m-%d")
                    if time_in.startswith(today):
                        state = "present"
                    else:
                        state = "absent"
                    # should not show timeout of anotherday
                    # if not time_out.startswith(today):
                        # time_out=None
            else:
                state = "absent"
            vals[obj.id] = {
                "time_in": time_in,
                "time_out": time_out,
                "attend_state": state,
            }
        return vals

    def get_address(self, ids, context={}):
        obj = self.browse(ids)[0]
        if not obj.addresses:
            return ""
        addr = obj.addresses[0]
        res = addr.get_address_text()
        return res[addr.id]

    def onchange_num_child(self, context={}):
        data = context["data"]
        setting = get_model("hr.payroll.settings").browse(1)
        child_alw_limit = setting.child_alw_limit or 0
        child_total = (data['num_child1'] or 0) + (data['num_child2'] or 0)
        if child_alw_limit and child_total > child_alw_limit:
            data['num_child1'] = 0
            data['num_child2'] = 0
        return data


Employee.register()
