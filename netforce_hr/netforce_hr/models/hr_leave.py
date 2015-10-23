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

import time
from datetime import datetime, timedelta

from netforce.model import Model, fields, get_model
from netforce.access import get_active_user, set_active_user
from netforce.access import get_active_company
from netforce import database
from decimal import Decimal

FMT_TIME = '%Y-%m-%d %H:%M:%S'
FMT_DAY = '%Y-%m-%d'


class Leave(Model):
    _name = "hr.leave"
    _string = "Leave Request"
    _multi_company = True
    _key = ["number"]

    _fields = {
        "name": fields.Char("Name", function="get_name"),
        "number": fields.Char("Number"),
        "date": fields.Date("Request Date", required=True),
        "employee_id": fields.Many2One("hr.employee", "Employee", required=True),
        "employee_work_status": fields.Selection([["working", "Working"], ["dismissed", "Dismissed"], ["resigned", "Resigned"], ["died", "Died"]], "Work Status"),
        "leave_type_id": fields.Many2One("hr.leave.type", "Leave Type", required=True),
        "leave_reason": fields.Text("Leave Reason"),
        "start_date": fields.DateTime("Start Date", required=True),
        "end_date": fields.DateTime("End Date", required=True),
        "state": fields.Selection([["draft", "Draft"], ["waiting_approval", "Awaiting Approval"], ["approved", "Approved"], ["rejected", "Rejected"]], "Status"),
        "days_requested": fields.Decimal("Days Requested", function="cal_days_requested"),
        "days_remaining": fields.Decimal("Days Remaining", function="cal_days_remaining"),
        "documents": fields.One2Many("document", "related_id", "Documents"),
        "comments": fields.One2Many("message", "related_id", "Comments"),
        "time_from": fields.Char("From Time"),
        "time_to": fields.Char("To Time"),
        "period_id": fields.Many2One("hr.leave.period", "Leave Period", required=True),
        'schedule_id': fields.Many2One("hr.schedule", "Working Schedule"),
        "user_id": fields.Many2One("base.user", "User"),
        "company_id": fields.Many2One("company", "Company"),
    }

    def _get_number(self, context={}):
        user_id = get_active_user()
        set_active_user(1)
        seq_id = get_model("sequence").find_sequence(type="leave_request")
        if not seq_id:
            return None
        while 1:
            num = get_model("sequence").get_next_number(seq_id)
            user_id = get_active_user()
            set_active_user(1)
            res = self.search([["number", "=", num]])
            set_active_user(user_id)
            if not res:
                return num
            get_model("sequence").increment_number(seq_id)
        set_active_user(user_id)

    def _get_employee(self, context={}):
        user_id = get_active_user()
        res = get_model("hr.employee").search([["user_id", "=", user_id]])
        if not res:
            return None
        return res[0]

    _defaults = {
        "state": "draft",
        "date": lambda *a: time.strftime(FMT_DAY),
        "period_type": "day",
        "period_hour": 0,
        "number": _get_number,
        "employee_id": _get_employee,
        "company_id": lambda *a: get_active_company(),
        'start_date': lambda *a: '%s 08:30:00' % time.strftime(FMT_DAY),
        'end_date': lambda *a: '%s 18:00:00' % time.strftime(FMT_DAY),
        'user_id': lambda *a: get_active_user(),
    }

    _order = "date desc, number desc"

    def get_name(self, ids, context={}):
        vals = {}
        for obj in self.browse(ids):
            emp = obj.employee_id
            vals[obj.id] = "%s %s" % (emp.first_name, emp.last_name)
        return vals

    def get_holidays(self, ids, context={}):
        date_from = context.get('date_from', time.strftime(FMT_DAY))
        date_to = context.get('date_to', time.strftime(FMT_DAY))
        cond = [
            ['date', '>=', date_from],
            ['date', '<=', date_to],
        ]
        res = set()
        for r in get_model("hr.holiday").search_read(cond, ['date']):
            res.update({r['date']})
        return list(res)

    def daterange(self, start_date, end_date):
        # interate between start date and stop date
        for n in range(int((end_date - start_date).days)):
            yield start_date + timedelta(n)

    def get_day_request(self, data={}):
        day_off = [5, 6]  # Sat and Sun XXX
        default_hour = 8
        total_break = 0
        part1 = 0
        employee_id = data.get('employee_id')
        if not employee_id:
            return 0
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        if not start_date or not end_date:
            return 0
        holidays = get_model("hr.holiday").get_holidays(context=data)
        emp = get_model("hr.employee").browse(employee_id)
        start_date = datetime.strptime(start_date, FMT_TIME)
        end_date = datetime.strptime(end_date, FMT_TIME)
        total_day_off = 0
        schedule = emp.schedule_id
        if data.get('schedule_id'):
            schedule = get_model("hr.schedule").browse(data['schedule_id'])
        if schedule:
            default_hour = schedule.working_hour or 0
            total_break = schedule.total_break or 0
            part1 = schedule.part1 or 0
            for rdate in self.daterange(start_date, end_date + timedelta(days=1)):
                hdate = rdate.strftime(FMT_DAY)
                if hdate in holidays:
                    total_day_off += 1
                dow = rdate.weekday()
                if dow in day_off:
                    total_day_off += 1
                else:
                    #items=schedule.get_day(context={'dow': dow})
                    pass
        total_day = 0
        total_hrs = 0
        total_day -= total_day_off
        if end_date >= start_date:
            diff = end_date - start_date
            total_day = diff.days
            total_day -= total_day_off
            total_sec = diff.seconds
            total_hrs = total_sec / 60 / 60
        if total_hrs >= part1 and total_hrs <= part1 + total_break and part1 > 0:
            hrs2day = Decimal(0.5)
        else:
            if total_hrs >= part1 + total_break * 2:  # XXX *2
                total_hrs -= total_break
            hrs2day = (total_hrs / default_hour)
        res = total_day + hrs2day
        return Decimal(res)

    def cal_days_requested(self, ids, context={}):
        res = {}
        for obj in self.browse(ids):
            emp = obj.employee_id
            data = {
                'employee_id': emp.id,
                'start_date': obj.start_date,
                'end_date': obj.end_date,
            }
            res[obj.id] = self.get_day_request(data)
        return res

    def cal_days_remaining(self, ids, context={}):
        vals = {}
        for obj in self.browse(ids):
            period_id = obj.period_id.id
            emp_id = obj.employee_id.id
            vals[obj.id] = self.get_remaining(emp_id, period_id)
        return vals

    def get_remaining(self, emp_id=None, period_id=None):
        if not emp_id or not period_id:
            return 0
        requested = self.search_read(
            [["period_id", "=", period_id], ["state", "=", "approved"], ["employee_id", "=", emp_id]], ["days_requested"])
        requested = sum([d.get("days_requested") or 0 for d in requested])
        if period_id:
            total = get_model("hr.leave.period").read([period_id], ["max_days"])[0].get("max_days") or 0
        else:
            total = 0
        return total - requested

    def submit_for_approval(self, ids, context={}):
        for obj in self.browse(ids):
            if obj.state != "draft":
                raise Exception("Invalid state")
            obj.write({"state": "waiting_approval"})
            obj.trigger("submit_approval")

    def approve(self, ids, context={}):
        user_id = get_active_user()
        user = get_model("base.user").browse(user_id)
        res = get_model("hr.employee").search([["user_id", "=", user_id]])
        if res:
            emp_id = res[0]
        for obj in self.browse(ids):
            if obj.state not in ("draft", "waiting_approval"):
                raise Exception("Invalid state")
            if res and obj.employee_id.id == emp_id:
                if obj.employee_id.approver_id:
                    raise Exception("User %s is not authorized to approve his own leave requests" % user.name)
            else:
                if obj.employee_id.approver_id.id != user_id:
                    raise Exception("User %s is not authorized to approve leave requests of employee %s" %
                                    (user.name, obj.employee_id.name_get()[0][1]))
            obj.write({"state": "approved"})
            vals = {
                "related_id": "hr.leave,%s" % obj.id,
                "body": "Approved by %s" % user.name,
            }
            get_model("message").create(vals)
            obj.trigger("approved")

    def reject(self, ids, context={}):
        user_id = get_active_user()
        user = get_model("base.user").browse(user_id)
        res = get_model("hr.employee").search([["user_id", "=", user_id]])
        if res:
            emp_id = res[0]
        for obj in self.browse(ids):
            if obj.state not in ("draft", "waiting_approval"):
                raise Exception("Invalid state")
            if res and obj.employee_id.id == emp_id:
                if obj.employee_id.approver_id:
                    raise Exception("User %s is not authorized to reject his own leave requests" % user.name)
            else:
                if obj.employee_id.approver_id.id != user_id:
                    raise Exception("User %s is not authorized to reject leave requests of employee %s" %
                                    (user.name, obj.employee_id.name_get()[0][1]))
            obj.write({"state": "rejected"})
            vals = {
                "related_id": "hr.leave,%s" % obj.id,
                "body": "Rejected by %s" % user.name,
            }
            get_model("message").create(vals)
            obj.trigger("rejected")

    def do_reopen(self, ids, context={}):
        user_id = get_active_user()
        user = get_model("base.user").browse(user_id)
        res = get_model("hr.employee").search([["user_id", "=", user_id]])
        if res:
            emp_id = res[0]
        for obj in self.browse(ids):
            assert obj.state in ("rejected", "approved")
            if res and obj.employee_id.id == emp_id:
                if obj.employee_id.approver_id:
                    raise Exception("User %s is not authorized to reopen his own leave requests" % user.name)
            else:
                if obj.employee_id.approver_id.id != user_id:
                    raise Exception("User %s is not authorized to reopen leave requests of employee %s" %
                                    (user.name, obj.employee_id.name_get()[0][1]))
            obj.write({"state": "waiting_approval"})

    def to_draft(self, ids, context={}):
        for obj in self.browse(ids):
            obj.write({"state": "draft"})

    def convert_date(self, date_in):
        date_out = [int(x) for x in date_in.split("-")]
        return date(date_out[0], date_out[1], date_out[2])

    def write(self, ids, vals, **kw):
        obj = self.browse(ids)[0]
        vals['employee_work_status'] = obj.employee_id.work_status
        super().write(ids, vals, **kw)

    def onchange_date(self, context={}):
        data = context['data']
        data['days_requested'] = self.get_day_request(data)
        return data

    def onchange_employee(self, context={}):
        data = context["data"]
        data["period_id"] = None
        data["leave_type_id"] = None
        data['days_remaining'] = None
        data['days_requested'] = None
        data['schedule_id'] = None
        employee_id = data['employee_id']
        schd = get_model("hr.employee").browse(employee_id).schedule_id
        if schd:
            data['schedule_id'] = schd.id
            datenow = datetime.now()
            wd = datenow.weekday()
            res = []
            for line in schd.lines:
                dow = int(line.dow or '0') - 1
                if wd == dow:
                    res.append({
                        'time_start': '%s:00' % line.time_start,
                        'time_stop': '%s:00' % line.time_stop,
                    })
            if res:
                data['start_date'] = '%s %s' % (datenow.strftime(FMT_DAY), res[0]['time_start'])
                data['end_date'] = '%s %s' % (datenow.strftime(FMT_DAY), res[-1]['time_stop'])
                data['days_requested'] = self.get_day_request(data)
        return data

    def onchange_type(self, context={}):
        data = context["data"]
        leave_type = data["leave_type_id"]
        con = "leave_type_id = %s" % (leave_type)
        year = datetime.now().strftime("%Y")
        db = database.get_connection()
        pids = db.query("SELECT id FROM hr_leave_period WHERE %s" % con)
        pids = [pid["id"] for pid in pids]
        sids = []
        for obj in get_model("hr.leave.period").browse(pids):
            if obj.get("date_to").find(year) != -1:
                sids.append(obj.id)
                data['days_remaining'] = obj.max_days or 0
        if sids:
            pid = sids[-1]
            data["period_id"] = pid
            if data.get("employee_id"):
                data['days_remaining'] = self.get_remaining(data['employee_id'], pid)
        else:
            data["period_id"] = None
        return data

Leave.register()
