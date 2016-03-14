from netforce.model import Model,fields,get_model

class Voucher(Model):
    _name="ecom2.voucher"
    _string="Voucher"
    _fields={
        "code": fields.Char("Voucher Code",required=True,search=True),
        "name": fields.Char("Voucher Name",required=True,search=True),
        "fixed_discount": fields.Decimal("Fixed Discount"),
        "min_order_amount": fields.Decimal("Min Order Amount"),
        "carts": fields.One2Many("ecom2.cart","voucher_id","Carts"),
        "state": fields.Selection([["active","Active"],["inactive","Inactive"]],"Status",required=True),
        "max_orders_per_customer": fields.Integer("Max Orders Per Customer"),
    }
    _defaults={
        "state": "active",
    }

Voucher.register()
