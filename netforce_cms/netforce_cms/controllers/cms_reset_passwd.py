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
from .cms_base import BaseController
import random

class CMSResetPasswd(BaseController):
    _path="/cms_reset_passwd"

    def get(self):
        db=get_connection()
        try:
            ctx=self.context
            key=self.get_argument("key",None)
            if not key:
                raise Exception("Invaid Key")
            if not get_model("cms.forgot.passwd").search([["key","=",key]]):
                raise Exception("Invalid Key")
            ctx["key"] = key
            content=render("cms_reset_passwd",ctx)
            ctx["content"]=content
            html=render("cms_layout",ctx)
            self.write(html)
            db.commit()
        except:
            self.redirect("cms_page_not_found")
            import traceback
            traceback.print_exc()
            db.rollback()

    def post(self):
        db=get_connection()
        try:
            key=self.get_argument("key",None)
            if not key:
                raise Exception("Invalid key")
            new_password = self.get_argument("new_password",None)
            re_password = self.get_argument("re_password",None)
            if len(new_password)<6:
                raise Exception("New password must be more than 6 character")
            if new_password != re_password:
                raise Exception("New password does not match confirmed password")
            res = get_model("cms.forgot.passwd").search([["key","=",key]])
            if not res:
                raise Exception("Can not find email that match the key")
            forgot_obj = get_model("cms.forgot.passwd").browse(res[0])
            res = get_model("base.user").search([["login","=",forgot_obj.email]])
            if not res:
                raise Exception("Can not find user")
            user = get_model("base.user").browse(res[0])
            user.write({"password": new_password})
            user.trigger("change_password", context={"new_password": new_password})

            for obj in get_model("cms.forgot.passwd").search_browse([["email","=",forgot_obj.email]]):
                obj.delete()
            db.commit()

            self.redirect("cms_login?message=Your%20password%20has%20been%20reset")
        except Exception as e:
            try:
                ctx=self.context
                ctx["error"]=True
                ctx["message"]=str(e)
                ctx["key"] = key
                content=render("cms_reset_passwd",ctx)
                ctx["content"]=content
                html=render("cms_layout",ctx)
                self.write(html)
                db.commit()
            except:
                import traceback
                traceback.print_exc()
                db.rollback()

CMSResetPasswd.register()
