from netforce.model import Model, fields

class ImportField(Model):
    _name="import.field"
    _fields={
        'name': fields.Char("Name", required=True),
        'model': fields.Char("Model", required=True),
    }

ImportField.register()
