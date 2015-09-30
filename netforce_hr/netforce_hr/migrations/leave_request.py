from netforce.model import get_model
from netforce import migration

class Migration(migration.Migration):
    _name="hr.leave"
    _version="2.12.0"

    def migrate(self):
        # ./run.py -m 2.11.0
        for leave in get_model('hr.leave').search_browse([]):
            time_from='00:00:00'
            time_to=time_from
            if leave.time_from:
                time_from=leave.time_from
            if leave.time_to:
                time_to=leave.time_to
            leave.write({
                'start_date': '%s %s'%(leave.start_date[0:10],time_from),
                'end_date': '%s %s'%(leave.end_date[0:10],time_to)
            })
        print("Update Leave Request OK!")

Migration.register()

