from netforce.model import Model,fields,get_model
from netforce import access
from datetime import *
import time

class Issue(Model):
    _name="issue"
    _string="Issue"
    _name_field="number"
    _fields={
        "number": fields.Char("Number",required=True,search=True),
        "date_created": fields.DateTime("Date Created",required=True,search=True),
        "date_closed": fields.DateTime("Date Closed"),
        "date_estimate": fields.DateTime("Estimated Close Date"),
        "contact_id": fields.Many2One("contact","Customer",required=True,search=True),
        "project_id": fields.Many2One("project","Project",required=True,search=True),
        "title": fields.Char("Title",required=True,search=True),
        "description": fields.Text("Description",search=True),
        "priority": fields.Decimal("Priority",required=True),
        "emails": fields.One2Many("email.message", "related_id", "Emails"),
        "state": fields.Selection([["new","New"],["ready","Ready To Start"],["in_progress","In Progress"],["closed","Closed"],["wait_customer","Wait For Customer"],["wait_internal","Internal Wait"]],"Status",required=True,search=True),
        "planned_hours": fields.Decimal("Planned Hours"),
        "days_open": fields.Integer("Days Open",function="get_days_open"),
        "resource_id": fields.Many2One("service.resource","Assigned To"),
        "documents": fields.One2Many("document", "related_id", "Documents"),
        "emails": fields.One2Many("email.message", "related_id", "Emails"),
        "comments": fields.Text("Comments"),
        "type_id": fields.Many2One("issue.type","Issue Type",required=True),
        "messages": fields.One2Many("message", "related_id", "Messages"),
    }
    _order="priority,id"

    def _get_number(self, context={}):
        seq_id = get_model("sequence").find_sequence(type="issue")
        if not seq_id:
            return None
        while 1:
            num = get_model("sequence").get_next_number(seq_id)
            user_id = access.get_active_user()
            access.set_active_user(1)
            res = self.search([["number", "=", num]])
            access.set_active_user(user_id)
            if not res:
                return num
            get_model("sequence").increment_number(seq_id)

    _defaults={
        "date_created": lambda *a: time.strftime("%Y-%m-%d %H:%M:%S"),
        "state": "new",
        "number": _get_number,
    }

    def get_days_open(self,ids,context={}):
        vals={}
        today=date.today()
        for obj in self.browse(ids):
            if obj.state=="closed":
                vals[obj.id]=None
                continue
            d=datetime.strptime(obj.date_created,"%Y-%m-%d %H:%M:%S").date()
            vals[obj.id]=(today-d).days
        return vals

Issue.register()
