from netforce.model import Model,fields,get_model
from netforce import access
import time

class Route(Model):
    _name="delivery.route"
    _string="Route"
    _name_field="number"
    _fields={
        "number": fields.Char("Number",required=True,search=True),
        "date": fields.Date("Date",required=True,search=True),
        "carrier_id": fields.Many2One("delivery.carrier","Carrier",search=True),
        "lines": fields.One2Many("delivery.route.line","route_id","Destinations"),
        "state": fields.Selection([["planned","Planned"],["transit","In Transit"],["done","Completed"],["canceled","Canceled"]],"Status",required=True),
        "num_lines": fields.Integer("# Items",function="get_num_lines"),
        "ref": fields.Char("Ref"),
        "create_delivery_route_id": fields.Many2One("create.delivery.route","Create Wizard"),
        "depart_time": fields.DateTime("Departure Time"),
        "return_time": fields.DateTime("Return Time"),
    }
    _order="date desc,number desc"

    def _get_number(self, context={}):
        seq_id = get_model("sequence").find_sequence(type="delivery_route",context=context)
        if not seq_id:
            return None
        while 1:
            num = get_model("sequence").get_next_number(seq_id, context=context)
            if not num:
                return None
            user_id = access.get_active_user()
            access.set_active_user(1)
            res = self.search([["number", "=", num]])
            access.set_active_user(user_id)
            if not res:
                return num
            get_model("sequence").increment_number(seq_id, context=context)

    _defaults={
        "state": "planned",
        "date": lambda *a: time.strftime("%Y-%m-%d %H:%M:%S"),
        "number": _get_number,
    }
    
    def get_num_lines(self,ids,context={}):
        vals={}
        for obj in self.browse(ids):
            vals[obj.id]=len(obj.lines)
        return vals

Route.register()
