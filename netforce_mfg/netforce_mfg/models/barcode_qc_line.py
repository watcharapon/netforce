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


class BarcodeQCLine(Model):
    _name = "barcode.qc.line"
    _transient = True
    _fields = {
        "barcode_id": fields.Many2One("barcode.qc", "Barcode", required=True, on_delete="cascade"),
        "test_id": fields.Many2One("qc.test", "QC Test", required=True),
        "sample_qty": fields.Decimal("Sampling Qty", scale=6),
        "value": fields.Char("Value"),
        "min_value": fields.Decimal("Min Value", function="_get_related", function_context={"path": "test_id.min_value"}),
        "max_value": fields.Decimal("Max Value", function="_get_related", function_context={"path": "test_id.max_value"}),
        "result": fields.Selection([["yes", "Yes"], ["no", "No"], ["na", "N/A"]], "Result", required=True),
        "prod_qc_id": fields.Many2One("production.qc", "Production QC"),
    }

BarcodeQCLine.register()
