from netforce.model import Model, fields, get_model, clear_cache
from netforce.database import get_connection


class ServiceResourceAllocDepend(Model):
    _name = "service.resource.alloc.depend"
    _string = "Service Resource Alloc Dependency"
    _name_field="resource_alloc_id"

    _fields = {
        "resource_alloc_id": fields.Many2One("service.resource.alloc","Service Resource Alloc",required=True,on_delete="cascade"),
        "prev_resource_alloc_id": fields.Many2One("service.resource.alloc","Previous Service Resource Alloc",required=True),
        "delay": fields.Integer("Delay (Days)"),
    }
    _order = "id"

ServiceResourceAllocDepend.register()
