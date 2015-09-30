from netforce.model import get_model
from netforce import migration

class Migration(migration.Migration):
    _name="pos.settings"
    _version="1.96.0"

    def migrate(self):
        res=get_model("pos.settings").search([])
        if res:
            return
        get_model("pos.settings").create({})

Migration.register()
