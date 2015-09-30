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

from datetime import datetime, timedelta

from netforce.model import Model, fields


class Schedule(Model):
    _name = "hr.schedule.time"
    _string = "Schedule Time"

    def fmt_time(self, time_str):
        time_str = time_str or ""
        time_str = time_str.replace(".", ":")
        if not time_str:
            time_str = '00:00'
        return time_str

    def get_total(self, ids, context={}):
        res = {}
        for obj in self.browse(ids):
            time_start = datetime.strptime(self.fmt_time(obj.time_start), '%H:%S')
            time_stop = datetime.strptime(self.fmt_time(obj.time_stop), '%H:%S')
            hrs = (time_stop - time_start).seconds / 60.0 / 60.0
            res[obj.id] = hrs
        return res

    _fields = {
        'schedule_id': fields.Many2One('hr.schedule', "Schedule"),
        "name": fields.Char("Name", search=True),
        'time_start': fields.Char("Time Start", size=5),
        'time_stop': fields.Char("Time Stop", size=5),
        'time_total': fields.Decimal("Working Time (HRS)", function="get_total"),
    }


Schedule.register()
