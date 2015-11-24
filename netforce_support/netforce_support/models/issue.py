from netforce.model import Model,fields,get_model
from netforce import access
from datetime import *
import time
import json

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
        "state": fields.Selection([["new","New"],["ready","Ready To Start"],["in_progress","In Progress"],["test_internal","Internal Testing"],["test_customer","Customer Testing"],["closed","Closed"],["wait_customer","Wait For Customer"],["wait_internal","Internal Wait"]],"Status",required=True,search=True),
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

    def get_email_addresses(self,ids,context={}):
        emails=[]
        for obj in self.browse(ids):
            project=obj.project_id
            contact=project.contact_id
            if contact.email:
                emails.append(contact.email)
            for resource in project.resources:
                user=resource.user_id
                if user:
                    emails.append(user.email)
        return emails

    def create(self,vals,*args,**kw):
        new_id=super().create(vals,*args,**kw)
        obj=self.browse(new_id)
        project=obj.project_id
        contact=project.contact_id
        emails=obj.get_email_addresses()
        user_id=access.get_active_user()
        user=get_model("base.user").browse(user_id)
        if emails:
            body=obj.description
            vals={
                "from_addr": "support@netforce.com", # XXX
                "to_addrs": ",".join(emails),
                "subject": "New issue %s by %s: %s (Pri %s)"%(obj.number,user.name,obj.title,obj.priority),
                "body": body,
                "state": "to_send",
                "name_id": "contact,%s"%contact.id,
                "related_id": "issue,%s"%obj.id,
            }
            get_model("email.message").create(vals)
        return new_id

    def write(self,ids,vals,*args,**kw):
        super().write(ids,vals,*args,**kw)
        user_id=access.get_active_user()
        user=get_model("base.user").browse(user_id)
        for obj in self.browse(ids):
            project=obj.project_id
            contact=project.contact_id
            emails=obj.get_email_addresses()
            if emails:
                body=json.dumps(vals)
                vals={
                    "from_addr": "support@netforce.com", # XXX
                    "to_addrs": ",".join(emails),
                    "subject": "Issue %s modified by %s: %s (Pri %s)"%(obj.number,user.name,obj.title,obj.priority),
                    "body": body,
                    "state": "to_send",
                    "name_id": "contact,%s"%contact.id,
                    "related_id": "issue,%s"%obj.id,
                }
                get_model("email.message").create(vals)

Issue.register()
