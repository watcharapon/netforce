from netforce.model import Model, fields, get_model
from netforce.utils import get_file_path

class ImportDataCol(Model):
    _name="import.data.col"
    _fields={
        'import_id': fields.Many2One("import.data","Import", required=True, on_delete="cascade"),
        'col': fields.Char("Column"),
        'field': fields.Selection([],"Field"),
        'field_id': fields.Many2One("import.field","Field"),
        "model": fields.Char("Model"),
        "file": fields.Char("File"),
    }

    def default_get(self,field_names=None,context={},**kw):
        data=context['data']
        vals={
            'model': data['model'],
            'file': data['file'],
        }
        print('data ', vals)
        return vals

    def get_fields(self, context={}):
        data=context['data']
        model = data["model"]
        m = get_model(model)
        res=[(k, v.string) for k,v in m._fields.items()]
        return res

ImportDataCol.register()
