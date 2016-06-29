from netforce.migration import Migration
from netforce.database import get_connection

class Migration(Migration):
    _name="active.profile"
    _version="3.2.1"

    def migrate(self):
        db=get_connection()
        profiles=db.query("SELECT id, name, active FROM profile")
        for profile in profiles:
            if not profile.active:
                db.execute("UPDATE profile SET active=%s WHERE id=%s","true",profile.id)
                print("set active for profile %s"%profile.name)

Migration.register()
