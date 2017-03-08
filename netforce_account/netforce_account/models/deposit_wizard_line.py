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

class DepositWizardLine(Model):
    _name = "account.deposit.wizard.line"
    _transient = True
    _fields = {
        "wiz_id": fields.Many2One("account.deposit.wizard", "Wizard", on_delete="cascade"),
        "invoice_id": fields.Many2One("account.invoice", "Invoice", on_delete="cascade"),
        "deposit_id": fields.Many2One("account.payment", "Deposit", required=True, on_delete="cascade"),
        "date": fields.Date("Date", readonly=True),
        "amount_deposit_remain": fields.Decimal("Outstanding Deposit", readonly=True),
        "amount": fields.Decimal("Amount"),
    }

    def delete(self, ids, **kw):
        for obj in self.browse(ids):
            for alloc in get_model("account.deposit.alloc").search_browse([["invoice_id","=",obj.invoice_id.id],["deposit_id","=",obj.deposit_id.id], ["total_amount","=",obj.amount]]):
                alloc.delete()
        super().delete(ids, **kw)

DepositWizardLine.register()
