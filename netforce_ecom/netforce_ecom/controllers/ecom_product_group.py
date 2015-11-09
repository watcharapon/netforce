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


class ProductGroup(BaseController):
    _path = "/ecom_product_group"

    def get(self):
        db = get_connection()
        try:
            ctx = self.context
            group_id=self.get_argument("group_id",None)
            website=ctx["website"]
            browse_ctx={
                "pricelist_id": website.sale_channel_id.pricelist_id.id if website.sale_channel_id else None,
            }
            user_id=self.get_cookie("user_id",None)
            if user_id:
                user_id=int(user_id)
                user=get_model("base.user").browse(user_id)
                contact = user.contact_id
                if contact.sale_price_list_id.id:
                    browse_ctx["pricelist_id"] =contact.sale_price_list_id.id 
                
            if group_id:
                group_id = int(group_id)
            else:
                group_code=self.get_argument("group_code",None)
                res=get_model("product.group").search([["code","=",group_code]])
                if not res:
                    raise Exception("Product group not found: '%s'"%group_code)
                group_id=res[0]
            res = get_model("product.group").browse([group_id], browse_ctx)
            if not res:
                raise Exception("Can't find product group id: ",group_id)
            group = res[0]
            ctx["product_group"] = group
            content = render("ecom_product_group", ctx)
            ctx["content"] = content
            html = render("cms_layout", ctx)
            self.write(html)
            db.commit()
        except:
            self.redirect("/cms_page_not_found")
            import traceback
            traceback.print_exc()
            db.rollback()

ProductGroup.register()
