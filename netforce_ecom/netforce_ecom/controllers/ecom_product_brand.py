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

def list_brand_parent(obj, brand_list):
    if obj.parent_id:
        brand_list = list_brand_parent(obj.parent_id, brand_list)
    brand_list.append(obj)
    return brand_list

class ProductBrand(BaseController):
    _path = "/ecom_product_brand"

    def get(self):
        db = get_connection()
        try:
            ctx = self.context
            brand_id=self.get_argument("brand_id",None)
            if brand_id:
                brand_id = int(brand_id)
            else:
                brand_code=self.get_argument("brand_code",None)
                res=get_model("product.brand").search([["code","=",brand_code]])
                if not res:
                    raise Exception("Product brand not found: '%s'"%brand_code)
                brand_id=res[0]
            res = get_model("product.brand").browse([brand_id])
            if not res:
                raise Exception("Can't find product brand id: ",brand_id)
            brand = res[0]
            ctx["product_brand"] = brand
            ctx["parent_brand_list"] = list_brand_parent(brand, brand_list=[])
            content = render("ecom_product_brand", ctx)
            ctx["content"] = content
            html = render("cms_layout", ctx)
            self.write(html)
            db.commit()
        except:
            self.redirect("/cms_page_not_found")
            import traceback
            traceback.print_exc()
            db.rollback()

ProductBrand.register()
