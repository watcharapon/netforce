from netforce.model import Model,fields,get_model

class Settings(Model):
    _name="ecom2.settings"
    _string="Settings"
    _fields={
        "delivery_slot_discount": fields.Decimal("Same Delivery Slot Discount"),
        "delivery_max_days": fields.Integer("Delivery Max Days"),
        "delivery_min_hours": fields.Integer("Delivery Min Hours"),
        "ecom_num_lots": fields.Integer("Number Of Lots To Show On Website"),
    }

Settings.register()
