from netforce.model import Model,fields,get_model

class Picking(Model):
    _inherit="stock.picking"
    _fields={
        "route_lines": fields.One2Many("delivery.route.line","picking_id","Route Destinations"),
    }

Picking.register()
