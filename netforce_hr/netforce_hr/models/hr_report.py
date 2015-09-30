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
from netforce import database
import datetime


class Report(Model):
    _name = "hr.report"
    _store = False

    def get_attend_hist(self, context={}):
        db = database.get_connection()
        date_from = datetime.date.today() - datetime.timedelta(days=30)
        res = db.query("SELECT user_id,action,time FROM hr_attendance WHERE time>=%s ORDER BY time", date_from)
        days = {}
        sign_ins = {}
        for r in res:
            if r.action == "sign_in":
                sign_ins[r.user_id] = r.time
            elif r.action == "sign_out":
                last_in = sign_ins.get(r.user_id)
                if not last_in:
                    continue
                day = r.time[:10]
                if last_in[:10] != day:
                    continue
                t = days.get(day, 0)
                t += (datetime.datetime.strptime(r.time, "%Y-%m-%d %H:%M:%S") -
                      datetime.datetime.strptime(last_in, "%Y-%m-%d %H:%M:%S")).seconds / 3600.0
                days[day] = t
        vals = sorted(days.items())
        return {
            "value": vals,
        }

Report.register()
