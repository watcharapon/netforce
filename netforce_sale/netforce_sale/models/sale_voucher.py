from netforce.model import Model,fields,get_model
import time

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
        "state": fields.Selection([["active","Active"],["inactive","Inactive"]],"Status",required=True),
        "max_orders_per_customer": fields.Integer("Max Orders Per Customer"),
        "new_customer": fields.Boolean("New Customers Only"),
        "contact_groups": fields.Many2Many("contact.group","Customer Groups"),
        "product_groups": fields.Many2Many("product.group","Product Groups"),
        "min_qty": fields.Decimal("Min Qty"),
        "customer_id": fields.Many2One("contact","Customer"),
        "description": fields.Text("Description"),
        "expire_date": fields.Date("Expiration Date"),
        "carts": fields.One2Many("ecom2.cart","voucher_id","Carts"),
        "sale_orders": fields.One2Many("sale.order","voucher_id","Sales Orders"),
        "product_id": fields.Many2One("product","Configuration Product",required=True),
    }
    _defaults={
        "state": "active",
    }

    def apply_voucher(self,ids,context={}):
        print("$"*80)
        print("voucher.apply_coupon",ids)
        obj=self.browse(ids[0])
        contact_id=context.get("contact_id")
        print("contact_id",contact_id)
        amount_total=context.get("amount_total")
        print("amount_total",amount_total)
        products=context.get("products")
        print("products",products)
        date=time.strftime("%Y-%m-%d")
        try:
            if obj.expire_date and date>obj.expire_date:
                raise Exception("This voucher is expired.")
            if obj.contact_id and contact_id!=obj.contact_id.id:
                raise Exception("This voucher can not apply to this customer.")
            if obj.min_order_amount and (amount_total is None or amount_total<obj.min_order_amount):
                raise Exception("Order total is insufficient to use this voucher.")
            if obj.new_customer:
                res=get_model("sale.order").search([["contact_id","=",contact_id]])
                if res:
                    raise Exception("This voucher can only be used by new customers.")
            if obj.max_orders_per_customer:
                res=get_model("sale.order").search([["contact_id","=",contact_id],["voucher_id","=",obj.id]])
                if len(res)>=obj.max_orders_per_customer:
                    raise Exception("The maximum usage limit has been reached for this voucher")
            disc_amt=0
            if obj.benefit_type=="fixed_discount_order":
                disc_amt=obj.discount_amount
            return {
                "discount_amount": disc_amt,
            }
        except Exception as e:
            return {
                "discount_amount": 0,
                "error_message": str(e),
            }

Voucher.register()
