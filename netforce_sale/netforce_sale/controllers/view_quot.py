from netforce.controller import Controller
from netforce import database
from netforce.model import get_model,clear_cache
from netforce.template import get_template

class ViewQuot(Controller):
    _path="/view_quot"

    def get(self):
        dbname=self.get_argument("dbname")
        uuid=self.get_argument("uuid")
        db=database.connect(dbname)
        clear_cache()
        try:
            res=get_model("sale.quot").search([["uuid","=",uuid]])
            if not res:
                raise Exception("Invalid UUID")
            quot_id=res[0]
            quot=get_model("sale.quot").browse(quot_id)
            comp=get_model("company").browse(1)
            data={
                "logo": comp.logo,
                "state": quot.state,
                "partner_name": quot.partner_id.name,
                "number": quot.number,
                "exp_date": quot.exp_date,
                "user_name": quot.user_id.name,
                "comments": [],
            }
            if quot.documents:
                doc=quot.documents[0]
                fname=doc.file
            else:
                fname=None
            data["file"]=fname
            for msg in quot.comments:
                vals={
                    "date": msg.date,
                    "body": msg.body,
                }
                data["comments"].append(vals)
            data["num_comments"]=len(data["comments"])
            tmpl=get_template("view_quot")
            html=tmpl.render(data)
            self.write(html)
            db.commit()
        except Exception as e:
            db.rollback()
            import traceback
            traceback.print_exc()

    def post(self):
        dbname=self.get_argument("dbname")
        uuid=self.get_argument("uuid")
        submit=self.get_argument("submit")
        db=database.connect(dbname)
        clear_cache()
        try:
            res=get_model("sale.quot").search([["uuid","=",uuid]])
            if not res:
                raise Exception("Invalid UUID")
            quot_id=res[0]
            quot=get_model("sale.quot").browse(quot_id)
            if submit=="accept":
                quot.write({"state":"won"})
            elif submit=="reject":
                quot.write({"state":"lost"})
            elif submit=="send":
                vals={"related_id":"sale.quot,%s"%quot_id,"body": self.get_argument("message"),"from_id":1}
                get_model("message").create(vals)
            self.redirect("/view_quot?dbname=%s&uuid=%s"%(dbname,uuid))
            db.commit()
        except Exception as e:
            db.rollback()
            import traceback
            traceback.print_exc()
        

ViewQuot.register()
