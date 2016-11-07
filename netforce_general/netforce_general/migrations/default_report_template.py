
from netforce.model import get_model
from netforce import migration


class Migration(migration.Migration):
    _name="default.report.template"
    _version="3.1.0"

    def migrate(self):
        get_model("report.template").get_default_template()


Migration.register()
