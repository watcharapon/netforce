import time

from netforce.model import get_model
from netforce import migration
from netforce.access import set_active_user, set_active_company

class Migration(migration.Migration):
    _name="update.duplicate.number.stock.move"
    _version="3.1.0"

    def migrate(self):
        set_active_company(1)
        set_active_user(1)
        moves={}
        for move in get_model("stock.move").search_browse([[]]):
            moves.setdefault(move.number,[])
            moves[move.number].append(move.id)

        count=0
        for number, ids in moves.items():
            if len(ids) > 1:
                count+=1
                for index, id in enumerate(ids):
                    if index > 0:
                        move=get_model("stock.move").browse(id)
                        move.write({
                            'number': "%s.%s"%(number, index),
                        })
        print('total duplicate ', count)
        print("//"*20)

Migration.register()
