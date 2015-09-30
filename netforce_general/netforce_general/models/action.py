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

from netforce.model import Model, fields
import json


class Action(Model):
    _name = "action"
    _string = "Action"
    _key = ["name"]
    _fields = {
        "name": fields.Char("Name", required=True),
        "string": fields.Char("String"),
        "view": fields.Selection([["multi_view", "Multi"], ["board", "Dashboard"], ["list_view", "List"], ["form_view", "Form"], ["page", "Page"], ["calendar", "Calendar"], ["gantt", "Gantt"]], "View"),
        "view_layout_id": fields.Many2One("view.layout", "View Layout"),
        "model_id": fields.Many2One("model", "Model"),
        "menu_id": fields.Many2One("view.layout", "Menu", condition=[["type", "=", "menu"]]),
        "options": fields.Text("Options"),
        "module_id": fields.Many2One("module", "Module"),
    }
    _order = "name"

    def name_get(self, ids, context={}):
        vals = []
        for obj in self.browse(ids):
            if obj.string:
                name = "[%s] %s" % (obj.name, obj.string)
            else:
                name = "[%s]" % obj.name
            vals.append((obj.id, name))
        return vals

    def actions_to_json(self):
        data = {}
        for obj in self.search_browse([]):
            vals = {
                "name": obj.name,
            }
            if obj.string:
                vals["string"] = obj.string
            if obj.view:
                vals["view_cls"] = obj.view
            if obj.menu_id:
                vals["menu"] = obj.menu_id.name
            if obj.view_layout_id:
                vals["view_xml"] = obj.view_layout_id.name
            if obj.model_id:
                vals["model"] = obj.model_id.name
            if obj.options:
                try:
                    opts = json.loads(obj.options)
                    vals.update(opts)
                except Exception as e:
                    raise Exception("Failed to parse options of action '%s': %s" % (obj.name, e))
            data[obj.name] = vals
        return data

Action.register()
