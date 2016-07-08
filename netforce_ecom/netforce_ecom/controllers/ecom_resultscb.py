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


class ResultSCB(BaseController):
    _path = "/ecom_resultscb"

    def post(self):
        #try:
        with database.Transaction():
            #db = get_connection()
            print("########################################")
            print("#######Result Payment Online SCB########")
            print("#############     POST    ##############")
            print("########################################")

            f = open("scblog", "a")
            s = "################################################################################################################" + \
                "\n"
            s += "Date : " + time.strftime("%Y-%m-%d %H:%M:%S") + "\n"
            s += "Request : " + str(self.request) + "\n"
            if self.request.body:
                s += "Body : " + str(self.request.body) + "\n"
            s += "################################################################################################################" + \
                "\n"
            f.write(s)
            f.close()

            if self.request.arguments:
                website = get_model("website").browse(1)
                if not website.scb_mid:
                    raise Exception("no merchant id in website settings")
                if not website.scb_terminal:
                    raise Exception("no terminal id in website settings")
                if not website.scb_url:
                    raise Exception("no URL server in website settings")
                mid = self.get_argument("mid", None)
                print(mid)
                if mid != website.scb_mid:
                    raise Exception("Merchant id does not match")
                terminal = self.get_argument("terminal", None)
                print(terminal)
                if terminal != website.scb_terminal:
                    raise Exception("Terminal id does not match")
                command = self.get_argument("command", None)
                print(command)
                if command != 'CRAUTH':
                    raise Exception("Command does not match")
                payment_status = self.get_argument("payment_status", None)
                print(payment_status)
                if payment_status == '003':
                    raise Exception("Payment host reject")
                if payment_status == '006':
                    raise Exception("Payment error")
                ref_no = self.get_argument("ref_no", None)
                print(ref_no)
                if payment_status == '002':
                    set_active_user(1)
                    set_active_company(1)
                    res = get_model("sale.order").search_browse([["number", "=", ref_no]])
                    if res:  # XXX Inquiry double check
                        sale = res[0]
                        if not sale.is_paid:
                            sale.import_scb_payment()
                            #db.commit()
                        #sale_date = time.strptime(sale.date, '%Y-%m-%d')
                        #date = time.strftime('%Y%m%d%H%M%S', sale_date)
                        # qs = urllib.parse.urlencode([
                        #('mid', mid),
                        #('terminal', terminal),
                        #('command', 'CRINQ'),
                        #('ref_no', sale.number),
                        #('ref_date', date),
                        #('service_id', 10),
                        #('cur_abbr', 'THB'),
                        #('amount', sale.amount_total),
                        #])
                        # if settings.scb_url == "test":
                        #url = 'https://nsips-test.scb.co.th:443/NSIPSWeb/NsipsMessageAction.do?'
                        # else:
                        #url = 'https://nsips.scb.co.th/NSIPSWeb/NsipsMessageAction.do?'
                        #data = qs.encode('utf-8')
                        #req = urllib.request.Request(url, data)
                        # print(qs)
                        #response = urllib.request.urlopen(req)
                        #ur = response.read()
                        # print(ur)
                        #te = ur.decode('utf-8')
                        #p = urllib.parse.parse_qsl(te)
                        #params = dict(list(map(lambda x: (x[0],x[1]),p)))
                        #inq_payment_status = params['payment_status'] or ''
                        #inq_payment_amount = params['amount'] or ''
                        # if not inq_payment_amount:
                        #raise Exception("Cannot get paid amount from SCB")
                        #inq_payment_amount = float(inq_payment_amount)
                        #print("Cart Amount --->%f"%sale.amount_total)
                        #print("Inquiry Amount--->%f"%inq_payment_amount)
                        # if abs(sale.amount_total-inq_payment_amount) >= 0.01:
                        #raise Exception("Pay amount does not match!!!")
                        # print(params)
                        # if inq_payment_status == "002":
                        # cart.write({"state":"paid"})
                        # db.commit()
                        # cart.copy_to_contact()
                        # if not cart.sale_id:
                        # cart.copy_to_sale()
                        #print("Payment Created")
                        # db.commit()
        #except Exception as e:
            #db = get_connection()
            #db.rollback
            #import traceback
            #audit_log("Failed to get result payment from scb", details=traceback.format_exc())
            #traceback.print_exc()

    def get(self):
        #try:
        with database.Transaction():
            print("########################################")
            print("#######Result Payment Online SCB########")
            print("#############     GET     ##############")
            print("########################################")

            f = open("scblog", "a")
            s = "################################################################################################################" + \
                "\n"
            s += "Date : " + time.strftime("%Y-%m-%d %H:%M:%S") + "\n"
            s += "Request : " + str(self.request) + "\n"
            if self.request.body:
                s += "Body : " + str(self.request.body) + "\n"
            s += "################################################################################################################" + \
                "\n"
            f.write(s)
            f.close()

            if self.request.arguments:
                website=self.context["website"]
                if not website.scb_mid:
                    raise Exception("no merchant id in website settings")
                if not website.scb_terminal:
                    raise Exception("no terminal id in website settings")
                if not website.scb_url:
                    raise Exception("no URL server in website settings")
                mid = self.get_argument("mid", None)
                print(mid)
                if mid != website.scb_mid:
                    raise Exception("Mercahant id does not match")
                terminal = self.get_argument("terminal", None)
                print(terminal)
                if terminal != website.scb_terminal:
                    raise Exception("Terminal id does not match")
                command = self.get_argument("command", None)
                print(command)
                if command != 'CRAUTH':
                    raise Exception("Command does not match")
                payment_status = self.get_argument("payment_status", None)
                print(payment_status)
                if payment_status == '003':
                    raise Exception("Payment host reject")
                if payment_status == '006':
                    raise Exception("Payment error")
                ref_no = self.get_argument("ref_no", None)
                print(ref_no)
                if payment_status == '002':
                    set_active_user(1)
                    set_active_company(1)
                    res = get_model("ecom.cart").search_browse([["id", "=", ref_no]])
                    if res:  # XXX Inquiry double check
                        sale = res[0]
                        if not sale.is_paid:
                            sale.import_scb_payment()
                            #db.commit()
        #except Exception as e:
            #db = get_connection()
            #db.rollback
            #import traceback
            #audit_log("Failed to get result payment from scb", details=traceback.format_exc())
            #traceback.print_exc()

ResultSCB.register()
