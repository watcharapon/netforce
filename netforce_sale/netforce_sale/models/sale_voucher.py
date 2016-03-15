from netforce.model import Model,fields,get_model

class Voucher(Model):
    _name="sale.voucher"
    _string="Voucher"
    _name_field="code"
    _fields={
        "code": fields.Char("Voucher Code",required=True,search=True),
        "benefit_type": fields.Selection([["fixed_discount_order","Fixed Discount On Order"],["free_product","Free Product"],["percent_discount_product","Percent Discount On Product"],["credit","Credits"]],"Benefit For Customer",required=True),
        "refer_benefit_type": fields.Selection([["credit","Credits"]],"Benefit For Referring Customer"),
        "discount_amount": fields.Decimal("Discount Amount"),
        "discount_percent": fields.Decimal("Discount Percent"),
        "discount_product_groups": fields.Many2Many("product.group","Discount Product Groups",reltable="m2m_voucher_discount_product_groups",relfield="voucher_id",relfield_other="product_group_id"),
        "discount_max_qty": fields.Integer("Discount Max Qty"),
        "credit_amount": fields.Decimal("Credit Amount"),
        "refer_credit_amount": fields.Decimal("Credit Amount For Referring Customer"),
        "min_order_amount": fields.Decimal("Min Order Amount"),
        "carts": fields.One2Many("ecom2.cart","voucher_id","Carts"),
        "state": fields.Selection([["active","Active"],["inactive","Inactive"]],"Status",required=True),
        "max_orders_per_customer": fields.Integer("Max Orders Per Customer"),
        "new_customer": fields.Boolean("New Customers Only"),
        "contact_groups": fields.Many2Many("contact.group","Customer Groups"),
        "product_groups": fields.Many2Many("product.group","Product Groups"),
        "min_qty": fields.Decimal("Min Qty"),
        "customer_id": fields.Many2One("contact","Customer"),
        "description": fields.Text("Description"),
        "expire_date": fields.Date("Expiration Date"),
    }
    _defaults={
        "state": "active",
    }

Voucher.register()
