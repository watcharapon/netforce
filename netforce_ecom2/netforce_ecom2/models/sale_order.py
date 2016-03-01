from netforce.model import Model,fields,get_model

class SaleOrder(Model):
    _inherit="sale.order"
    _fields={
        "ecom_state": fields.Selection([["wait_payment","Waiting Payment"],["wait_ship","Waiting Shipment"],["wait_delivery","Waiting Delivery"],["done","Finished"]],"Ecommerce Frontend Status",function="get_ecom_state"),
    }

    def get_ecom_state(self,ids,context={}):
        vals={}
        for obj in self.browse(ids):
            if not obj.is_paid:
                state="wait_payment"
            else:
                ship_states={}
                for pick in obj.pickings:
                    ship_states.setdefault(pick.ship_state,[]).append(pick.id)
                if None in ship_states or "wait_pick" in ship_states:
                    state="wait_ship"
                elif "in_transit" in ship_states:
                    state="wait_delivery"
                else:
                    state="done"
            vals[obj.id]=state
        return vals

SaleOrder.register()
