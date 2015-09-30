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
import datetime
from netforce.utils import get_data_path


class ContractTemplateJob(Model):
    _name = "service.contract.template.job"
    _name_field = "name"
    _fields = {
        "template_id": fields.Many2One("service.contract.template", "Template", required=True, on_delete="cascade"),
        "sequence": fields.Integer("Sequence"),
        "counter": fields.Integer("Service Item Counter"),
        "job_template_id": fields.Many2One("job.template", "Service Order Template"),
        "description": fields.Text("Description"),
        "amount_total": fields.Decimal("Total Amount", function="_get_related", function_context={"path": "job_template_id.amount_total"}),
        "amount_labor": fields.Decimal("Labor Amount", function="_get_related", function_context={"path": "job_template_id.amount_labor"}),
        "amount_part": fields.Decimal("Parts Amount", function="_get_related", function_context={"path": "job_template_id.amount_part"}),
        "amount_other": fields.Decimal("Other Amount", function="_get_related", function_context={"path": "job_template_id.amount_other"}),
    }
    _order = "sequence"

ContractTemplateJob.register()
