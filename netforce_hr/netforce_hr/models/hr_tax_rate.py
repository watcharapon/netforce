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


class TaxRate(Model):
    _name = "hr.tax.rate"
    _fields = {
        "settings_id": fields.Many2One("hr.payroll.settings", "Settings", required=True),
        "sequence": fields.Integer("Step No."),
        "min_income": fields.Decimal("Min. Net Income"),
        "max_income": fields.Decimal("Max. Net Income"),
        "rate": fields.Decimal("Tax Rate"),
    }
    _order = "sequence"

    def compute_tax(self, income=0):
        total_tax = 0
        total_base = 0
        for obj in self.search_browse([]):
            if obj.min_income and income < obj.min_income:
                break
            base = min(income, obj.max_income) - total_base
            tax = base * (obj.rate or 0) / 100
            total_tax += tax
            total_base += base
        return total_tax

TaxRate.register()
