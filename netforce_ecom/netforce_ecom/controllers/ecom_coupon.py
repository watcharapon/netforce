# Copyright (c) 2015, Netforce Co., Ltd.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from netforce.controller import Controller
from netforce.template import render
from netforce.model import get_model
from netforce.database import get_connection,get_active_db # XXX: move this
from netforce.locale import set_active_locale,get_active_locale
from .cms_base import BaseController

class Coupon(BaseController):
    _path="/ecom_coupon"

    def get(self):
        db=get_connection()
        try:
            ctx=self.context
            user_id = self.get_cookie("user_id")
            if not user_id:
                raise Exception("Can't access coupon page without login")
            user_id = int(user_id)
            user = get_model("base.user").browse(user_id)
            coupon_id=int(self.get_argument("coupon_id"))
            coupon=get_model("sale.coupon").browse(coupon_id)
            #if user.contact_id.id != coupon.contact_id.id:
                #raise Exception("Can't access coupon of other users")
            ctx["coupon"]=coupon
            content=render("ecom_coupon",ctx)
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
            ctx=self.context
            coupon_id=int(self.get_argument("coupon_id"))
            action=self.get_argument("action")
            try:
                if action=="use_coupon":
                    coupon=get_model("sale.coupon").browse(coupon_id)
                    coupon.use_coupon()
                    db.commit()
                    self.redirect("/ecom_coupon?coupon_id=%s"%coupon.id)
            except Exception as e:
                ctx["error_message"]=str(e)
                coupon=get_model("sale.coupon").browse(coupon_id)
                ctx["coupon"]=coupon
                content=render("ecom_coupon",ctx)
                ctx["content"]=content
                html=render("cms_layout",ctx)
                self.write(html)
                db.commit()
        except:
            import traceback
            traceback.print_exc()
            db.rollback()

Coupon.register()
