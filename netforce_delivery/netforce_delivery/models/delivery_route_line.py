from netforce.model import Model,fields,get_model

class RouteLine(Model):
    _name="delivery.route.line"
    _string="Destination"
    _fields={
        "route_id": fields.Many2One("delivery.route","Route",required=True,on_delete="cascade"),
        "sequence": fields.Integer("Sequence",required=True),
        "picking_id": fields.Many2One("stock.picking","Goods Issue",condition=[["type","=","out"]]),
        "contact_id": fields.Many2One("contact","Customer",function="_get_related",function_context={"path":"picking_id.contact_id"}),
        "ship_address_id": fields.Many2One("address","Shipping Address",function="_get_related",function_context={"path":"picking_id.ship_address_id"}),
        "state": fields.Selection([["planned","Planned"],["done","Completed"],["canceled","Canceled"]],"Status",required=True),
        "delivery_slot_id": fields.Many2One("delivery.slot","Delivery Slot"),
    }
    _order="sequence"
    _defaults={
        "state": "planned",
    }

RouteLine.register()
