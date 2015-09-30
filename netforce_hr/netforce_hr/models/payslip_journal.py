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
from netforce.access import get_active_company
from netforce.utils import get_data_path


class PayslipJournal(Model):
    _name = "hr.payslip.journal"
    _transient = True

    def _get_all(self, ids, context={}):
        res = {}
        for obj in self.browse(ids):
            total_credit = 0
            total_debit = 0
            for line in obj.lines:
                total_credit += line.credit or 0
                total_debit += line.debit or 0
            res[obj.id] = {
                'total_credit': total_credit,
                'total_debit': total_debit,
            }
        return res

    _fields = {
        'name': fields.Char("Name"),
        "payslip_id": fields.Many2One("hr.payslip", "Payslip", required=True, on_delete="cascade"),
        'note': fields.Text("Note"),
        'lines': fields.One2Many("hr.payslip.journal.line", "payslip_journal_id", "Lines"),
        'total_credit': fields.Decimal("Credit", function="_get_all", function_multi=True),
        'total_debit': fields.Decimal("Debit", function="_get_all", function_multi=True),
    }

    def _default_get(self, field_names=None, context={}, **kw):
        payslip_id = context.get("refer_id")
        payslip_id = int(payslip_id)
        lines = []
        if payslip_id:
            payslip = get_model("hr.payslip").browse(payslip_id)
            lines = payslip.get_move_lines()
        total_credit = 0
        total_debit = 0
        for line in lines:
            total_credit += line['credit'] or 0
            total_debit += line['debit'] or 0
        res = {
            'payslip_id': payslip_id,
            'name': payslip_id,
            'lines': lines,
            'total_credit': total_credit,
            'total_debit': total_debit,
        }
        return res

    def _get_payslip(self, context={}):
        payslip_id = context.get("refer_id")
        if not payslip_id:
            return None
        payslip_id = int(payslip_id)
        return payslip_id

    def _get_lines(self, context={}):
        payslip_id = context.get("refer_id")
        if not payslip_id:
            return None
        payslip_id = int(payslip_id)
        lines = []
        if payslip_id:
            payslip = get_model("hr.payslip").browse(payslip_id)
            lines = payslip.get_move_lines()
        return lines

    def _get_total_credit(self, context={}):
        payslip_id = context.get("refer_id")
        if not payslip_id:
            return 0
        payslip_id = int(payslip_id)
        lines = []
        total_credit = 0
        if payslip_id:
            payslip = get_model("hr.payslip").browse(payslip_id)
            lines = payslip.get_move_lines()
        for line in lines:
            total_credit += line['credit'] or 0
        return total_credit

    def _get_total_debit(self, context={}):
        payslip_id = context.get("refer_id")
        if not payslip_id:
            return 0
        payslip_id = int(payslip_id)
        lines = []
        total_debit = 0
        if payslip_id:
            payslip = get_model("hr.payslip").browse(payslip_id)
            lines = payslip.get_move_lines()
        for line in lines:
            total_debit += line['credit'] or 0
        return total_debit

    _defaults = {
        'payslip_id': _get_payslip,
        'name': _get_payslip,
        'lines': _get_lines,
        'total_credit': _get_total_credit,
        'total_debit': _get_total_debit,
    }

    def post(self, ids, context={}):
        obj = self.browse(ids)[0]
        if obj.total_credit != obj.total_credit:
            raise Exception("Debit & Credit is not balance!")
        payslip = obj.payslip_id
        company_id = get_active_company()
        move = payslip.move_id
        if move:
            move.to_draft()
            for line in move.lines:
                line.delete()
        pst = get_model("hr.payroll.settings").browse(1)
        journal = pst.journal_id
        if not journal:
            raise Exception("Please define journal in payroll setting.")
        if not move:
            move_vals = {
                "journal_id": journal.id,
                "number": '%s/%s' % (payslip.employee_id.code, payslip.date),
                "date": payslip.date,
                "narration": 'Paid- %s' % (payslip.date),
                "related_id": "hr.payslip,%s" % payslip.id,
                "company_id": company_id,
            }
            move_id = get_model("account.move").create(move_vals)
            move = get_model("account.move").browse(move_id)
        lines = []
        for line in obj.lines:
            lines.append(('create', {
                'description': line.description or "",
                'debit': line.debit or 0,
                'credit': line.credit or 0,
                'account_id': line.account_id.id,
            }))
        move.write({
            'lines': lines,
        })
        payslip.write({
            'move_id': move.id,
            'state': 'posted',
        })
        return {
            'next': {
                'name': 'payslip',
                'mode': 'form',
                'active_id': payslip.id,
            },
            'flash': 'payslip of employee %s has been posted!' % payslip.employee_id.code,
        }

    def update_amount(self, data={}):
        data['total_credit'] = 0
        data['total_debit'] = 0
        for line in data['lines']:
            data['total_debit'] += line['debit'] or 0
            data['total_credit'] += line['credit'] or 0
        return data

    def onchange_line(self, context={}):
        data = context['data']
        # path=context['path']
        # line=get_data_path(data,path,parent=True)
        data = self.update_amount(data)
        return data

PayslipJournal.register()
