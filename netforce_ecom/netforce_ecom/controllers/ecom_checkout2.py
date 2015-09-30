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
from netforce.utils import new_token
import requests
import urllib.parse
from lxml import etree
from .cms_base import BaseController
from netforce.access import get_active_company, set_active_user, set_active_company, get_active_user
import time
from pprint import pprint


class Checkout2(BaseController):
    _path = "/ecom_checkout2"

    def get(self):
        db = get_connection()
        try:
            ctx = self.context
            cart = ctx.get("cart")
            if not cart:
                db.commit()
                self.redirect("/cms_index")
                return
            if not cart.email or not cart.bill_first_name or not cart.bill_phone:  # XXX
                self.redirect("/cms_index")
                return
            ctx["ship_methods"] = cart.get_ship_methods()
            content = render("ecom_checkout2", ctx)
            ctx["content"] = content
            html = render("cms_layout", ctx)
            self.write(html)
            db.commit()
        except:
            import traceback
            traceback.print_exc()
            db.rollback()

    def post(self):
        website=self.context["website"]
        db = get_connection()
        try:
            if self.get_argument("commit", None):
                cart_id = self.get_argument("cart_id")
                cart_id = int(cart_id)
                fnames = [
                    "accept_marketing",
                ]
                vals = {}
                for n in fnames:
                    v = self.get_argument(n, None)
                    f = get_model("ecom.cart")._fields[n]
                    if v:
                        if isinstance(f, fields.Boolean):
                            v = v and True or False
                        elif isinstance(f, fields.Many2One):
                            v = int(v)
                    vals[n] = v
                if self.get_argument("check_tax", None):
                    if not self.get_argument("tax_no", None):
                        raise Exception("Please Enter Tax ID")
                    vals["tax_no"] = self.get_argument("tax_no", None)
                else:
                    vals["tax_no"] = ""
                if self.get_argument("tax_branch_no",None):
                    vals["tax_branch_no"]= self.get_argument("tax_branch_no",None)
                else:
                    vals["tax_branch_no"]= ""
                pay_method=self.get_argument("pay_method",None)
                if not pay_method:
                    raise Exception("Missing payment method")
                if pay_method=="bank_transfer":
                    pay_method_id=website.bank_method_id.id
                elif pay_method=="paypal":
                    pay_method_id=website.paypal_method_id.id
                elif pay_method=="paysbuy":
                    pay_method_id=website.paysbuy_method_id.id
                elif pay_method=="scb_gateway":
                    pay_method_id=website.scb_method_id.id
                else:
                    raise Exception("Invalid payment method")
                if not pay_method_id:
                    raise Exception("Payment method not configured")
                vals["pay_method_id"]=pay_method_id
                print("CART VALS", vals)
                get_model("ecom.cart").write([cart_id], vals)
                for arg in self.request.arguments:
                    if not arg.startswith("LINE_SHIP_METHOD_"):
                        continue
                    line_id=int(arg.replace("LINE_SHIP_METHOD_",""))
                    ship_method_code=self.get_argument(arg)
                    if ship_method_code:
                        res=get_model("ship.method").search([["code","=",ship_method_code]])
                        if not res:
                            raise Exception("Shipping method not found: %s"%ship_method_code)
                        ship_method_id=res[0]
                    else:
                        ship_method_id=None
                    vals={
                        "ship_method_id": ship_method_id,
                    }
                    print("line_id=%s => ship_method_id=%s"%(line_id,ship_method_id))
                    get_model("ecom.cart.line").write([line_id],vals)
                cart = get_model("ecom.cart").browse(cart_id)
                is_accept = self.get_argument("accept_marketing", None)
                if is_accept == 'on':
                    user_id = 1
                    res = get_model("sale.lead").search([["email", "=", cart.email]])
                    if not res:  # Check if this email already exist in Newsletter contact
                        vals = {
                            "state": "open",
                            "first_name": cart.bill_first_name,
                            "last_name": cart.bill_last_name,
                            "email": cart.email,
                            "user_id": user_id,
                        }
                        get_model("sale.lead").create(vals)
                    if not website.target_list_id:
                        raise Exception("No target list")
                    list_id = website.target_list_id.id
                    res = get_model("mkt.target").search([["email", "=", cart.email], ["list_id", "=", list_id]])
                    if not res:
                        target_vals = {
                            "list_id": list_id,
                            "first_name": cart.bill_first_name,
                            "last_name": cart.bill_last_name,
                            "email": cart.email,
                            "company": cart.bill_company,
                            "city": cart.bill_city,
                            "province_id": cart.bill_province_id.id,
                            "country_id": cart.bill_country_id.id,
                            "phone": cart.bill_phone,
                            "zip": cart.bill_postal_code,
                        }
                        get_model("mkt.target").create(target_vals)
                user_id = get_active_user()
                if not user_id and website.auto_create_account:
                    user_id = cart.create_account()
                    dbname = get_active_db()
                    token = new_token(dbname, user_id)
                    self.set_cookie("user_id", str(user_id))
                    self.set_cookie("token", token)
                set_active_user(1)
                set_active_company(1)
                cart.copy_to_contact({'force_write': False})
                if not user_id and website.auto_create_account: #First time create account
                    get_model("contact").trigger([cart.contact_id.id],"ecom_register")
                cart.copy_to_sale()
                cart = get_model("ecom.cart").browse(cart_id)
                db.commit()  # XXX: need otherwise browser redirect before commit?
                self.clear_cookie("cart_id")
                meth=cart.pay_method_id
                if not meth:
                    raise Exception("Missing payment method")
                if meth.type == "bank":
                    self.redirect("/ecom_order_confirmed?cart_id=%s" % cart.id)
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
                    self.redirect(url)
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
                    self.redirect(url)
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
                    self.redirect(url)
                else:
                    raise Exception("Unsupported payment method")
            db.commit()
        except Exception as e:
            import traceback
            traceback.print_exc()
            error_message = str(e)
            ctx = self.context
            cart = ctx.get("cart")
            if not cart:
                db.commit()
                self.redirect("/index")
                return
            ctx["ship_methods"] = cart.get_ship_methods()
            website=self.context["website"]
            ctx["error_message"] = error_message
            content = render("ecom_checkout2", ctx)
            ctx["content"] = content
            html = render("cms_layout", ctx)
            self.write(html)
            db.rollback()

Checkout2.register()
