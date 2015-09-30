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

from netforce.controller import Controller
from netforce.template import render
from netforce.model import get_model
from netforce.database import get_connection, get_active_db  # XXX: move this
from netforce.locale import set_active_locale, get_active_locale
from .cms_base import BaseController


class Addresses(BaseController):
    _path = "/ecom_addresses"

    def get(self):
        db = get_connection()
        try:
            ctx = self.context
            edit_form_vals = {}
            for addr in ctx["customer"].addresses:
                edit_form_vals[addr.id] = {
                    "first_name": addr.first_name,
                    "last_name": addr.last_name,
                    "company": addr.company,
                    "address": addr.address,
                    "address2": addr.address2,
                    "province": addr.province,
                    "province_id": addr.province_id.id,
                    "district_id": addr.district_id.id,
                    "subdistrict_id": addr.subdistrict_id.id,
                    "postal_code": addr.postal_code,
                    "country": addr.country_id.name,
                    "phone": addr.phone,
                }
            ctx["edit_form_vals"] = edit_form_vals
            content = render("ecom_addresses", ctx)
            ctx["content"] = content
            html = render("cms_layout", ctx)
            self.write(html)
            db.commit()
        except:
            import traceback
            traceback.print_exc()
            db.rollback()

    def post(self):
        db = get_connection()
        try:
            try:
                addr_id = self.get_argument("id", None)
                if addr_id:
                    addr_id = int(addr_id)
                method = self.get_argument("method", None)
                if method == "delete":
                    get_model("address").delete([addr_id])
                    return
                # fields=["first_name","last_name","company","address","address2","postal_code","province","district","subdistrict","country","phone"]
                fields = ["first_name", "last_name", "company", "address", "address2",
                          "postal_code", "city", "province", "district", "subdistrict", "country", "phone"]
                # req_fields=["first_name","last_name","address","postal_code","country","province","district","subdistrict"]
                req_fields = ["first_name", "last_name", "address", "postal_code", "country"]
                field_errors = {}
                form_vals = {}
                for n in fields:
                    v = self.get_argument(n, None)
                    form_vals[n] = v
                    if n in req_fields and not v:
                        field_errors[n] = True
                if field_errors:
                    raise Exception("Some required fields are missing")
                user_id = self.get_cookie("user_id")
                user_id = int(user_id)
                user = get_model("base.user").browse(user_id)
                if not user:
                    raise Exception("User not found")
                contact_id = user.contact_id.id
                res = get_model("country").search([["id", "=", form_vals["country"]]])
                if not res:
                    raise Exception("Invalid country")
                country_id = res[0]
                res=get_model("province").search([["id","=",form_vals["province"]]])
                if not res:
                    raise Exception("Invalid province")
                province_id=res[0]
                res=get_model("district").search([["id","=",form_vals["district"]]])
                if not res:
                    raise Exception("Invalid district")
                district_id=res[0]
                res=get_model("subdistrict").search([["id","=",form_vals["subdistrict"]]])
                if not res:
                    raise Exception("Invalid subdistrict")
                subdistrict_id=res[0]
                vals = {
                    "contact_id": contact_id,
                    "first_name": form_vals["first_name"],
                    "last_name": form_vals["last_name"],
                    "company": form_vals["company"],
                    "address": form_vals["address"],
                    "address2": form_vals["address2"],
                    "province_id": province_id,
                    "postal_code": form_vals["postal_code"],
                    "country_id": country_id,
                    "city": form_vals["city"],
                    "province_id": province_id,
                    "district_id": district_id,
                    "subdistrict_id": subdistrict_id,
                }
                if addr_id:
                    get_model("address").write([addr_id], vals)
                else:
                    get_model("address").create(vals)
                cart_id = self.get_cookie("cart_id")
                if cart_id:
                    cart_id = int(cart_id)
                    get_model("ecom.cart").set_default_address([cart_id])
                db.commit()
                self.redirect("/ecom_addresses")
            except Exception as e:
                ctx = self.context
                db = get_connection()
                error_message = str(e)
                edit_form_vals = {}
                for addr in ctx["customer"].addresses:
                    edit_form_vals[addr.id] = {
                        "first_name": addr.first_name,
                        "last_name": addr.last_name,
                        "company": addr.company,
                        "address": addr.address,
                        "address2": addr.address2,
                        "postal_code": addr.postal_code,
                        "province": addr.province,
                        "district": addr.district,
                        "subdistrict": addr.subdistrict,
                        "city": addr.city,
                        "country": addr.country_id.name,
                        "phone": addr.phone,
                    }
                ctx["edit_form_vals"] = edit_form_vals
                if addr_id:
                    edit_form_vals[addr_id] = form_vals
                    ctx["edit_error_message"] = {addr_id: error_message}
                    ctx["edit_field_errors"] = {addr_id: field_errors}
                    ctx["show_edit_address"] = {addr_id: True}
                else:
                    ctx["form_vals"] = form_vals
                    ctx["error_message"] = error_message
                    ctx["field_errors"] = field_errors
                    ctx["show_add_address"] = True
                content = render("ecom_addresses", ctx)
                ctx["content"] = content
                html = render("cms_layout", ctx)
                db.commit()
                self.write(html)
        except:
            import traceback
            traceback.print_exc()
            db.rollback()

Addresses.register()
