from netforce.model import Model,fields,get_model
from datetime import *
import time

class CreateRoute(Model):
    _name="create.delivery.route"
    _fields={
        "date": fields.Date("Date",required=True),
        "routes": fields.One2Many("delivery.route","create_delivery_route_id","Delivery Routes"),
    }

    def _get_date(self,context={}):
        d=datetime.today()+timedelta(days=1)
        w=d.weekday()
        if w==6:
            d+=timedelta(days=1)
        return d.strftime("%Y-%m-%d")

    _defaults={
        "date": _get_date,
    }

    def create_routes(self,ids,context={}):
        obj=self.browse(ids[0])
        rounds={}
        for pick in get_model("stock.picking").search_browse([["type","=","out"],["type","=","approved"],["date",">=",obj.date+" 00:00:00"],["date","<=",obj.date+" 23:59:59"]]):
            if pick.route_lines: # XXX
                continue
            seq=pick.sequence
            if not seq:
                raise Exception("Missing sequence for %s"%pick.number)
            res=get_model("delivery.carrier.round").search([["seq_min","<=",seq],["seq_max",">=",seq]])
            if not res:
                raise Exception("Carrier not found for %s (%s)"%(pick.number,seq))
            if len(res)>2:
                raise Exception("More than 1 carrier for %s (%s)"%(pick.number,seq))
            round_id=res[0]
            rounds.setdefault(round_id,[])
            rounds[round_id].append(pick.id)
        print("rounds",rounds)
        num_routes=0
        for round_id,pick_ids in rounds.items():
            rd=get_model("delivery.carrier.round").browse(round_id)
            route_vals = {
                "date": obj.date,
                "carrier_id": rd.carrier_id.id,
                "ref": rd.description,
                "create_delivery_route_id": obj.id,
                "lines": [],
            }
            for pick in get_model("stock.picking").browse(pick_ids):
                line_vals = {
                    "sequence": pick.sequence,
                    "picking_id": pick.id,
                }
                route_vals["lines"].append(("create", line_vals))
            if not route_vals["lines"]:
                continue
            get_model("delivery.route").create(route_vals)
            num_routes+=1
        return {
            "flash": "%d routes created."%num_routes,
        }

CreateRoute.register()
