from netforce.model import get_model
from netforce import migration
#from netforce.database import get_connection

class Migration(migration.Migration):
    _name="job.template"
    _version="3.1.3"

    def migrate(self):
        for obj in get_model("job.template").search_browse([[]]):
            print("Migrate Job Template %s"%obj.name)
            for line in obj.lines:
                if line.unit_price:
                    continue
                line.write({"unit_price": obj.product_id.sale_price or 1})

Migration.register()
