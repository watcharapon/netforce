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


class ReviewAdd(BaseController):
    _path = "/ecom_review_add"

    def post(self):
        db = get_connection()
        try:
            vals = {
                "name": self.get_argument("name"),
                "title": self.get_argument("title"),
                "review": self.get_argument("review"),
                "rating": self.get_argument("rating"),
                "product_id": self.get_argument("product_id"),
                "date": time.strftime("%Y-%m-%d %H:%M:%S"),
                "state": "draft",
            }
            get_model("ecom.product.review").create(vals)
            db.commit()
        except:
            import traceback
            traceback.print_exc()
            db.rollback()

ReviewAdd.register()
