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
from netforce.database import get_connection # XXX: move this
from netforce.access import get_active_user
from .cms_base import BaseController

class ChangePass(BaseController):
    _path="/cms_change_pass"

    def get(self):
        db=get_connection()
        try:
            user_id=self.get_cookie("user_id",None)
            if not user_id:
                self.redirect("/cms_login")
            ctx=self.context
            content=render("cms_change_pass",ctx)
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
                fields=["old_password","new_password","re_password"]
                field_errors={}
                form_vals={}
                for n in fields:
                    v=self.get_argument(n,None)
                    form_vals[n]=v
                    if not v:
                        field_errors[n]=True
                if field_errors:
                    raise Exception("Some required fields are missing")
                user_id=get_active_user()
                if not user_id:
                    raise Exception("No user")
                user=get_model("base.user").browse(user_id)
                user_id=get_model("base.user").check_password(user.email,form_vals["old_password"])
                if not user_id:
                    raise Exception("Wrong password") 
                if len(form_vals["new_password"])<6:
                    raise Exception("New password must be more than 6 character")
                if form_vals["new_password"]!=form_vals["re_password"]:
                    raise Exception("New password does not match confirmed password")
                get_model("base.user").write([user_id],{"password":form_vals["new_password"]})
                get_model("base.user").trigger([user_id],"change_password",context={"new_password": form_vals["new_password"]})
                self.redirect("/cms_account?message=Your%20password%20has%20been%20changed")
                db.commit()
            except Exception as e:
                db=get_connection()
                error_message=str(e)
                ctx=self.context
                ctx["form_vals"]=form_vals
                ctx["error_message"]=error_message
                ctx["field_errors"]=field_errors
                content=render("cms_change_pass",ctx)
                ctx["content"]=content
                html=render("cms_layout",ctx)
                self.write(html)
                db.commit()
        except:
            import traceback
            traceback.print_exc()
            db.rollback()

ChangePass.register()
