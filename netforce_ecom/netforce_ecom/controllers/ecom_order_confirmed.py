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
import requests
import urllib.parse
import time
from lxml import etree
from .cms_base import BaseController
from netforce.access import get_active_company, get_active_user, set_active_user, set_active_company


class OrderConfirmed(BaseController):
    _path = "/ecom_order_confirmed"

    def get(self):
        db = get_connection()
        try:
            cart_id = int(self.get_argument("cart_id"))
            print("cart_id", cart_id)
            cart = get_model("ecom.cart").browse(cart_id)
            set_active_company(1)
            user_id = get_active_user()
            website = self.context["website"]
            ctx = self.context
            ctx["cart"] = cart
            if not cart.is_paid and website.payment_slip_template_id and (cart.pay_method_id.id == website.bank_method_id.id):
                tmpl_name = website.payment_slip_template_id.name
                url = "/report?type=report_jasper&model=ecom.cart&convert=pdf&ids=[%d]&template=%s" % (
                    cart.id, tmpl_name)
                ctx["payment_slip_report_url"] = url
            content = render("ecom_order_confirmed", ctx)
            ctx["content"] = content
            html = render("cms_layout", ctx)
            self.write(html)
            db.commit()
        except:
            import traceback
            traceback.print_exc()
            db.rollback()

    def post(self):
        self.get()

OrderConfirmed.register()
