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

def list_categ_parent(obj, categ_list):
    if obj.parent_id:
        categ_list = list_categ_parent(obj.parent_id, categ_list)
    categ_list.append(obj)
    return categ_list

class ProductCateg(BaseController):
    _path = "/ecom_product_categ"

    def get(self):
        db = get_connection()
        try:
            ctx = self.context
            categ_id=self.get_argument("categ_id",None)
            if categ_id:
                categ_id = int(categ_id)
            else:
                categ_code=self.get_argument("categ_code",None)
                res=get_model("product.categ").search([["code","=",categ_code]])
                if not res:
                    raise Exception("Product categ not found: '%s'"%categ_code)
                categ_id=res[0]
            res = get_model("product.categ").browse([categ_id])
            if not res:
                raise Exception("Can't find product category id: ",categ_id)
            categ = res[0]
            ctx["product_categ"] = categ
            ctx["parent_categ_list"] = list_categ_parent(categ, categ_list=[])
            content = render("ecom_product_categ", ctx)
            ctx["content"] = content
            html = render("cms_layout", ctx)
            self.write(html)
            db.commit()
        except:
            self.redirect("/cms_page_not_found")
            import traceback
            traceback.print_exc()
            db.rollback()

ProductCateg.register()
