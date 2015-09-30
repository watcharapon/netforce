from netforce.model import Model,fields,get_model

class RouteLine(Model):
    _name="delivery.route.line"
    _string="Destination"
    _fields={
        "route_id": fields.Many2One("delivery.route","Route",required=True,on_delete="cascade"),
        "sequence": fields.Integer("Sequence",required=True),
        "contact_id": fields.Many2One("contact","Customer",required=True),
        "phone": fields.Char("Phone"),
        "address": fields.Text("Address"),
        "coordinates": fields.Char("Coordinates"),
        "payment_type": fields.Selection([["transfer","Transfer"],["cod","Cash on Delivery"]],"Payment Type"),
        "items_description": fields.Text("Items To Deliver"),
        "state": fields.Selection([["planned","Planned"],["done","Completed"],["canceled","Canceled"]],"Status",required=True),
    }
    _order="sequence"
    _defaults={
        "state": "planned",
    }

RouteLine.register()
