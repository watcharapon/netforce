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


class ServiceContractLine(Model):
    _name = "service.contract.line"
    _fields = {
        "contract_id": fields.Many2One("service.contract", "Contract", required=True, on_delete="cascade"),
        "service_item_id": fields.Many2One("service.item", "Service Item"),
        "template_id": fields.Many2One("service.contract.template", "Contract Template"),
        "amount_labor": fields.Decimal("Labor Amount"),
        "amount_part": fields.Decimal("Parts Amount"),
        "amount_other": fields.Decimal("Other Amount"),
        "amount_total": fields.Decimal("Total Amount", function="get_total"),
        "account_id": fields.Many2One("account.account", "Account"),
    }

    def get_total(self, ids, context={}):
        vals = {}
        for obj in self.browse(ids):
            amt = 0
            amt += obj.amount_part or 0
            amt += obj.amount_labor or 0
            amt += obj.amount_other or 0
            vals[obj.id] = amt
        return vals

ServiceContractLine.register()
