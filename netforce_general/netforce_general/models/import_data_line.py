from netforce.model import Model, fields, get_model
from netforce.utils import get_file_path

class ImportDataLine(Model):
    _name="import.data.line"
    _fields={
        'import_id': fields.Many2One("import.data","Import", required=True, on_delete="cascade"),
        'external': fields.Char("External Field"),
        'field_id': fields.Many2One("import.field","Field"),
        'simple_value': fields.Text("Simple Value"),
    }


ImportDataLine.register()
