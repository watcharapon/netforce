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
import time
from netforce import access


class Issue(Model):
    _name = "issue"
    _string = "Issue"
    _fields = {
        "contact_id": fields.Many2One("contact", "Customer", search=True),
        "contact_person_id": fields.Many2One("contact", "Contact Person", search=True),
        "project_id": fields.Many2One("project", "Project", search=True),
        "job_id": fields.Many2One("job", "Service Order", search=True),
        "service_item_id": fields.Many2One("service.item", "Service Item", search=True),
        "date": fields.DateTime("Date Created", required=True, search=True),
        "name": fields.Char("Subject", required=True, search=True),
        "report_by_id": fields.Many2One("base.user", "Reported By", search=True),
        "assigned_to_id": fields.Many2One("base.user", "Assigned To", search=True),
        "details": fields.Text("Details", search=True),
        "state": fields.Selection([["open", "Open"], ["closed", "Closed"]], "Status", required=True),
        "priority": fields.Selection([["low", "Low"], ["normal", "Normal"], ["high", "High"]], "Priority", search=True),
        "documents": fields.One2Many("document", "related_id", "Documents"),
        "promised_date": fields.Date("Promised Date"),
        "response_date": fields.DateTime("Response Date"),
        "comments": fields.One2Many("message", "related_id", "Comments"),
        "quotations": fields.One2Many("sale.quot", "related_id", "Quotations"),
        "jobs": fields.One2Many("job", "related_id", "Service Orders"),
        "activities": fields.One2Many("activity", "related_id", "Activities"),
        "service_type_id": fields.Many2One("service.type", "Service Type", search=True),
    }
    _order = "date desc"

    _defaults = {
        "state": "open",
        "date": lambda *a: time.strftime("%Y-%m-%d %H:%M:%S"),
        "report_by_id": lambda *a: access.get_active_user(),
        "priority": "normal",
    }

    def create(self, vals, **kw):
        new_id = super().create(vals, **kw)
        assign_ids = []
        assigned_to_id = vals.get("assigned_to_id")
        if assigned_to_id:
            assign_ids.append(new_id)
        if assign_ids:
            self.trigger(assign_ids, "assigned")
        return new_id

    def write(self, ids, vals, **kw):
        event = None
        assign_ids = []
        assigned_to_id = vals.get("assigned_to_id")
        state = vals.get("state")
        event_helper = {
            "closed": "closed",
            "open": "reopened"
        }
        if assigned_to_id:
            assign_ids += ids
            event = "assigned"
        elif state:
            assign_ids += ids
            event = event_helper[state]
        super().write(ids, vals, **kw)
        if assign_ids:
            self.trigger(assign_ids, event)

    def copy_to_service_order(self, ids, context={}):
        obj = self.browse(ids)[0]

        if not obj.contact_id.id:
            raise Exception("Customer not found")

        vals = {
            "contact_id": obj.contact_id.id,
            "due_date": obj.promised_date,
            "time_start": obj.promised_date,
            'priority': obj.priority,
            "related_id": "issue,%d" % obj.id,
            "project_id": obj.project_id.id,
            "service_type_id": obj.service_type_id.id,
            "lines": [],
        }

        new_id = get_model("job").create(vals)
        job = get_model("job").browse(new_id)

        service_item = obj.service_item_id
        if service_item:
            get_model("job.item").create({
                'job_id': new_id,
                'service_item_id': service_item.id,
                'description': obj.details or "",
            })

        return {
            "flash": "Service Order %s copied from issue %s" % (job.number, obj.name),
            "next": {
                "name": "job",
                "mode": "form",
                "active_id": new_id,
            }
        }

    def onchange_contact_id(self, context={}):
        data = context.get("data")
        import pprint
        pprint.pprint(data)
        return data


Issue.register()
