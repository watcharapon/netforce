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


class Seller(BaseController):
    _path = "/ecom_seller"

    def get(self):
        db = get_connection()
        try:
            ctx = self.context
            seller_id = int(self.get_argument("seller_id"))
            comp = get_model("company").browse(seller_id)
            #products=get_model("product").search_browse([["company_id","=",seller_id]])
            res = get_model("product.group").search_browse([["code","=","seller_new"],["company_id","=",seller_id]])
            if not res:
                raise Exception("No product group code 'seller_new' in company: ",comp.name)
            new_product_group = res[0]
            res = get_model("product.group").search_browse([["code","=","seller_rec"],["company_id","=",seller_id]])
            if not res:
                raise Exception("No product group code 'seller_new' in company: ",comp.name)
            rec_product_group = res[0]
            ctx["seller"]={
                "name": comp.name,
                "new_product_group": new_product_group,
                "rec_product_group": rec_product_group,
            }
            content = render("ecom_seller", ctx)
            ctx["content"] = content
            html = render("cms_layout", ctx)
            self.write(html)
            db.commit()
        except:
            self.redirect("/cms_page_not_found")
            import traceback
            traceback.print_exc()
            db.rollback()

Seller.register()
