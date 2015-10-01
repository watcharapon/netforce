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

from netforce.model import Model, fields, get_model, clear_cache
from netforce.database import get_connection
import time
import datetime
from netforce.access import get_active_user, set_active_user


class Task(Model):
    _name = "task"
    _string = "Task"
    _fields = {
        "project_id": fields.Many2One("project", "Project", search=True), # XXX: deprecated
        "job_id": fields.Many2One("job", "Service Order", search=True), # XXX: deprecated
        "related_id": fields.Reference([["project","Project"],["job","Job"],["rental.order","Rental Order"]],"Related To"),
        "name": fields.Char("Task Name", required=True, search=True),
        "deadline": fields.Date("Deadline", search=True),
        "description": fields.Text("Description"),
        "state": fields.Selection([["in_progress", "In Progress"], ["done", "Completed"], ["waiting", "Waiting"], ["canceled", "Canceled"]], "Status", required=True),
        "user_id": fields.Many2One("base.user", "Assigned To"),  # XXX: deprecated
        "documents": fields.One2Many("document", "related_id", "Documents"),
        "comments": fields.One2Many("message", "related_id", "Comments"),
        "overdue": fields.Boolean("Overdue", function="get_overdue", function_search="search_overdue"),
        "days_late": fields.Integer("Days Late", function="get_days_late"),
        "planned_duration": fields.Decimal("Planned Duration (Hours)"),
        "resource_id": fields.Many2One("service.resource", "Assigned To",search=True),
        "documents": fields.One2Many("document", "related_id", "Documents"),
        "priority": fields.Integer("Priority",search=True),
        "date_created": fields.Date("Date Created"),
        "date_started": fields.Date("Date Started"),
        "date_completed": fields.Date("Date Completed"),
        "est_date_completed": fields.Date("Est. Completion Date"),
        "actual_duration": fields.Decimal("Actual Duration (Hours)"),
        "requested_by_id": fields.Many2One("contact","Requested By"),
    }
    _order = "priority,id"

    _defaults = {
        "state": "in_progress",
    }

    def get_overdue(self, ids, context={}):
        vals = {}
        for obj in self.browse(ids):
            if obj.deadline:
                vals[obj.id] = obj.deadline < time.strftime("%Y-%m-%d") and obj.state != "done"
            else:
                vals[obj.id] = False
        return vals

    def search_overdue(self, clause, context={}):
        return [["deadline", "<", time.strftime("%Y-%m-%d")], ["state", "!=", "done"], ["job_id.state", "=", "in_progress"]]

    def get_days_late(self, ids, context={}):
        vals = {}
        d = datetime.datetime.now()
        for obj in self.browse(ids):
            if obj.deadline:
                vals[obj.id] = max(0, (d - datetime.datetime.strptime(obj.deadline, "%Y-%m-%d")).days) or None
            else:
                vals[obj.id] = None
        return vals

    def view_task(self, ids, context={}):
        obj = self.browse(ids[0])
        return {
            "next": {
                "name": "job",
                "mode": "form",
                "active_id": obj.job_id.id,
            }
        }

    def set_done(self, ids, context={}):
        print("task.set_done", ids)
        for obj in self.browse(ids):
            obj.write({"state": "done"})

    def click_task(self, ids, context={}):
        task = self.browse(ids)[0]
        return {
            "next": {
                "name": "job",
                "active_id": task.job_id.id,
                "mode": "page",
            }
        }

Task.register()
