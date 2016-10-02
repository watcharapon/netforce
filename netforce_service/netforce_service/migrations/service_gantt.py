from netforce.model import get_model
from netforce import migration

class Migration(migration.Migration):
    _name="service.gantt"
    _version="3.1.1"

    def migrate(self):
        src_alloc_ids=get_model("service.resource.alloc").search([])
        get_model("service.resource.alloc").write(src_alloc_ids, {'duration': 0})
        #get_model("service.resource.alloc").function_store(src_alloc_ids)

Migration.register()
