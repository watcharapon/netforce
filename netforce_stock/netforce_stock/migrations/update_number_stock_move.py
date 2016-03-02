import time

from netforce.model import get_model
from netforce import migration
from netforce.access import set_active_user, set_active_company

class Migration(migration.Migration):
    _name="stock.update.number.stock.move"
    _version="3.1.0"

    def migrate(self):
        set_active_company(1)
        set_active_user(1)
        total_all=0
        total_found=0
        datenow=time.strftime("%Y-%m-%d")
        for move in get_model("stock.move").search_browse([[]]):
            context={
                'date': move.date or datenow,
            }
            number=move.number
            total_all+=1
            if not number:
                number=get_model('stock.move')._get_number(context)
                move.write({
                    'number': number,
                })
        print("="*80)
        print('updated %s of %s item'%(total_found,total_all))
        print("="*80)

Migration.register()
