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


class NewsletterAdd(BaseController):
    _path = "/ecom_newsletter_add"

    def post(self):
        db = get_connection()
        try:
            website=self.context["website"]
            name = self.get_argument("newsletter_name")
            email = self.get_argument("newsletter_email")
            # Leads
            vals = {
                "state": "open",
                "first_name": name,
                "last_name": name,
                "email": email,
                "user_id": 1,
            }
            res = get_model("sale.lead").search([["email", "=", vals['email']]])
            if not res:
                get_model("sale.lead").create(vals)
            # Target list
            if not website.target_list_id:
                raise Exception("No target list")
            list_id = website.target_list_id.id
            target_vals = {
                "list_id": list_id,
                "first_name": name,
                "last_name": name,
                "email": email,
            }
            res = get_model("mkt.target").search([["email", "=", email], ["list_id", "=", list_id]])
            if not res:
                get_model("mkt.target").create(target_vals)
            db.commit()
            self.redirect("/cms_index")
        except:
            import traceback
            traceback.print_exc()
            db.rollback()

NewsletterAdd.register()
