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


class ViewLayout(Model):
    _name = "view.layout"
    _string = "View Layout"
    _key = ["name"]
    _fields = {
        "name": fields.Char("Name", required=True, search=True),
        "inherit": fields.Char("Inherit", search=True),
        "model_id": fields.Many2One("model", "Model", search=True),
        "type": fields.Selection([["list", "List"], ["form", "Form"], ["menu", "Menu"], ["board", "Dashboard"], ["page", "Page"], ["grid", "Grid"], ["calendar", "Calendar"], ["gantt", "Gantt"], ["inherit", "Inherit"]], "Type", search=True),
        "layout": fields.Text("Layout"),
        "module_id": fields.Many2One("module", "Module"),
    }
    _order = "name"

    def layouts_to_json(self):
        data = {}
        for obj in self.search_browse([]):
            vals = {
                "name": obj.name,
                "type": obj.type,
                "layout": obj.layout,
            }
            if obj.model_id:
                vals["model"] = obj.model_id.name
            if obj.inherit:
                vals["inherit"] = obj.inherit
            data[obj.name] = vals
        return data

ViewLayout.register()
