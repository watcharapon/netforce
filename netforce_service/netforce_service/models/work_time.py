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
from netforce.access import get_active_user
import datetime


class WorkTime(Model):
    _name = "work.time"
    _string = "Work Time"
    _key = ["project_id","resource_id","date"]
    _fields = {
        "resource_id": fields.Many2One("service.resource", "Resource", required=True, search=True, on_delete="cascade"),
        "resource_type": fields.Selection([["person","Person"],["machine","Machine"]],"Resource Type",function="_get_related",function_search="_search_related",function_context={"path":"resource_id.type"},search=True),
        "project_id": fields.Many2One("project", "Project", search=True),
        "related_id": fields.Reference([["job","Service Order"],["sale.order","Sales Order"],["rental.order","Rental Order"]],"Related To",search=True),
        "job_id": fields.Many2One("job", "Service Order", search=True), # XXX: deprecated
        "service_item_id": fields.Many2One("service.item","Service Item"), # XXX: deprecated
        "service_type_id": fields.Many2One("service.type", "Service Type", function="_get_related", function_context={"path": "job_id.service_type_id"}, function_search="_search_related", search=True),
        "date": fields.Date("Date", required=True, search=True),
        "actual_hours": fields.Decimal("Actual Hours", required=True),
        "bill_hours": fields.Decimal("Billable Hours"),
        "work_type_id": fields.Many2One("work.type", "Work Type"),
        "description": fields.Text("Description"),
        "week": fields.Date("Week", function="get_week", store=True),
        "comments": fields.One2Many("message", "related_id", "Comments"),
        "is_today": fields.Boolean("Today", store=False, function_search="search_today"),
        "is_this_week": fields.Boolean("This Week", store=False, function_search="search_this_week"),
        "is_last_week": fields.Boolean("Last Week", store=False, function_search="search_last_week"),
        "state": fields.Selection([["waiting_approval", "Waiting Approval"], ["approved", "Approved"], ["rejected", "Rejected"]], "Status", required=True),
        "agg_actual_hours_total": fields.Decimal("Actual Hours Total", agg_function=["sum", "actual_hours"]),
        "agg_bill_hours_total": fields.Decimal("Billable Hours Total", agg_function=["sum", "bill_hours"]),
        "track_entries": fields.One2Many("account.track.entry","related_id","Tracking Entries"),
        "track_id": fields.Many2One("account.track.categ","Tracking",function="get_track_categ"),
        "cost_amount": fields.Decimal("Cost Amount",function="get_cost_amount"),
        #"agg_cost_amount": fields.Decimal("Cost Amount", agg_function=["sum", "cost_amount"]),
        "sale_price": fields.Decimal("Hourly Rate"),
    }
    _order = "date,resource_id.name"

    def get_resource(self, context={}):
        user_id = get_active_user()
        res = get_model("service.resource").search([["user_id", "=", user_id]])
        if not res:
            return None
        return res[0]

    def get_default_project(self, context={}):
        defaults=context.get('defaults', {})
        data=context.get('data',{})
        return data.get('project_id')

    def get_default_related(self, context={}):
        defaults = context.get('defaults', {})
        data = context.get('data',{})
        job_number = data.get("number")
        job_id = None
        if job_number:
            for job_id in get_model("job").search([['number','=', job_number]]):
                data['job_id']=job_id
        return "job,%s"%(job_id) if job_id else None

    _defaults = {
        "date": lambda *a: time.strftime("%Y-%m-%d"),
        "resource_id": get_resource,
        "project_id": get_default_project,
        #"related_id": get_default_related,
        "state": "waiting_approval",
    }

    def name_get(self,ids,context={}):
        res=[]
        for obj in self.browse(ids):
            res.append((obj.id,"Work Time %s / %s"%(obj.resource_id.name,obj.date)))
        return res

    def create(self, vals, **kw):
        if 'related_id' in vals and 'job' in vals['related_id']:
            job_id = int(vals['related_id'].split(',')[1])
            vals['job_id'] = job_id
            #auto assign project
            if not 'project_id' in vals and job_id:
                for job in get_model("job").search_read([['id','=', job_id]],['project_id']):
                    if job['project_id']:
                        vals['project_id']=job['project_id'][0]
        new_id = super().create(vals, **kw)
        self.function_store([new_id])
        if 'job_id' in vals:
            get_model('job').function_store([vals['job_id']])
        return new_id

    def write(self, ids, vals, **kw):
        #auto assign project
        job_ids=[]
        for obj in self.browse(ids):
            if not obj.project_id:
                if obj.job_id and obj.job_id.project_id:
                    vals['project_id']=obj.job_id.project_id.id
                    job_ids.append(obj.job_id.id)
                elif obj.related_id and obj.related_id._model=='job':
                    vals['project_id']=obj.related_id.project_id.id
        super().write(ids, vals, **kw)
        self.function_store(ids)
        if job_ids:
            get_model('job').function_store(job_ids)

    def delete(self, ids, context={}):
        job_ids=[]
        for obj in self.browse(ids):
            if obj.job_id:
                job_ids.append(obj.job_id.id)
        super().delete(ids)
        get_model('job').function_store(job_ids)

    def get_week(self, ids, context={}):
        vals = {}
        for obj in self.browse(ids):
            d = datetime.datetime.strptime(obj.date, "%Y-%m-%d")
            d -= datetime.timedelta(d.weekday())
            vals[obj.id] = d.strftime("%Y-%m-%d")
        return vals

    def search_today(self, clause, context={}):
        t = time.strftime("%Y-%m-%d")
        return [["date", "=", t]]

    def search_this_week(self, clause, context={}):
        d = datetime.datetime.today()
        d0 = d - datetime.timedelta(days=d.weekday())
        d1 = d0 + datetime.timedelta(days=6)
        return [["date", ">=", d0.strftime("%Y-%m-%d")], ["date", "<=", d1.strftime("%Y-%m-%d")]]

    def search_last_week(self, clause, context={}):
        d = datetime.datetime.today()
        d0 = d - datetime.timedelta(days=d.weekday() + 7)
        d1 = d0 + datetime.timedelta(days=6)
        return [["date", ">=", d0.strftime("%Y-%m-%d")], ["date", "<=", d1.strftime("%Y-%m-%d")]]

    def approve(self, ids, context={}):
        res=get_model("uom").search([["name","=","Hour"]])
        if not res:
            raise Exception("Hour UoM not found")
        hour_uom_id=res[0]
        for obj in self.browse(ids):
            obj.write({"state": "approved"})
            if obj.track_id and obj.cost_amount:
                vals={
                    "track_id": obj.track_id.id,
                    "date": obj.date,
                    "amount": -obj.cost_amount,
                    "product_id": obj.resource_id.product_id.id,
                    "qty": obj.actual_hours or 0,
                    "uom_id": hour_uom_id,
                    "related_id": "work.time,%s"%obj.id,
                }
                get_model("account.track.entry").create(vals)

    def reject(self, ids, context={}):
        for obj in self.browse(ids):
            obj.write({"state": "rejected"})

    def waiting_approval(self, ids, context={}):
        for obj in self.browse(ids):
            obj.write({"state": "waiting_approval"})
            obj.track_entries.delete()

    def onchange_product(self, context={}):
        data = context["data"]
        prod_id = data["product_id"]
        prod = get_model("product").browse(prod_id)
        data["unit_price"] = prod.cost_price
        return data

    def get_track_categ(self,ids,context={}):
        vals={}
        for obj in self.browse(ids):
            track_id=None
            project_id=obj.project_id
            if project_id and project_id.track_id:
                track_id=project_id.track_id.id
            rel=obj.related_id
            if rel.track_id:
                track_id=rel.track_id.id
            vals[obj.id]=track_id
        return vals

    def get_cost_amount(self,ids,context={}):
        vals={}
        for obj in self.browse(ids):
            # Use standard price in product in resource
            prod=obj.resource_id.product_id
            amt=(prod.cost_price or 0)*(obj.actual_hours or 0)
            vals[obj.id]=amt
        return vals

    def copy_to_invoice_group(self,ids,context={}):
        inv_vals = {
            "type": "out",
            "inv_type": "invoice",
            "lines": [],
        }
        res_hours={}
        for obj in self.browse(ids):
            if obj.invoice_id:
                raise Exception("Invoice already created for work time %s"%obj.id)
            project=obj.project_id
            contact_id=project.contact_id.id
            if not contact_id and obj.related_id._model=="rental.order": # XXX
                contact_id=obj.related_id.contact_id.id
            if not contact_id:
                raise Exception("Contact not found for worktime %s"%obj.id)
            if inv_vals.get("contact_id"):
                if contact_id!=inv_vals["contact_id"]:
                    raise Exception("Different contacts")
            else:
                inv_vals["contact_id"]=contact_id
            if obj.related_id:
                related_id="%s,%d"%(obj.related_id._model,obj.related_id.id)
            else:
                related_id=None
            if inv_vals.get("related_id"):
                if related_id!=inv_vals["related_id"]:
                    raise Exception("Different related documents")
            else:
                inv_vals["related_id"]=related_id
            if obj.related_id._model=="rental.order": # XXX
                currency_id=obj.related_id.currency_id.id
            else:
                currency_id=None
            if currency_id:
                if inv_vals.get("currency_id"):
                    if currency_id!=inv_vals["currency_id"]:
                        raise Exception("Different currencies")
                else:
                    inv_vals["currency_id"]=currency_id
            resource=obj.resource_id
            k=(resource.id,obj.sale_price or 0)
            res_hours.setdefault(k,0)
            res_hours[k]+=obj.bill_hours or 0
        for (resource_id,sale_price),bill_hours in res_hours.items():
            if not bill_hours:
                continue
            resource=get_model("service.resource").browse(resource_id)
            prod=resource.product_id
            if not prod:
                raise Exception("Missing product for resource %s"%resource.name)
            sale_acc_id=prod.sale_account_id.id
            if not sale_acc_id and prod.categ_id:
                sale_acc_id=prod.categ_id.sale_account_id.id
            if not sale_acc_id:
                raise Exception("Missing sales account in product %s"%prod.code)
            line_vals = {
                "product_id": prod.id,
                "description": resource.name,
                "qty": bill_hours or 0,
                "uom_id": prod.uom_id.id,
                "unit_price": sale_price,
                "account_id": sale_acc_id,
                "tax_id": prod.sale_tax_id.id if prod else None,
                "amount": (bill_hours or 0)*(sale_price or 0),
            }
            inv_vals["lines"].append(("create", line_vals))
        if not inv_vals["lines"]:
            raise Exception("Nothing to invoice")
        inv_id = get_model("account.invoice").create(inv_vals, {"type": "out", "inv_type": "invoice"})
        self.write(ids,{"invoice_id": inv_id})
        inv = get_model("account.invoice").browse(inv_id)
        return {
            "next": {
                "name": "view_invoice",
                "active_id": inv_id,
            },
            "flash": "Invoice %s created from work time" % inv.number,
        }

WorkTime.register()
