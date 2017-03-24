from netforce.model import get_model
from netforce import migration

class Migration(migration.Migration):
    _name="sale.lead.store"
    _version="1.9.0"

    def migrate(self):
        for obj in get_model("sale.lead").search_browse([]):
            obj.function_store()

Migration.register()
