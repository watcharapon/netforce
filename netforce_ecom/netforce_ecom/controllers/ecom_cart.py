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
from .cms_base import BaseController


class Cart(BaseController):
    _path = "/ecom_cart"

    def get(self):
        db = get_connection()
        try:
            ctx = self.context
            content = render("ecom_cart", ctx)
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
            cart_id = self.get_cookie("cart_id", None)
            cart_id = int(cart_id)
            cart = get_model("ecom.cart").browse(cart_id)
            action=self.get_argument("action",None)
            if action in ("checkout","update"):
                for line in cart.lines:
                    qty = self.get_argument("qty_%s" % line.sequence, None)
                    if qty != None:
                        qty = int(qty)
                        line.change_qty(qty)
                cart = get_model("ecom.cart").browse(cart_id)
                if cart.lines:
                    comments = self.get_argument("comments", None)
                    if comments != None:
                        cart.write({"comments": comments})
                    user_id = self.get_cookie("user_id", None)
                    if user_id:
                        user_id = int(user_id)
                        user = get_model("base.user").browse(user_id)
                        contact_id = user.contact_id.id
                        cart.write({"contact_id": contact_id})
                    coupon_code = self.get_argument("coupon_code", None)
                    if coupon_code != None:
                        cart.write({"coupon_code": coupon_code})
                    if action=="checkout":
                        self.redirect("/ecom_checkout")
                    else:
                        self.redirect("/ecom_cart")
                else:
                    cart.delete()
                    self.clear_cookie("cart_id")
                    self.redirect("/ecom_cart")
            elif action.startswith("apply_prom_"):
                prom_id=int(action.replace("apply_prom_",""))
                cart.apply_promotion_multi(prom_id)
                self.redirect("/ecom_cart")
            elif action.startswith("unapply_prom_"):
                prom_id=int(action.replace("unapply_prom_",""))
                cart.unapply_promotion(prom_id)
                self.redirect("/ecom_cart")
            else:
                raise Exception("Invalid action")
            db.commit()
        except:
            import traceback
            traceback.print_exc()
            db.rollback()
            self.redirect("/ecom_cart")  # XXX

Cart.register()
