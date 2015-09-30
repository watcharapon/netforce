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


class GetPostalCode(BaseController):
    _path = "/get_postal_code"

    def get(self):
        db = get_connection()
        try:
            province_id = self.get_argument("province_id")
            province = get_model("province").browse(int(province_id))
            if not province:
                raise Exception("Province not found")

            district_id = self.get_argument("district_id")
            district = get_model("district").browse(int(district_id))
            if not district:
                raise Exception("District not found")

            subdistrict_id = self.get_argument("subdistrict_id")
            subdistrict = get_model("subdistrict").browse(int(subdistrict_id))
            if not subdistrict:
                raise Exception("SubDistrict not found")

            postal_codes = []
            postal_obj = get_model("postal.code").search_browse(
                [["province_id", "=", province.id], ["district_id", "=", district.id], ["subdistrict_id", "=", subdistrict.id]])
            for postal_code in postal_obj:
                vals = {
                    "code": postal_code.code,
                    "id": postal_code.id,
                }
                postal_codes.append(vals)
            postal_codes = sorted(postal_codes, key=lambda k: k['code'])
            print(postal_codes)
            data = json.dumps(postal_codes)
            self.write(data)
            db.commit()
        except:
            import traceback
            traceback.print_exc()
            db.rollback()

GetPostalCode.register()
