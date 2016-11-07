from netforce.model import Model, fields

class ImportDataLog(Model):
    _name="import.data.log"
    _fields={
        'import_id': fields.Many2One("import.data","Import", required=True, on_delete="cascade"),
        'sequence': fields.Char("No."),
        'description': fields.Text("Description"),
    }

ImportDataLog.register()
