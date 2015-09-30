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
from netforce import utils
import random

class CMSForgotPass(BaseController):
    _path="/cms_forgot_passwd"

    def get(self):
        db=get_connection()
        try:
            ctx=self.context
            content=render("cms_forgot_passwd",ctx)
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
            email=self.get_argument("email",None)
            if not email:
                raise Exception("Missing email")
            if not utils.check_email_syntax(email):
                raise Exception("Wrong Email syntax")
            res=get_model("base.user").search([["login","=",email]])
            if not res:
                raise Exception("Email not found")
            forgot_id = get_model("cms.forgot.passwd").create({"email": email})
            forgot_obj = get_model("cms.forgot.passwd").browse(forgot_id)
            forgot_obj.trigger("forgot")
            ctx=self.context
            ctx["success"]=True
            ctx["message"]="Reset password request was sent to your email. Please follow the instruction in email.";
            content=render("cms_forgot_passwd",ctx)
            ctx["content"]=content
            html=render("cms_layout",ctx)
            self.write(html)
            db.commit()
        except Exception as e:
            try:
                ctx=self.context
                ctx["error"]=True
                ctx["message"]=str(e)
                ctx["email"]=email
                content=render("cms_forgot_passwd",ctx)
                ctx["content"]=content
                html=render("cms_layout",ctx)
                self.write(html)
                db.commit()
            except:
                import traceback
                traceback.print_exc()
                db.rollback()

CMSForgotPass.register()
