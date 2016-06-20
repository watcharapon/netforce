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
from netforce.utils import get_data_path


class CopyPR2PO(Model):
    _name="copy.pr2po"
    _transient=True

    _fields={
        "request_id": fields.Many2One("purchase.request", "Purchase Request", required=True, on_delete="cascade"),
        'contact_id': fields.Many2One("contact","Contact",required=True),
        "bill_address_id": fields.Many2One("address", "Billing Address"),
        "ship_address_id": fields.Many2One("address", "Shipping Address"),
        'lines': fields.One2Many("copy.pr2po.line","pr2po_id","Lines"),
        'complete': fields.Boolean("Complete"),
    }

    def _get_request(self, context={}):
        request_id=int(context.get('refer_id') or "")
        return request_id

    def _get_lines(self, context={}):
        request_id=int(context.get('refer_id') or "")
        lines=[]
        if request_id:
            rq=get_model("purchase.request").browse(request_id)
            for line in rq.lines:    
                qty=line.qty or 0
                unit_price=0
                line_vals={
                    'description': line.description,
                    'qty': qty,
                    'uom_id': line.uom_id.id,
                    'location_id': line.location_id.id,
                }
                product=line.product_id
                if product:
                    unit_price=product.purchase_price or 0
                    line_vals.update({
                        'product_id': product.id,
                        'unit_price': unit_price
                    })
                amt=qty*unit_price
                line_vals['amount']=amt
                lines.append(line_vals)
        return lines

    _defaults={
        'request_id': _get_request,
        'lines': _get_lines,
        'complete': True,
    }

    def copy(self, ids, context={}):
        obj=self.browse(ids)[0]
        contact=obj.contact_id
        rq=obj.request_id
        vals={
            'ref': rq.number,
            'contact_id': contact.id,
            'ship_address_id': obj.ship_address_id.id,
            'bill_address_id': obj.bill_address_id.id,
            'contact_id': contact.id,
            'lines': [],
        }
                
        for line in obj.lines:
            qty=line.qty or 0
            line_vals={
                'description': line.description,
                'qty': qty,
                'uom_id': line.uom_id.id,
                'location_id': line.location_id.id,
            }
            product=line.product_id
            unit_price=0
            if product:
                line_vals['product_id']=product.id
                unit_price=product.purchase_price or 0
                line_vals['unit_price']=unit_price
            amt=unit_price*qty
            line_vals['amount']=amt
            vals['lines'].append(('create', line_vals))

        new_id=get_model('purchase.order').create(vals)
        po=get_model("purchase.order").browse(new_id)
        po.write({
            'request_id': rq.id,
        })
        if obj.complete:
            rq.btn_done()
        return {
            'next': {
                'name': 'purchase',
                'mode': 'form',
                'active_id': new_id,
            },
            'flash': 'Copy to purchase order, %s successfully'%(po.number)
        }

    def onchange_contact(self, context={}):
        data=context['data']
        contact_id=data['contact_id']
        contact=get_model("contact").browse(contact_id)
        data['ship_address_id']=None
        data['bill_address_id']=None
        for address in contact.addresses:
            if address.type=='shipping':
                data['ship_address_id']=address.id
            elif address.type=='billing':
                data['bill_address_id']=address.id
        return data

    def onchange_product(self, context={}):
        data=context['data']
        path=context['path']
        line=get_data_path(data, path, parent=True)
        product_id=line['product_id']
        product=get_model('product').browse(product_id)
        line['description']=product.description or product.name
        qty=line.get('qty') or 1
        unit_price=product.purchase_price or 0
        amt=qty*unit_price
        line['qty']=qty
        line['unit_price']=unit_price
        line['amount']=amt
        uom_id=product.uom_id.id #default
        if product.purchase_uom_id:
            uom_id=product.purchase_uom_id.id
        line['uom_id']=uom_id

        if product.locations:
            line["location_id"] = product.locations[0].location_id.id
            for loc in product.locations:
                if loc.stock_qty:
                    line['location_id']=product.location_id.id
                    break
        return data

    def update_amount(self,context={}):
        data=context['data']
        for line in data['lines']:
            line['amount']=(line.get('qty') or 0) * (line.get("unit_price") or 0)
        return data

CopyPR2PO.register()
