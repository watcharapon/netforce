from netforce.model import Model, fields

class StockSettings(Model):
    _inherit="settings"

    _fields={
        "prevent_validate_neg_stock": fields.Boolean("Prevent Validate Negative Stock"),
    }

StockSettings.register()
