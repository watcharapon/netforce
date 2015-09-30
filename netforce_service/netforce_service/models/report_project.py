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
from netforce.database import get_connection
from netforce.access import get_active_user, check_permission_other
import time
from datetime import *
from pprint import pprint


class ReportProject(Model):
    _name = "report.project"
    _store = False

    def time_week(self, context={}):
        d = date.today()
        date_from = d - timedelta(days=d.weekday())
        date_to = d + timedelta(days=6)
        db = get_connection()
        data = {}
        res = db.get("SELECT SUM(duration) AS duration FROM work_time WHERE date>=%s AND date<=%s", date_from, date_to)
        if not res.duration:
            return None
        data["duration"] = res.duration or 0
        res = db.get(
            "SELECT SUM(l.duration) AS bill_duration, SUM(l.duration*t.rate) AS bill_amount FROM task t,work_time l WHERE t.id=l.task_id AND t.billable AND l.date>=%s AND l.date<=%s", date_from, date_to)
        data["bill_duration"] = res.bill_duration or 0
        data["bill_amount"] = res.bill_amount or 0
        data["chart_data"] = {
            "value": [("Billable", data["bill_duration"]), ("Unbillable", data["duration"] - data["bill_duration"])],
        }
        return data

    def time_per_project(self, context={}):
        d = date.today()
        date_from = d - timedelta(days=d.weekday())
        date_to = d + timedelta(days=6)
        db = get_connection()
        res = db.query(
            "SELECT p.name AS project_name, contact.name AS contact_name, SUM(l.duration) AS duration, SUM(CASE WHEN t.billable THEN l.duration ELSE 0 END) AS bill_duration, SUM(CASE WHEN t.billable THEN l.duration*t.rate ELSE 0 END) AS bill_amount FROM project p,contact contact,task t,work_time l WHERE p.id=l.service_id AND contact.id=p.contact_id AND t.id=l.task_id AND l.date>=%s AND l.date<=%s GROUP BY project_name,contact_name", date_from, date_to)
        return res

    def time_per_employee(self, context={}):
        d = date.today()
        date_from = d - timedelta(days=d.weekday())
        date_to = d + timedelta(days=6)
        db = get_connection()
        res = db.query(
            "SELECT u.name AS employee_name, SUM(l.duration) AS duration, SUM(CASE WHEN t.billable THEN l.duration ELSE 0 END) AS bill_duration, SUM(CASE WHEN t.billable THEN l.duration*t.rate ELSE 0 END) AS bill_amount FROM timesheet ts,base_user u,task t,work_time l WHERE ts.id=l.sheet_id AND u.id=ts.user_id AND t.id=l.task_id AND l.date>=%s AND l.date<=%s GROUP BY employee_name", date_from, date_to)
        return res

    def jobs_per_user(self, context={}):
        # XXX: use read_group
        user_id = get_active_user()
        job_ids = get_model("job").search([["state", "=", "in_progress"], ["user_id", "!=", None]])
        groups = {}
        for job in get_model("job").browse(job_ids):
            name = job.user_id.login
            if name not in groups:
                groups[name] = 0
            groups[name] += 1
        data = sorted(groups.items(), key=lambda a: -a[1])
        return {"value": data}

    def tasks_per_service(self, context={}):
        db = get_connection()
        res = db.query(
            "SELECT s.code,COUNT(*) AS num FROM task t,service s WHERE s.id=t.service_id AND t.state='in_progress' GROUP BY s.code ORDER BY num DESC")
        data = []
        for r in res:
            data.append((r.code, r.num))
        return {"value": data}

    def jobs_per_service(self, context={}):
        # XXX: use read_group
        user_id = get_active_user()
        job_ids = get_model("job").search([["state", "=", "in_progress"]])
        groups = {}
        for job in get_model("job").browse(job_ids):
            if job.product_id:
                code = job.product_id.code
            else:
                code = "N/A"
            if code not in groups:
                groups[code] = 0
            groups[code] += 1
        data = sorted(groups.items(), key=lambda a: -a[1])
        other = sum([v[1] for v in data[10:]])
        data = data[:10]
        if other:
            data.append(("Other", other))
        return {"value": data}

    def tasks_per_service_user(self, context={}):
        db = get_connection()
        user_id = get_active_user()
        res = db.query(
            "SELECT s.code,COUNT(*) AS num FROM task t,job j,service s WHERE j.id=t.job_id AND s.id=j.service_id AND t.state='in_progress' AND t.user_id=%s GROUP BY s.code ORDER BY num DESC", user_id)
        data = []
        for r in res:
            data.append((r.code, r.num))
        return {"value": data}

    def tasks_per_stage(self, context={}):
        db = get_connection()
        res = db.query(
            "SELECT c.name AS categ_name,s.name AS stage_name,s.sequence,COUNT(*) AS num FROM task t,task_categ c,task_stage s WHERE c.id=t.categ_id AND s.id=t.stage_id AND t.state='in_progress' GROUP BY c.name,s.name,s.sequence ORDER BY c.name,s.sequence,s.name")
        categ_data = {}
        for r in res:
            categ_data.setdefault(r.categ_name, []).append((r.stage_name, r.num))
        categs = []
        for categ_name, data in sorted(categ_data.items()):
            categs.append({
                "categ_name": categ_name,
                "data": data,
            })
        return {"categs": categs}

    def click_service(self, context={}):
        categ = context["category"]
        res = get_model("service").search([["code", "=", categ]])
        if not res:
            raise Exception("Service not found: %s" % categ)
        serv_id = res[0]
        return {
            "next": {
                "name": "job_analysis",
                "condition": '[["state","=","in_progress"],["service_id","child_of",%s]]' % serv_id,
                "group_fields": "",
            }
        }

    def click_service_user(self, context={}):
        categ = context["category"]
        res = get_model("service").search([["code", "=", categ]])
        if not res:
            raise Exception("Service not found: %s" % categ)
        serv_id = res[0]
        user_id = get_active_user()
        return {
            "next": {
                "name": "job_analysis",
                "condition": '[["state","=","in_progress"],["service_id","child_of",%s],["user_id","=",%s]]' % (serv_id, user_id),
                "group_fields": "",
            }
        }

    def click_user(self, context={}):
        categ = context["category"]
        res = get_model("base.user").search([["login", "=", categ]])
        if not res:
            raise Exception("User login not found: %s" % categ)
        user_id = res[0]
        return {
            "next": {
                "name": "job_analysis",
                "condition": '[["state","=","in_progress"],["user_id","=",%s]]' % user_id,
                "group_fields": "",
            }
        }

ReportProject.register()
