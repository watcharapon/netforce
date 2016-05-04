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
from netforce.database import get_connection # XXX: move this
from .cms_base import BaseController
import re

class Search(BaseController):
    _path="/cms_search"

    def get(self):
        db=get_connection()
        try:
            ctx=self.context
            q = self.get_argument("q","")
            minprice = self.get_argument("minprice","")
            maxprice = self.get_argument("maxprice","")
            website=ctx["website"]
            browse_ctx = {
                "pricelist_id": website.sale_channel_id.pricelist_id.id if website.sale_channel_id else None,
            }
            condition = [["state","=","approved"]]
            if minprice: condition.append(["sale_price", ">=", minprice])
            if maxprice: condition.append(["sale_price", "<=", maxprice])
            for word in q.split():
                condition.append(["or",["name","ilike",word],["description","ilike",word]])
            results=[]
            if condition:
                condition.append(["parent_id","=",None]) #Filter out variant
                results=get_model("product").search_browse(condition=condition, context=browse_ctx)
            for result in results:
                print("RES:", result.sale_price, result.name)
            ctx["search"]={
                "query": q,
                "minprice": minprice,
                "maxprice": maxprice,
                "results": results,
            }
            content=render("ecom_search",ctx)
            ctx["content"]=content
            html=render("cms_layout",ctx)
            self.write(html)
            db.commit()
        except:
            import traceback
            traceback.print_exc()
            db.rollback()

Search.register()
