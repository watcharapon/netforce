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
from netforce.database import get_connection,get_active_db # XXX: move this
from netforce.locale import set_active_locale,get_active_locale
from netforce.utils import new_token
from .cms_base import BaseController
from netforce import utils
from netforce.access import set_active_user

class Register(BaseController):
    _path="/register"

    def get(self):
        db=get_connection()
        try:
            ctx=self.context
            content=render("cms_register",ctx)
            ctx["content"]=content
            html=render("cms_layout",ctx)
            self.write(html)
            db.commit()
        except:
            import traceback
            traceback.print_exc()
            db.rollback()

    def post(self):
        db=get_connection()
        try:
            try:
                cart_id=self.get_argument("cart_id",None)
                fields=["first_name","last_name","email","password","re_password"]
                form_vals={}
                if cart_id:
                    cart_id=int(cart_id)
                    cart=get_model("ecom.cart").browse(cart_id)
                    password=self.get_argument("password",None)
                    form_vals={
                        "first_name": cart.bill_first_name,
                        "last_name": cart.bill_last_name,
                        "email": cart.email,
                        "password": password,
                        "re_password": password,
                    }
                else:
                    cart_id=self.get_cookie("cart_id") #In case of have a cart and register with register form
                    for n in fields:
                        form_vals[n]=self.get_argument(n,None)
                field_errors={}
                for n in fields:
                    if not form_vals.get(n):
                        field_errors[n]=True
                if field_errors:
                    raise Exception("Some required fields are missing")
                website=self.context["website"]
                if not website.user_profile_id.id:
                    raise Exception("Missing user profile in website settings")
                res=get_model("base.user").search([["login","=",form_vals["email"]]])
                if res:
                    raise Exception("An account with this email already exists")
                if len(form_vals["password"])<6:
                    raise Exception("Password is too short (Minimum 6 Characters)")
                if form_vals["password"] != form_vals["re_password"]:
                    raise Exception("Password and Re-Type Password does not match!")
                vals={
                    "name": form_vals["first_name"]+" "+form_vals["last_name"],
                    "login": form_vals["email"],
                    "password": form_vals["password"],
                    "email": form_vals["email"],
                    "profile_id": website.user_profile_id.id,
                }
                user_id=get_model("base.user").create(vals)
                get_model("base.user").trigger([user_id],"create_user",context={"password": form_vals["password"]})
                if not website.contact_categ_id.id:
                    raise Exception("Missing contact category in website settings")
                if not utils.check_email_syntax(form_vals["email"]):
                    raise Exception("Invalid email syntax!!")
                res=get_model("contact").search([["email","=",form_vals["email"]],["categ_id","=",website.contact_categ_id.id]])
                if res:
                    contact_id=res[0]
                else:
                    vals={
                        "type": "person",
                        "first_name": form_vals["first_name"],
                        "last_name": form_vals["last_name"],
                        "email": form_vals["email"],
                        "categ_id": website.contact_categ_id.id,
                        "account_receivable_id": website.account_receivable_id.id,
                        "customer" : True,
                    }
                    contact_id=get_model("contact").create(vals)
                get_model("contact").trigger([contact_id],"ecom_register")
                get_model("contact").write([contact_id],{"user_id":user_id})
                get_model("base.user").write([user_id],{"contact_id":contact_id})
                tmpl=website.create_account_email_tmpl_id
                if tmpl:
                    data={
                        "email": form_vals["email"],
                        "first_name": form_vals["first_name"],
                        "last_name": form_vals["last_name"],
                        "new_password": form_vals["password"],
                    }
                    tmpl.create_email(data)
                dbname=get_active_db()
                token=new_token(dbname,user_id)
                print("commit")
                db.commit()
                self.set_cookie("user_id",str(user_id))
                self.set_cookie("token",token)
                print("redirect")
                if cart_id:
                    if user_id:
                        set_active_user(user_id)
                    cart_id=int(cart_id)
                    get_model("ecom.cart").set_default_address([cart_id])
                self.next_page()
            except Exception as e:
                db=get_connection()
                error_message=str(e)
                ctx=self.context
                ctx["form_vals"]=form_vals
                ctx["error_message"]=error_message
                ctx["field_errors"]=field_errors
                content=render("cms_register",ctx)
                ctx["content"]=content
                html=render("cms_layout",ctx)
                self.write(html)
                print("commit")
                db.commit()
        except:
            import traceback
            traceback.print_exc()
            print("rollback")
            db.rollback()

    def next_page(self):
        self.redirect("/register")

Register.register()
