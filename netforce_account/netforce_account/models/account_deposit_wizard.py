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

class DepositWizard(Model):
    _name = "account.deposit.wizard"
    _transient = True
    _fields = {
        "invoice_id": fields.Many2One("account.invoice", "Invoice", required=True, on_delete="cascade"),
        "type": fields.Char("Type"),
        "lines": fields.One2Many("account.deposit.wizard.line", "wiz_id", "Lines"),
        "amount_due": fields.Decimal("Amount Due on Invoice", readonly=True),
        "amount_alloc": fields.Decimal("Total Amount to Deposit", readonly=True),
        "amount_remain": fields.Decimal("Remaining Due", readonly=True),
    }

    def default_get(self, field_names={}, context={}, **kw):
        if "refer_id" not in context:
            return {}
        inv_id = int(context["refer_id"])
        inv = get_model("account.invoice").browse(inv_id)
        contact_id = inv.contact_id.id
        lines = []
        payment_type = "in" if inv.type == "out" else "out"
        for deposit in get_model("account.payment").search_browse([["type", "=", payment_type], ["pay_type", "=", "deposit"], ["contact_id", "=", contact_id], ["state", "=", "posted"], ["currency_id", "=", inv.currency_id.id], ["amount_deposit_remain",">",0]]):
            lines.append({
                "deposit_id": [deposit.id, deposit.name_get()[0][1]],
                "date": deposit.date,
                "amount_deposit_remain": deposit.amount_deposit_remain,
            })
        vals = {
            "invoice_id": [inv.id, inv.name_get()[0][1]],
            "lines": lines,
            "type": inv.type,
            "amount_due": inv.amount_due,
            "amount_alloc": 0,
            "amount_remain": inv.amount_due,
        }
        return vals

    def allocate(self, ids, context={}):
        obj = self.browse(ids)[0]
        assert obj.invoice_id.inv_type == "invoice"
        for line in obj.lines:
            if not line.amount:
                continue
            vals = {
                "invoice_id": obj.invoice_id.id,
                "deposit_id": line.deposit_id.id,
                "total_amount": line.amount,
            }
            get_model("account.deposit.alloc").create(vals)
        return {
            "next": {
                "name": "view_invoice",
                "active_id": obj.invoice_id.id,
            },
            "flash": "Invoice updated.",
        }

    def update_amounts(self, context={}):
        data = context["data"]
        amt = 0
        for line in data["lines"]:
            amt += line.get("amount", 0)
        data["amount_alloc"] = amt
        data["amount_remain"] = data["amount_due"] - amt
        return data

DepositWizard.register()
