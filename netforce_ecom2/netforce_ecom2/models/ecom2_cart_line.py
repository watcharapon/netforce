from netforce.model import Model,fields,get_model
import time

class CartLine(Model):
    _name="ecom2.cart.line"
    _string="Cart Line"
    _fields={
        "cart_id": fields.Many2One("ecom2.cart","Cart",required=True,on_delete="cascade"),
        "product_id": fields.Many2One("product","Product",required=True),
        "lot_id": fields.Many2One("stock.lot","Lot / Serial Number"),
        "weight": fields.Decimal("Weight",function="_get_related",function_context={"path": "lot_id.weight"}),
        "unit_price": fields.Decimal("Unit Price",required=True),
        "qty": fields.Decimal("Qty",required=True),
        "uom_id": fields.Many2One("uom","UoM",required=True),
        "amount": fields.Decimal("Amount",function="get_amount"),
        "deliver_date": fields.Date("Delivery Date"),
        "ship_address_id": fields.Many2One("address","Shipping Address"),
        "deliver_slot_id": fields.Many2One("delivery.slot","Peferred Delivery Slot"),
    }

    def get_amount(self,ids,context={}):
        vals={}
        for obj in self.browse(ids):
            vals[obj.id]=obj.unit_price*obj.qty
        return vals

    def create(self,vals,*args,**kw):
        prod_id=vals["product_id"]
        prod=get_model("product").browse(prod_id)
        vals["uom_id"]=prod.uom_id.id
        vals["unit_price"]=prod.sale_price
        return super().create(vals,*args,**kw)

CartLine.register()
