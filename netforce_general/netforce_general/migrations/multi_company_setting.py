from netforce.model import get_model
from netforce.database import get_connection
from netforce.access import set_active_company
from netforce.migration import Migration

class Migration(Migration):
    _name="multi.company.setting"
    _version="3.2.0"

    def migrate(self):
        db=get_connection()
        res=db.query("select id from company")
        multi_fields=[
            "lock_date",
            "year_end_day",
            "year_end_month",
            # inventory settings
            "pick_in_journal_id",
            "pick_out_journal_id",
            "pick_internal_journal_id",
            "stock_count_journal_id",
            "landed_cost_journal_id",
            "transform_journal_id",
            "production_journal_id",
            "product_borrow_journal_id",
            "lot_expiry_journal_id",
            "stock_cost_mode",
            "prevent_validate_neg_stock",
            # financial settings
            "sale_journal_id",
            "purchase_journal_id",
            "pay_in_journal_id",
            "pay_out_journal_id",
            "general_journal_id",
            ]
        for r in res:
            company_id=r.id
            set_active_company(company_id)
            res2=db.query("select "+",".join(multi_fields)+" from settings where id=1")
            if res2:
                for f in multi_fields:
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
