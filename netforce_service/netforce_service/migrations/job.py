from netforce.model import get_model
from netforce import migration

class Migration(migration.Migration):
    _name="job"
    _version="3.1.1"

    def migrate(self):
        job_ids = []
        for obj in get_model("job").search_browse([[]]):
            job_ids.append(obj.id)
        get_model("job").function_store(job_ids)

Migration.register()
