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
from netforce.database import get_connection, get_active_db  # XXX: move this
from netforce.locale import set_active_locale, get_active_locale
from netforce.access import set_active_company
from .cms_base import BaseController
import time
from pprint import pprint
import requests
from lxml import etree


class OrderDetails(BaseController):
    _path = "/ecom_order_details"

    def get(self):
        db = get_connection()
        try:
            website = self.context["website"]
            ctx = self.context
            cart_id = int(self.get_argument("cart_id"))
            cart = get_model("ecom.cart").browse(cart_id)
            ctx["cart"] = cart
            #if not cart.is_paid and website.payment_slip_template_id and (cart.pay_method_id.id == website.bank_method_id.id) and cart.state == "confirmed":
                #tmpl_name = website.payment_slip_template_id.name
                #url = "/report?type=report_jasper&model=ecom.cart&convert=pdf&ids=[%d]&template=%s" % (
                #    cart.id, tmpl_name)
                #ctx["payment_slip_report_url"] = url


            if not cart.is_paid and cart.state == "confirmed":

                meth=cart.pay_method_id
                if not meth:
                    raise Exception("Missing payment method")
                if meth.type == "bank":
                    if website.payment_slip_template_id:
                        tmpl_name = website.payment_slip_template_id.name
                        url = "/report?type=report_jasper&model=ecom.cart&convert=pdf&ids=[%d]&template=%s" % (
                            cart.id, tmpl_name)
                        ctx["payment_slip_report_url"] = url
                elif meth.type == "paypal":
                    if not meth.paypal_user:
                        raise Exception("Missing paypal user")
                    if not meth.paypal_password:
                        raise Exception("Missing paypal password")
                    if not meth.paypal_signature:
                        raise Exception("Missing paypal signature")
                    if not meth.paypal_url:
                        raise Exception("Missing paypal URL Server")
                    if meth.paypal_url == "test":
                        url = "https://api-3t.sandbox.paypal.com/nvp"
                    else:
                        url = "https://api-3t.paypal.com/nvp"
                    params = {
                        "method": "SetExpressCheckout",
                        "PAYMENTREQUEST_0_ITEMAMT": "%.2f" % (cart.amount_total - cart.amount_ship),
                        "PAYMENTREQUEST_0_AMT": "%.2f" % cart.amount_total,
                        "PAYMENTREQUEST_0_SHIPPINGAMT": "%.2f" % cart.amount_ship,
                        "PAYMENTREQUEST_0_CURRENCYCODE": "THB",
                        "PAYMENTREQUEST_0_PAYMENTACTION": "Sale",
                        "PAYMENTREQUEST_0_INVNUM": cart.number,
                        "returnUrl": "%s://%s/ecom_return_paypal?cart_id=%s" % (self.request.protocol, self.request.host, cart.id),
                        "cancelUrl": "%s://%s/ecom_order_cancelled?cart_id=%s" % (self.request.protocol, self.request.host, cart.id),
                        "version": "104.0",
                        "user": meth.paypal_user,
                        "pwd": meth.paypal_password,
                        "signature": meth.paypal_signature,
                    }
                    for i, line in enumerate(cart.lines):
                        params.update({
                            "L_PAYMENTREQUEST_0_NAME%d" % i: line.product_id.name,
                            "L_PAYMENTREQUEST_0_AMT%d" % i: "%.2f" % (line.amount / line.qty),
                            "L_PAYMENTREQUEST_0_QTY%d" % i: "%d" % line.qty,
                        })
                    try:
                        r = requests.get(url, params=params)
                        print("URL", r.url)
                        print("params", params)
                        res = urllib.parse.parse_qs(r.text)
                        print("RES", res)
                        token = res["TOKEN"][0]
                    except:
                        raise Exception("Failed start paypal transaction")
                    print("TOKEN", token)
                    if meth.paypal_url == "test":
                        url = "https://www.sandbox.paypal.com/cgi-bin/webscr?cmd=_express-checkout&token=%s" % token
                    else:
                        url = "https://www.paypal.com/cgi-bin/webscr?cmd=_express-checkout&token=%s" % token
                    ctx["payment_url"] = url
                elif meth.type == "paysbuy":
                    psbID = meth.paysbuy_id
                    if not meth.paysbuy_username:
                        raise Exception("Missing paysbuy username")
                    username = meth.paysbuy_username
                    if not meth.paysbuy_securecode:
                        raise Exception("Missing paysbuy secure code")
                    secureCode = meth.paysbuy_securecode
                    if not meth.paysbuy_url:
                        raise Exception("Missing paysbuy server URL")
                    if meth.paysbuy_url == "test":
                        url = "http://demo.paysbuy.com/api_paynow/api_paynow.asmx/api_paynow_authentication_new"
                    else:
                        url = "https://paysbuy.com/api_paynow/api_paynow.asmx/api_paynow_authentication_new"
                    itm = " & ".join(["%s x %s" % (line.product_id.name, line.qty) for line in cart.lines])
                    data = {
                        "psbId": psbID,
                        "username": username,
                        "secureCode": secureCode,
                        "inv": cart.number,
                        "itm": itm,
                        "amt": "%.2f" % cart.amount_total,
                        "curr_type": "TH",
                        "method": 1,
                        "language": "T",
                        "resp_front_url": "%s://%s/ecom_return_paysbuy?cart_id=%s" % (self.request.protocol, self.request.host, cart.id),
                        "resp_back_url": "%s://%s/ecom_notif_paysbuy?cart_id=%s" % (self.request.protocol, self.request.host, cart.id),
                        "paypal_amt": "",
                        "com": "",
                        "opt_fix_redirect": "1",
                        "opt_fix_method": "",
                        "opt_name": "",
                        "opt_email": "",
                        "opt_mobile": "",
                        "opt_address": "",
                        "opt_detail": "",
                    }
                    print("url", url)
                    print("Data sent to paysbuy:")
                    pprint(data)
                    try:
                        r = requests.post(url, data=data)
                        print("Paysbuy response:", r.text)
                        res = r.text.encode(encoding="utf-8")
                        parser = etree.XMLParser(ns_clean=True, recover=True, encoding='utf-8')
                        tree = etree.fromstring(res, parser)
                        response = tree.text
                        code = response[0:2]
                        refid = response[2:]
                        print("refid: %s" % refid)
                    except:
                        raise Exception("Failed start paysbuy transaction")
                    if code == "00":
                        if meth.paysbuy_url == "test":
                            url = "http://demo.paysbuy.com/api_payment/paynow.aspx?refid=%s" % refid
                        else:
                            url = "https://paysbuy.com/api_payment/paynow.aspx?refid=%s" % refid
                    else:
                        raise Exception("Invalid paysbuy response code: %s" % code)
                    ctx["payment_url"] = url
                elif meth.type == "scb_gateway":
                    if not meth.scb_mid:
                        raise Exception("Missing SCB merchant ID")
                    mid = meth.scb_mid
                    if not meth.scb_terminal:
                        raise Exception("Missing SCB terminal ID")
                    terminal = meth.scb_terminal
                    if not meth.scb_url:
                        raise Exception("Missing SCB server URL")
                    sale_date = time.strptime(cart.date_created, '%Y-%m-%d %H:%M:%S')
                    date = time.strftime('%Y%m%d%H%M%S', sale_date)
                    params = [
                        ('mid', mid),
                        ('terminal', terminal),
                        ('command', 'CRAUTH'),
                        ('ref_no', cart.number),
                        ('ref_date', date),
                        ('service_id', 10),
                        ('cur_abbr', 'THB'),
                        ('amount', '%.2f' % float(cart.amount_total)),
                        ('backURL', 'http://%s/ecom_returnscb?cart_id=%s' % (self.request.host, cart.id))
                    ]
                    urlparams = '&'.join(['%s=%s' % (k, v) for (k, v) in params])
                    if meth.scb_url == "test":
                        url = 'https://nsips-test.scb.co.th:443/NSIPSWeb/NsipsMessageAction.do?' + urlparams
                    else:
                        url = 'https://nsips.scb.co.th/NSIPSWeb/NsipsMessageAction.do?' + urlparams
                    ctx["payment_url"] = url


            content = render("ecom_order_details", ctx)
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
            ctx = self.context
            cart_id = int(self.get_argument("cart_id"))
            cart = get_model("ecom.cart").browse(cart_id)
            action = self.get_argument("action")
            if action == "cancel_cart":
                set_active_company(1) #XXX Set to ICC company
                cart.ecom_cancel_cart()
                cart.trigger("cancel_by_customer")
                self.redirect("/cms_account")
            else:
                raise Exception("Invalid post action")
            db.commit()
        except:
            import traceback
            traceback.print_exc()
            db.rollback()

OrderDetails.register()
