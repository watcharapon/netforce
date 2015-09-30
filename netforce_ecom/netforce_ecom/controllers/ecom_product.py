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
from netforce import utils
from .cms_base import BaseController
from netforce import access

def list_categ_parent(obj, categ_list):
    if obj.parent_id:
        categ_list = list_categ_parent(obj.parent_id, categ_list)
    categ_list.append(obj)
    return categ_list

class Product(BaseController):
    _path = "/ecom_product"

    def get(self):
        db = get_connection()
        try:
            ctx = self.context
            website_id=self.request.headers.get("X-Website-ID")
            if website_id:
                website_id=int(website_id)
            else:
                res=get_model("website").search([["state","=","active"]])
                if not res:
                    raise Exception("No website found")
                website_id=res[0]
            self.website_id=website_id
            website=get_model("website").browse(website_id)
            browse_ctx={
                "website_id": website.id,
                "theme_id": website.theme_id.id,
                "sale_channel_id": website.sale_channel_id.id,
                "pricelist_id": website.sale_channel_id.pricelist_id.id if website.sale_channel_id else None,
            }
            product_id = self.get_argument("product_id")
            product_id = int(product_id)
            prod = get_model("product").browse([product_id],context=browse_ctx)[0]
            if not prod.is_published and not access.check_permission_other("ecom_preview_product"):
                raise Exception("Product is not published")
            ctx["product"] = prod
            prod_vals = {
                "name": prod.name,
                "code": prod.code,
                "decription": prod.description,
                "image": prod.image,
                "sale_price": prod.customer_price,
                "variants": [],
                "images": [],
                "custom_options": [],
                "attributes": [],
                "type": prod.type,
            }
            if prod.customer_has_discount:
                prod_vals["old_price"] = prod.sale_price
            for img in prod.images:
                img_vals = {
                    "image": img.image,
                    "title": img.title,
                }
                prod_vals["images"].append(img_vals)
            for var in prod.variants:
                var_vals = {
                    "id": var.id,
                    "name": var.name,
                    "price": var.customer_price,
                    "stock_qty": var.stock_qty,
                    "image": var.image,
                    "images": [prod_image.image for prod_image in var.images],
                    "attributes": [],
                }
                if var.customer_has_discount:
                    var_vals["old_price"] = var.sale_price
                for attr in var.attributes:
                    attr_vals = {
                        "name": attr.attribute_id.name if attr.attribute_id else None,
                        "code": attr.attribute_id.code if attr.attribute_id else None,
                        "value": attr.option_id.code if attr.option_id else None,
                    }
                    var_vals["attributes"].append(attr_vals)
                prod_vals["variants"].append(var_vals)
            for attr in prod.attributes:
                attr_vals = {
                    "name": attr.attribute_id.name if attr.attribute_id else None,
                    "code": attr.attribute_id.code if attr.attribute_id else None,
                    "value": attr.option_id.code if attr.option_id else None,
                }
                prod_vals["attributes"].append(attr_vals)
            ctx["parent_categ_list"] = list_categ_parent(prod.categ_id, categ_list=[])
            ctx["product_json"] = utils.json_dumps(prod_vals)
            content = render("ecom_product", ctx)
            ctx["content"] = content
            html = render("cms_layout", ctx)
            self.write(html)
            db.commit()
        except:
            self.redirect("/cms_page_not_found")
            import traceback
            traceback.print_exc()
            db.rollback()

Product.register()
