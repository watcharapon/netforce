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
from netforce.utils import get_data_path
from datetime import *


class ContractTemplate(Model):
    _name = "service.contract.template"
    _string = "Service Contract Template"
    _name_field = "name"
    _fields = {
        "name": fields.Char("Template Name", required=True, search=True),
        "description": fields.Text("Description"),
        "comments": fields.One2Many("message", "related_id", "Comments"),
        "jobs": fields.One2Many("service.contract.template.job", "template_id", "Service Orders"),
        "amount_labor": fields.Decimal("Labor Amount", function="get_total", function_multi=True),
        "amount_part": fields.Decimal("Parts Amount", function="get_total", function_multi=True),
        "amount_other": fields.Decimal("Other Amount", function="get_total", function_multi=True),
        "amount_total": fields.Decimal("Total Amount", function="get_total", function_multi=True),
    }
    _order = "name"

    def create_jobs(self, ids, contract_line_id=None):
        obj = self.browse(ids)[0]
        contract_line = get_model("service.contract.line").browse(contract_line_id)
        contract = contract_line.contract_id
        if not contract.end_date:
            raise Exception("Missing end date in contract %s" % contract.number)
        item = contract_line.service_item_id
        d0 = datetime.strptime(contract.start_date, "%Y-%m-%d")
        for job in obj.jobs:
            if not item.est_counter_per_year:
                raise Exception("Missing counter per year for service item %s" % item.number)
            d = (d0 + timedelta(days=job.counter * 365.0 / item.est_counter_per_year)).strftime("%Y-%m-%d")
            if d <= contract.end_date:
                tmpl = job.job_template_id
                tmpl.create_job(contract_line_id=contract_line_id, date=d, description=job.description)

    def get_total(self, ids, context={}):
        vals = {}
        for obj in self.browse(ids):
            amt_labor = sum([l.amount_labor or 0 for l in obj.jobs])
            amt_part = sum([l.amount_part or 0 for l in obj.jobs])
            amt_other = sum([l.amount_other or 0 for l in obj.jobs])
            amt_total = amt_labor + amt_part + amt_other
            vals[obj.id] = {
                "amount_labor": amt_labor,
                "amount_part": amt_part,
                "amount_other": amt_other,
                "amount_total": amt_total,
            }
        return vals

    def copy(self, ids, context={}):
        obj = self.browse(ids)[0]
        vals = {
            "name": obj.name + " (copy)",
            "description": obj.description,
            "jobs": [],
        }
        for job in obj.jobs:
            job_vals = {
                "sequence": job.sequence,
                "counter": job.counter,
                "job_template_id": job.job_template_id.id,
                "description": job.description,
            }
            vals["jobs"].append(("create", job_vals))
        new_id = self.create(vals)
        return {
            "next": {
                "name": "service_contract_template",
                "mode": "form",
                "active_id": new_id,
            },
            "flash": "Service contract template copied",
        }

ContractTemplate.register()
