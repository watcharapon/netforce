from netforce.model import get_model
from netforce.database import get_connection
from netforce.access import set_active_company
from netforce.migration import Migration

class Migration(Migration):
    _name="multi.lock.date"
    _version="3.2.2"

    def migrate(self):
        db=get_connection()

        res=db.query("select id from company")
        for r in res:
            company_id=r.id
            set_active_company(company_id)
            res2=db.query("select lock_date from settings where id=1")
            if res2:
                f = "lock_date"
                res3=db.query("select id from field_value where model='settings' and field=%s and company_id=%s",f, company_id)
                if not res3:
                    get_model("field.value").create({
                        'model': "settings",
                        'company_id': company_id,
                        'field': f,
                        'record_id': 1,
                        'value': res2[0][f],
                    })

Migration.register()
