from netforce.model import get_model
from netforce import migration
from netforce.access import set_active_user, set_active_company

class Migration(migration.Migration):
    _name="del.duplicate.price.list.item"
    _version="3.1.0"

    def migrate(self):
        set_active_company(1)
        set_active_user(1)
        dp_prod={}
        for pl_item in get_model("price.list.item").search_browse([]):
            prod=pl_item.product_id
            l=pl_item.list_id
            key=(l.id,prod.id, pl_item.price)
            dp_prod.setdefault(key,[])
            dp_prod[key].append(pl_item.id)

        for k, v in dp_prod.items():
            #duplicate price.list.item
            if len(v)>1:
                del_ids=v[1:]
                print("del_ids %s ..."%(del_ids))
                get_model("price.list.item").delete(del_ids)

Migration.register()
