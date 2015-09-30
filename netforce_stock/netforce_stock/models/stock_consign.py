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
from netforce import access
from datetime import *
from dateutil.relativedelta import *

class StockConsign(Model):
    _name = "stock.consign"
    _string = "Consignment Stock"
    _name_field = "location_id"
    _multi_company = True
    _fields = {
        "location_id": fields.Many2One("stock.location","Stock Location",required=True,search=True),
        "contact_id": fields.Many2One("contact","Contact",required=True,search=True),
        "type": fields.Selection([["sale","Sell"],["purchase","Purchase"]],"Consignment Type",required=True,search=True),
        "company_id": fields.Many2One("company","Company",search=True),
        "periods": fields.One2Many("stock.consign.period","consign_id","Consignment Periods"),
        "order_type": fields.Selection([["stock","From Stock"],["sale","From Sales"]],"Create Order"),
    }
    _defaults = {
        "company_id": lambda *a: access.get_active_company(),
        "order_type": "stock",
    }

    def create_purchase(self,ids,context={}):
        for obj in self.browse(ids):
            if obj.type!="purchase":
                raise Exception("Wrong consignment type")
            for period in obj.periods:
                if period.purchase_id:
                    continue
                period.create_purchase()

    def create_sale(self,ids,context={}):
        for obj in self.browse(ids):
            if obj.type!="sale":
                raise Exception("Wrong consignment type")
            for period in obj.periods:
                if period.sale_id:
                    continue
                period.create_sale()

    def create_periods(self,ids,context={}):
        for obj in self.browse(ids):
            #date_from=date.today()
            #date_to=date_from
            #for i in range(7):
                #date_from_s=date_from.strftime("%Y-%m-%d")
                #date_to_s=date_to.strftime("%Y-%m-%d")
                #res=get_model("stock.consign.period").search([["consign_id","=",obj.id],["date_from","<=",date_to_s],["date_to",">=",date_from_s]])
                #if res:
                    #continue
                #vals={
                    #"consign_id": obj.id,
                    #"date_from": date_from_s,
                    #"date_to": date_to_s,
                #}
                #print("create consign period",obj.id,date_from_s,date_to_s)
                #get_model("stock.consign.period").create(vals)
                #date_from+=timedelta(days=1)
                #date_to+=timedelta(days=1)
            res = get_model("stock.consign.period").search_browse(condition=[["consign_id","=",obj.id]], order="date_from desc")
            if res:
                date_from_s = res[0].date_from
                date_from = datetime.strptime(date_from_s,"%Y-%m-%d")
            else:
                date_from = date.today()
                date_from_s = date_from.strftime("%Y-%m-%d")
            date_from = date_from + timedelta(days=1)
            create_month = date_from.strftime("%m")
            while create_month == date_from.strftime("%m"):
                date_from_s = date_from.strftime("%Y-%m-%d")
                date_to = date_from
                while 1:
                    res = get_model("hr.holiday").search([["date","=",(date_to+timedelta(days=1)).strftime("%Y-%m-%d")]])
                    if (date_to+timedelta(days=1)).weekday() < 5 and not res: 
                        break
                    date_to += timedelta(days=1)
                date_to_s = date_to.strftime("%Y-%m-%d")
                vals = {
                    "consign_id": obj.id,
                    "date_from": date_from_s,
                    "date_to": date_to_s, 
                }
                print("create consign period",obj.id,date_from_s,date_to_s)
                get_model("stock.consign.period").create(vals)
                date_from = date_to + timedelta(days=1)

StockConsign.register()
