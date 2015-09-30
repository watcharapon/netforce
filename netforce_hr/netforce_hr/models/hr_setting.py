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

from netforce.model import Model, fields, get_model
from netforce import database


class HRSetting(Model):
    _inherit = "settings"

    _fields = {
        # report address
        'addr_building': fields.Char('Building', size=64, multi_company=True),
        'addr_room_no': fields.Char('Room No', size=32, multi_company=True),
        'addr_floor': fields.Char('Floor', size=32, multi_company=True),
        'addr_village': fields.Char('Village', size=64, multi_company=True),
        'addr_no': fields.Char('No', size=32, multi_company=True),
        'addr_moo': fields.Char('Moo', size=10, multi_company=True),
        'addr_soi': fields.Char('Soi', size=64, multi_company=True),
        'addr_street': fields.Char('Street', size=64, multi_company=True),
        'addr_sub_district': fields.Char('Sub. Dist', size=64, multi_company=True),
        'addr_district': fields.Char('District', size=64, multi_company=True),
        'addr_province': fields.Char('Province', size=64, multi_company=True),
        'addr_zipcode': fields.Char('Zipcode', size=5, multi_company=True),
        'addr_tel': fields.Char('Tel', size=32, multi_company=True),
    }

HRSetting.register()
