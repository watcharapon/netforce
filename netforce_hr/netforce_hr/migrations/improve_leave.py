from netforce.model import get_model
from netforce import migration
from netforce.access import set_active_user, get_active_user

class Migration(migration.Migration):
    _name="improve.leave"
    _version="2.10.0"

    def migrate(self):
        user_id=get_active_user()
        set_active_user(1)
        for leave in get_model("hr.leave").search_browse([]):
            if leave.time_from and leave.time_to:
                leave.write({
                    'start_date': '%s %s:00'%(leave.start_date[0:10],leave.time_from.replace(".",":")),
                    'end_date': '%s %s:00'%(leave.end_date[0:10],leave.time_to.replace(".",":")),
                })
        set_active_user(user_id)

Migration.register()

