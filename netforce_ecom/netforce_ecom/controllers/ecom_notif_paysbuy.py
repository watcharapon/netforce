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
from netforce.model import fields, get_model
from netforce import database
from netforce.database import get_connection
from netforce.logger import audit_log
from .cms_base import BaseController
from netforce.access import get_active_company, set_active_user, set_active_company
import urllib.parse
import urllib.request
import time


class NotifPaysbuy(BaseController):
    _path = "/ecom_notif_paysbuy"

    def post(self):
        try:
            db = get_connection()
            result = self.get_argument("result")
            method = self.get_argument("method", None)
            cart_no = result[2:]
            res = get_model("ecom.cart").search([["number", "=", cart_no]])
            if not res:
                raise Exception("Invalid cart  number")
            cart_id=res[0]
            cart=get_model("ecom.cart").browse(cart_id)
            if method:
                cart.update_paysbuy_method(method)
            if result.startswith("00") and not cart.is_paid:
                set_active_user(1)
                set_active_company(1)
                cart.import_paysbuy_payment()  # Inquiry Doublecheck
            db.commit()
        except Exception as e:
            db = get_connection()
            db.rollback
            import traceback
            audit_log("Failed to get result payment from paysbuy", details=traceback.format_exc())
            traceback.print_exc()


NotifPaysbuy.register()
