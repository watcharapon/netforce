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


class Settings(Model):
    _name = "hr.payroll.settings"
    _fields = {
        "tax_rates": fields.One2Many("hr.tax.rate", "settings_id", "Tax Rates"),
        "social_rate": fields.Decimal("Rate (%)"),
        "social_min_wage": fields.Decimal("Min Wage Per Month"),
        "social_max_wage": fields.Decimal("Max Wage Per Month"),
        "comments": fields.One2Many("message", "related_id", "Comments"),
        "social_number": fields.Char("SSO Identification No."),
        "prov_name": fields.Char("Fund Name"),
        "child_alw_limit": fields.Integer("Limit to Children"),
        "child_alw_limit": fields.Integer("Limit to Children"),
        'journal_id': fields.Many2One("account.journal", "Journal"),
        'bank_account_id': fields.Many2One("account.account", "Bank Account"),
        'sso_account_id': fields.Many2One("account.account", "SSO Account"),
        'sso_comp_support': fields.Boolean("SSO Company Support"),
        'intg_acc': fields.Boolean("Integrate to Account"),
        "work_day_sat": fields.Boolean("Work On Saturday"),
        "work_day_sun": fields.Boolean("Work On Sunday"),
    }

Settings.register()
