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


class ScheduleLine(Model):
    _name = "hr.schedule.line"
    _string = "Schedule Line"

    def get_time_stop(self, ids, context={}):
        res = {}
        for obj in self.browse(ids):
            datenow = datetime.now().strftime("%Y-%m-%d")
            time_start = '%s %s' % (datenow, obj.time_start)
            time_total = obj.time_total or 0.0
            if obj.skip_mid:
                time_total += 1  # 12.00-13.00
            seconds = (time_total) * 60 * 60
            time_stop = datetime.strptime(time_start, '%Y-%m-%d %H:%S') + timedelta(seconds=seconds)
            res[obj.id] = time_stop.strftime("%H:%S")
        return res

    _fields = {
        'schedule_id': fields.Many2One("hr.schedule", "Schedule"),
        "dow": fields.Selection([["1", "Monday"], ["2", "Tuesday"], ["3", "Wednesday"], ["4", "Thursday"], ["5", "Friday"], ["6", "Saturday"], ["7", "Sunday"]], "Day Of Week"),
        'time_start': fields.Char("Time Start"),
        'time_stop': fields.Char("Time Stop"),
    }

    order = "dow, time_start"

ScheduleLine.register()
