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
import time


class WishlistAdd(BaseController):
    _path = "/ecom_wishlist_add"

    def post(self):
        db = get_connection()
        try:
            user_id = self.get_cookie("user_id", None)
            product_id = self.get_argument("product_id")
            if user_id:
                user_id = int(user_id)
                user = get_model("base.user").browse(user_id)
                if not user.contact_id:
                    raise Exception("Cannot find contact with user_id: ",user_id)
                vals = {
                    "contact_id": user.contact_id.id,
                    "product_id": product_id,
                    "date": time.strftime("%Y-%m-%d %H:%M:%S"),
                }
                res = db.query(
                    "SELECT COUNT(*) FROM ecom_wishlist WHERE contact_id = %s AND product_id = %s" % (user.contact_id.id, product_id))
                res = res[0]['count'] or 0
                if res == 0:
                    get_model("ecom.wishlist").create(vals)
                    db.commit()
        except:
            import traceback
            traceback.print_exc()
            db.rollback()

WishlistAdd.register()
