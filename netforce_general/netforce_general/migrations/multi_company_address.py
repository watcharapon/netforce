from netforce.model import get_model
from netforce.migration import Migration

class Migration(Migration):
    _name="update.company.setting"
    _version="3.2.2"

    def migrate(self):
        companies=get_model("company").search_read([]) 
        if companies:
            companies=sorted(companies, key=lambda c: c['id']) # looking for the first company
            default_company_id=companies[0]['id']
            for addr in get_model("address").search_browse([]):
                company_id=default_company_id
                emp=addr.employee_id
                if emp and emp.company_id:
                    company_id=emp.company_id.id
                addr.write({
                    'company_id': company_id,
                })

Migration.register()
