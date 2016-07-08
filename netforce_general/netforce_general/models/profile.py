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


class Profile(Model):
    _name = "profile"
    _string = "Profile"
    _key = ["name"]
    _fields = {
        "name": fields.Char("Name", required=True, search=True),
        "code": fields.Char("Short Code"),
        "perms": fields.One2Many("profile.access", "profile_id", "Model Permissions"),
        "field_perms": fields.One2Many("field.access", "profile_id", "Field Permissions"),
        "menu_perms": fields.One2Many("menu.access", "profile_id", "Menu Permissions"),
        "other_perms": fields.Many2Many("permission", "Other Permissions"),
        "home_action": fields.Char("Login Action"),
        "login_company_id": fields.Many2One("company", "Login Company"),
        "prevent_login": fields.Boolean("Prevent Login"),
        "comments": fields.One2Many("message", "related_id", "Comments"),
        "default_model_perms": fields.Selection([["full", "Full Access"], ["readonly","Read-only Access"], ["no", "No Access"]], "Default Model Permissions"),
        "default_menu_access": fields.Selection([["visible", "Visible"], ["hidden", "Hidden"]], "Default Menu Access"),
    }
    _order = "name"
    _defaults = {
        "default_model_perms": "full",
    }

    def get_data(self, context={}):
        vals = {}
        perms = []
        for m in get_model("model").search_browse([]):
            perms.append({
                "model_id": [m.id, m.string],
            })
        vals["perms"] = perms
        return vals

    def copy(self, ids, context={}):
        obj = self.browse(ids)[0]
        vals = {
            "name": obj.name + " (Copy)",
            "perms": [],
            "other_perms": [("set", [p.id for p in obj.other_perms])],
            "home_action": obj.home_action,
        }
        for perm in obj.perms:
            vals["perms"].append(("create", {
                "model_id": perm.model_id.id,
                "perm_read": perm.perm_read,
                "perm_create": perm.perm_create,
                "perm_write": perm.perm_write,
                "perm_delete": perm.perm_delete,
                "view_all": perm.view_all,
                "modif_all": perm.modif_all,
            }))
        profile_id = get_model("profile").create(vals)
        return {
            "next": {
                "name": "profile",
                "mode": "form",
                "active_id": profile_id,
            },
            "flash": "New profile created",
        }

Profile.register()
