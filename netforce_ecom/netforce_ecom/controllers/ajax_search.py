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
import json


class AjaxSearch(BaseController):
    _path = "/ajax_search"

    def get(self):
        db = get_connection()
        try:
            keyword = self.get_argument("keyword")
            domain = [["or",["name","ilike",keyword],["description","ilike",keyword],["code","ilike",keyword]],["parent_id","=",None],["is_published","=",True]]
            result = get_model("product").search_browse(domain)
            #if not result:
                #raise Exception("Product not found")
            products = []
            for product in result:
                vals = {
                    "name": product.name,
                    "id": product.id,
                    "desc": product.description[:20]+"..." if product.description else ""
                }
                products.append(vals)
            products = sorted(products, key=lambda k: k['name'])
            print(products)
            data = json.dumps(products)
            self.write(data)
            db.commit()
        except:
            import traceback
            traceback.print_exc()
            db.rollback()

AjaxSearch.register()
