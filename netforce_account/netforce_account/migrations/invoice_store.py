from netforce.model import get_model
from netforce import migration

class Migration(migration.Migration):
    _name="account.invoice.store"
    _version="1.85.0"

    def migrate(self):
        for obj in get_model("account.invoice").search_browse([]):
            obj.function_store()

Migration.register()
