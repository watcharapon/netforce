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

from netforce.model import get_model
from netforce.database import get_connection
from netforce.logger import audit_log
from .cms_base import BaseController
from netforce.access import set_active_user, set_active_company
import urllib.parse
import urllib.request
import time


class PaypalIPN(BaseController):
    _path = "/ecom_paypal_ipn"

    def post(self):
        try:
            db = get_connection()
            print("########################################")
            print("###########Result Paypal Ipn############")
            print("########################################")

            payment_status = self.get_argument("payment_status", None)
            if payment_status != "Completed":
                raise Exception("Paypal transaction is not completed")
            invoice = self.get_argument("invoice")

            set_active_user(1)
            set_active_company(1)
            res = get_model("ecom.cart").search([["number", "=", invoice]])
            if not res:
                raise Exception("Invalid cart number: %s"%invoice)
            cart_id = res[0]
            cart=get_model("ecom.cart").browse(cart_id)
            website=cart.website_id
            receiver_email = self.get_argument("receiver_email", None)
            if receiver_email != website.paypal_user:
                raise Exception("Wrong paypal receiver email")

            if not website.paypal_user:
                raise Exception("Missing paypal user in cms setting")
            if not website.paypal_password:
                raise Exception("Missing paypal password in cms setting")
            if not website.paypal_signature:
                raise Exception("Missing paypal signature in cms setting")
            if not website.paypal_url:
                raise Exception("Missing paypal URL Server in cms setting")
            params = {}
            for argument in self.request.arguments:
                params[argument] = argument[0].decode('utf-8')
            params['cmd'] = '_notify-validate'
            if website.paypal_url == "test":
                url = "https://www.sandbox.paypal.com/cgi-bin/webscr"
            else:
                url = "https://www.paypal.com/cgi-bin/webscr"
            data = urllib.parse.urlencode(params)
            data = data.encode('utf-8')
            req = urllib.request.Request(url, data)
            response = urllib.request.urlopen(req)
            word = response.read()
            verify = word.decode('utf-8')
            if verify != "VERIFIED":
                raise Exception("Failed to verify payment")
            mc_gross = float(self.get_argument("mc_gross", None))
            if cart.amount_total != mc_gross:
                raise Exception("Amount total doesn't match")
            cart.import_paypal_payment()  # TODO Add Token
            print("Payment Created")
            db.commit()
        except Exception as e:
            db = get_connection()
            db.rollback
            import traceback
            audit_log("Failed to get IPN from paypal", details=traceback.format_exc())
            traceback.print_exc()

PaypalIPN.register()
