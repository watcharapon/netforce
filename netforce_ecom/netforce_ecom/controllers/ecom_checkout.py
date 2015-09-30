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
from netforce.model import get_model, fields
from netforce.database import get_connection, get_active_db  # XXX: move this
from netforce.locale import set_active_locale, get_active_locale
from netforce.access import get_active_user
from .cms_base import BaseController
from netforce import utils

class Checkout(BaseController):
    _path = "/ecom_checkout"

    def get(self):
        db = get_connection()
        try:
            ctx = self.context
            cart = ctx.get("cart")
            if not cart:
                db.commit()
                self.redirect("/cms_index")
                return
            fnames = [
                "email",
                "bill_first_name",
                "bill_last_name",
                "bill_company",
                "bill_address",
                "bill_address2",
                "bill_city",
                "bill_postal_code",
                "bill_country_id",
                "bill_province_id",
                "bill_district_id",
                "bill_subdistrict_id",
                "bill_phone",
                "ship_to_bill",
                "ship_first_name",
                "ship_last_name",
                "ship_company",
                "ship_address",
                "ship_address2",
                "ship_city",
                "ship_postal_code",
                "ship_country_id",
                "ship_province_id",
                "ship_district_id",
                "ship_subdistrict_id",
                "ship_phone",
            ]
            form_vals = {}
            for n in fnames:
                v = cart[n]
                f = get_model("ecom.cart")._fields[n]
                if v and isinstance(f, fields.Many2One):
                    v = v.id
                form_vals[n] = v
            ctx["form_vals"] = form_vals
            content = render("ecom_checkout", ctx)
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
            if self.get_argument("commit", None):
                cart_id = self.get_argument("cart_id")
                cart_id = int(cart_id)
                fnames = [
                    "email",
                    "bill_first_name",
                    "bill_last_name",
                    "bill_company",
                    "bill_address",
                    "bill_address2",
                    "bill_city",
                    "bill_postal_code",
                    "bill_country_id",
                    "bill_district_id",
                    "bill_subdistrict_id",
                    "bill_province_id",
                    "bill_phone",
                    "ship_to_bill",
                    "ship_first_name",
                    "ship_last_name",
                    "ship_company",
                    "ship_address",
                    "ship_address2",
                    "ship_city",
                    "ship_postal_code",
                    "ship_country_id",
                    "ship_province_id",
                    "ship_district_id",
                    "ship_subdistrict_id",
                    "ship_phone",
                ]
                form_vals = {}
                for n in fnames:
                    v = self.get_argument(n, None)
                    f = get_model("ecom.cart")._fields[n]
                    if isinstance(f, fields.Boolean):
                        v = v and True or False
                    elif isinstance(f, fields.Many2One):
                        v = int(v) if v else None
                    form_vals[n] = v
                print("FORM VALS", form_vals)
                field_errors = {}
                try:
                    req_fields = [
                        "email",
                        "bill_first_name",
                        "bill_last_name",
                        "bill_address",
                        "bill_postal_code",
                        "bill_country_id",
                        #"bill_city",
                        #"bill_province_id",
                        #"bill_district_id",
                        #"bill_subdistrict_id",
                        "bill_phone",
                    ]
                    if not form_vals.get("ship_to_bill"):
                        req_fields += [
                            "ship_first_name",
                            "ship_last_name",
                            "ship_address",
                            "ship_postal_code",
                            "ship_country_id",
                            #"ship_city",
                            #"ship_province_id",
                            #"ship_district_id",
                            #"ship_subdistrict_id",
                            "ship_phone",
                        ]
                    missing = []
                    for n in req_fields:
                        if not form_vals.get(n):
                            missing.append(n)
                            field_errors[n] = True
                    if missing:
                        print("missing",missing)
                        raise Exception("Some required fields are missing")
                    email = form_vals["email"]
                    user_id = get_active_user()
                    cart = get_model("ecom.cart").browse(cart_id)
                    if not utils.check_email_syntax(form_vals["email"]):
                        raise Exception("Invalid email syntax!!")
                    if user_id:
                        user = get_model("base.user").browse(user_id)
                        if email != user.email:
                            raise Exception("Email does not match logged in account email (%s)" % user.mail)
                    else:
                        res = get_model("base.user").search([["email", "=", email]])
                        if res:
                            raise Exception("An account already exists with that email, please login first")
                except Exception as e:
                    error_message = str(e)
                    ctx = self.context
                    ctx["form_vals"] = form_vals
                    ctx["error_message"] = error_message
                    if error_message.startswith("We apologize for the inconvenient"):
                        ctx["hide_checkout"] = "yes"
                    ctx["field_errors"] = field_errors
                    content = render("ecom_checkout", ctx)
                    ctx["content"] = content
                    html = render("cms_layout", ctx)
                    self.write(html)
                    return
                if form_vals.get("ship_to_bill"):
                    form_vals["ship_first_name"] = form_vals["bill_first_name"]
                    form_vals["ship_last_name"] = form_vals["bill_last_name"]
                    form_vals["ship_address"] = form_vals["bill_address"]
                    form_vals["ship_address2"] = form_vals["bill_address2"]
                    form_vals["ship_company"] = form_vals["bill_company"]
                    form_vals["ship_postal_code"] = form_vals["bill_postal_code"]
                    form_vals["ship_country_id"] = form_vals["bill_country_id"]
                    form_vals["ship_city"] = form_vals["bill_city"]
                    form_vals["ship_province_id"] = form_vals["bill_province_id"]
                    form_vals["ship_district_id"] = form_vals["bill_district_id"]
                    form_vals["ship_subdistrict_id"] = form_vals["bill_subdistrict_id"]
                    form_vals["ship_phone"] = form_vals["bill_phone"]
                get_model("ecom.cart").write([cart_id], form_vals)
                methods = get_model("ecom.cart").get_ship_methods([cart_id])
                if methods:
                    get_model("ecom.cart").write([cart_id], {"ship_method_id": methods[0]["method_id"]})
                self.redirect("/ecom_checkout2")
            db.commit()
        except:
            import traceback
            traceback.print_exc()
            db.rollback()

Checkout.register()
