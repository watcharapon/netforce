from netforce.model import Model,fields,get_model

class Carrier(Model):
    _name="delivery.carrier"
    _string="Carrier"
    _fields={
        "code": fields.Char("Code",required=True,search=True),
        "name": fields.Char("Name",required=True,search=True),
        "routes": fields.One2Many("delivery.route","carrier_id","Routes"),
        "rounds": fields.One2Many("delivery.carrier.round","carrier_id","Rounds"),
    }

Carrier.register()
