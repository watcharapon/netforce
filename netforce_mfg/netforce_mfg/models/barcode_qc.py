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
from netforce.utils import get_data_path


class BarcodeQC(Model):
    _name = "barcode.qc"
    _transient = True
    _fields = {
        "production_id": fields.Many2One("production.order", "Production Order"),
        "test_id": fields.Many2One("qc.test", "QC Test"),
        "sample_qty": fields.Decimal("Sampling Qty", scale=6),
        "min_value": fields.Decimal("Min Value", function="_get_related", function_context={"path": "test_id.min_value"}),
        "max_value": fields.Decimal("Max Value", function="_get_related", function_context={"path": "test_id.max_value"}),
        "value": fields.Char("Value"),
        "result": fields.Selection([["yes", "Pass"], ["no", "Not Pass"], ["na", "N/A"]], "Result"),
        "lines": fields.One2Many("barcode.qc.line", "barcode_id", "Lines"),
    }

    def fill_qc_tests(self, ids, context={}):
        obj = self.browse(ids)[0]
        prod_order = obj.production_id
        if not prod_order:
            raise Exception("Please select production order")
        for qc_test in prod_order.qc_tests:
            vals = {
                "barcode_id": obj.id,
                "test_id": qc_test.test_id.id,
                "sample_qty": qc_test.sample_qty,
                "value": qc_test.value,
                "min_value": qc_test.min_value,
                "max_value": qc_test.max_value,
                "result": qc_test.result,
                "prod_qc_id": qc_test.id
            }
            get_model("barcode.qc.line").create(vals)

    def validate(self, ids, context={}):
        obj = self.browse(ids)[0]
        prod_order = obj.production_id
        if not prod_order:
            raise Exception("Plesae select production order")
        prod_order.write({"qc_tests": [("delete_all",)]})
        for line in obj.lines:
            vals = {
                "order_id": prod_order.id,
                "test_id": line.test_id.id,
                "sample_qty": line.sample_qty,
                "value": line.value,
                "min_value": line.min_value,
                "max_value": line.max_value,
                "result": line.result,
            }
            get_model("production.qc").create(vals)
        obj.write({
            "production_id": None,
            "test_id": None,
            "sample_qty": None,
            "value": None,
            "result": None,
            "lines": [("delete_all",)],
        })
        return {
            "flash": "QC result recorded successfully for production order %s" % obj.production_id.number,
            "focus_field": "production_id",
        }

    def onchange_qc_value(self, context={}):
        data = context["data"]
        path = context["path"]
        line = get_data_path(data, path, parent=True)
        try:
            value = float(line.get("value"))
        except:
            return
        min_value = line.get("min_value")
        max_value = line.get("max_value")
        if min_value and value < min_value:
            line["result"] = "no"
        elif max_value and value > max_value:
            line["result"] = "no"
        else:
            line["result"] = "yes"
        return data

    def onchange_qc_test(self, context={}):
        data = context["data"]
        path = context["path"]
        line = get_data_path(data, path, parent=True)
        test_id = line.get("test_id")
        if not test_id:
            return
        test = get_model("qc.test").browse(test_id)
        line["min_value"] = test.min_value
        line["max_value"] = test.max_value
        self.onchange_qc_value(context)
        return data

BarcodeQC.register()
