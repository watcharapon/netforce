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

from datetime import *
import time

from netforce.model import Model, fields

FMT_TIME = '%Y-%m-%d %H:%M:%S'
FMT_DAY = '%Y-%m-%d'


class Holiday(Model):
    _name = "hr.holiday"
    _string = "Holiday"
    _fields = {
        "name": fields.Char("Name", search=True),
        "date": fields.Date("Date", required=True, search=True),
        "description": fields.Text("Description"),
        "comments": fields.One2Many("message", "related_id", "Comments"),
        'generic': fields.Boolean("Generic"),
    }
    _defaults = {
        "date": lambda *a: time.strftime("%Y-%m-%d"),
        "comday": False,
        'generic': False,
    }
    _order = "date"

    _sql_constraints = [
        ("hr_holiday_date_uniq", "unique (date)", "Date should be unique"),
    ]

    def get_holidays(self, context={}):
        date_from = context.get('start_date', time.strftime(FMT_DAY))
        date_to = context.get('end_date', time.strftime(FMT_DAY))
        cond = [
            ['date', '>=', date_from],
            ['date', '<=', date_to],
        ]
        res = set()
        for r in self.search_read(cond, ['date']):
            res.update({r['date']})
        yearnow, month, date = time.strftime(FMT_DAY).split("-")
        cond = [['generic', '=', True]]
        for r in self.search_read(cond, ['date']):
            y, m, d = r['date'].split("-")
            date = '-'.join([yearnow, m, d])
            res.update({date})
        return list(res)

    def is_holiday(self,ds):
        d=datetime.strptime(ds,"%Y-%m-%d")
        w=d.weekday()
        if w==5 or w==6:
            return True
        res=self.search([["date","=",ds]])
        if res:
            return True
        return False

Holiday.register()
