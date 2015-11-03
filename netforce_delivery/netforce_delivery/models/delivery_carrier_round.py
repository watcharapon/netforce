from netforce.model import Model,fields,get_model

class CarrierRound(Model):
    _name="delivery.carrier.round"
    _string="Carrier Round"
    _fields={
        "carrier_id": fields.Many2One("delivery.carrier","Carrier",required=True,on_delete="cascade"),
        "seq_min": fields.Decimal("Sequence Min",required=True),
        "seq_max": fields.Decimal("Sequence Max",required=True),
        "description": fields.Char("Description",required=True),
    }

CarrierRound.register()
