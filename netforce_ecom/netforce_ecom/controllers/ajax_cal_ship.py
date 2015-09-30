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
from netforce.database import get_connection  # XXX: move this
from .cms_base import BaseController
import json


class AjaxCalShip(BaseController):
    _path = "/ajax_cal_ship"

    def post(self):
        db = get_connection()
        try:
            data_json = self.get_argument("json_str",None)
            if not data_json:
                raise Exception("Can't get json_str")
            data = json.loads(data_json)
            cart_id = self.get_cookie("cart_id",None)
            if not cart_id:
                raise Exception("Can't get cart id")
            cart_id = int(cart_id)
            cart = get_model("ecom.cart").browse(cart_id)
            order = 0
            for line in cart.lines:
                for item in data: 
                    if item.get('order') == order:
                        line.write({"ship_method_id": item.get('method_id')})
                order += 1
            cart.calc_shipping()
            amount_ship = "{:0,.2f}".format(float(cart.amount_ship))
            amount_total = "{:0,.2f}".format(float(cart.amount_total))
            total = {
                "amount_ship": amount_ship,
                "amount_total": amount_total,
            }
            data = json.dumps(total)
            self.write(data)
            db.commit()
        except:
            import traceback
            traceback.print_exc()
            db.rollback()

AjaxCalShip.register()
