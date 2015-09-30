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
from netforce.database import get_connection  # XXX: move this
from .cms_base import BaseController


class CartChange(BaseController):
    _path = "/ecom_cart_change"

    def get(self):
        print("ecom_cart_change")
        db = get_connection()
        try:
            line = int(self.get_argument("line"))
            qty = int(self.get_argument("qty"))
            cart_id = self.get_cookie("cart_id", None)
            if cart_id:
                cart_id = int(cart_id)
                line = get_model("ecom.cart.line").search_browse(
                    [["cart_id", "=", cart_id], ["sequence", "=", line]])[0]
                line.change_qty(qty)
                cart = get_model("ecom.cart").browse(cart_id)
                if not cart.lines:
                    #cart.delete()
                    self.clear_cookie("cart_id")
            print("commit")
            db.commit()
            print("redirect")
            self.redirect("/ecom_cart")
        except:
            import traceback
            traceback.print_exc()
            db.rollback()

CartChange.register()
