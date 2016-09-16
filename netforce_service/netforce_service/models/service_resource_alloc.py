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

from datetime import datetime
from netforce.model import Model, fields, get_model


class ResourceAlloc(Model):
    _name = "service.resource.alloc"
    _string = "Resource Allocation"
    _name_field="resource_id"

    def get_contact(self, ids, context={}):
        res = {}
        for obj in self.browse(ids):
            res[obj.id] = obj.job_id.contact_id.id
        return res

    def get_service_item(self, ids, context={}):
        res = {}
        for obj in self.browse(ids):
            items = obj.job_id.items
            if items:
                service_item_id = items[-1].id
                res[obj.id] = service_item_id
        return res

    _fields = {
        "resource_id": fields.Many2One("service.resource", "Resource", required=True, search=True, on_delete="cascade"),
        "job_id": fields.Many2One("job", "Service Order", required=True, search=True, on_delete="cascade"),
        "time_start": fields.DateTime("Planned Start Time", required=True),
        "time_stop": fields.DateTime("Planned Stop Time", required=True),
        "duration": fields.Integer("Duration (Days)"),
        "description": fields.Text("Description"),
        "contact_id": fields.Many2One("contact", "Customer", function="get_contact", store=True, search=True),
        "service_item_id": fields.Many2One("service.item", "Service Item", function="get_service_item"),
        "progress": fields.Integer("Progress (%)"),
        "depends": fields.One2Many("service.resource.alloc.depend","resource_alloc_id","Job Dependencies"),
        "depends_json": fields.Text("Job Dependencies (String)",function="get_depends_json"),
    }
    _order = "time_start,resource_id.name"

    def default_get(self,field_names=None,context={},**kw):
        defaults=context.get('defaults', {})
        data=context.get('data',{})
        vals={
            'time_start': data.get('time_start'),
            'time_stop': data.get('time_stop'),
            'job_id': defaults.get('job_id'),
        }
        vals=self.compute_duration(data=vals)
        return vals

    _constraints = ["check_overlap"]

    def check_overlap(self, ids, context={}):
        for obj in self.browse(ids):
            res = self.search([["id", "!=", obj.id], ["resource_id", "=", obj.resource_id.id],
                               ["time_start", "<", obj.time_stop], ["time_stop", ">", obj.time_start]])
            if res:
                alloc2 = self.browse(res[0])
                raise Exception("Invalid resource allocation for %s, %s overlaps with %s" %
                                (obj.resource_id.name, obj.job_id.number, alloc2.job_id.number))

    def get_depends_json(self,ids,context={}):
        vals={}
        for obj in self.browse(ids):
            res=[]
            for dep in obj.depends:
                res.append((dep.id,dep.prev_resource_alloc_id.id,dep.delay))
            vals[obj.id]=res
        return vals

    def compute_duration(self, data):
        t1=data['time_start']
        t2=data['time_stop']
        fmt="%Y-%m-%d %H:%M:%S"
        data['duration']=0
        if t1 and t2:
            d=datetime.strptime(t2,fmt)-datetime.strptime(t1, fmt)
            data['duration']=d.days
        return data

    def onchange_duration(self, context={}):
        data=context['data']
        data=self.compute_duration(data)
        return data

    def add_link(self,source_id,target_id,context={}):
        vals={
            "prev_resource_alloc_id": source_id,
            "resource_alloc_id": target_id,
        }
        get_model("service.resource.alloc.depend").create(vals)

    def delete(self, ids, context={}):
        depends_ids=[]
        for obj in self.browse(ids):
            for depend in obj.depends:
                depends_ids.append(depend.id)
        get_model("service.resource.alloc.depend").delete(depends_ids)
        super().delete(ids)

    def create(self, vals, context={}):
        new_id=super().create(vals,context)
        self.function_store([new_id])
        return new_id

    def write(self, ids, vals, **kw):
        super().write(ids,vals,**kw)
        self.function_store(ids)



ResourceAlloc.register()
