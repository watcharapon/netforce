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


class Model(Model):
    _name = "model"
    _string = "Model"
    _name_field = "string"
    _key = ["name"]
    _fields = {
        "name": fields.Char("Name", required=True, search=True),
        "string": fields.Char("String", required=True, search=True),
        "fields": fields.One2Many("field", "model_id", "Fields"),
        "code": fields.Text("Code"),
        "order": fields.Char("Order"),
        "description": fields.Text("Description"),
        "offline": fields.Boolean("Offline"),
        "module_id": fields.Many2One("module", "Module"),
    }
    _order = "name"

    def name_search_multi(self, name, models, condition=[], limit=None, context={}):
        for model in models:
            m = get_model(model)
            res = m.name_search(name, condition=condition, limit=limit, context=context)
            if res:
                return {
                    "model": model,
                    "values": res,
                }
        return {
            "model": None,
            "values": [],
        }

Model.register()
