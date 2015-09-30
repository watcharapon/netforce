from netforce.controller import Controller
from netforce.template import render
from netforce.model import get_model
from netforce.database import get_connection,get_active_db # XXX: move this
from netforce.locale import set_active_locale,get_active_locale
from .cms_base import BaseController

class Coupons(BaseController):
    _path="/ecom_coupons"

    def get(self):
        db=get_connection()
        try:
            user_id=self.get_cookie("user_id",None)
            if user_id:
                user_id = int(user_id)
                user = get_model("base.user").browse(user_id)
                ctx=self.context
                ctx["coupons_available"] = get_model("sale.coupon").search_browse([["contact_id","=",user.contact_id.id],["state","=","available"]])
                ctx["coupons_in_use"] = get_model("sale.coupon").search_browse([["contact_id","=",user.contact_id.id],["state","=","in_use"]])
                ctx["coupons_used"] = get_model("sale.coupon").search_browse([["contact_id","=",user.contact_id.id],["state","=","used"]])
                ctx["coupons_expired"] = get_model("sale.coupon").search_browse([["contact_id","=",user.contact_id.id],["state","=","expired"]])
                content=render("ecom_coupons",ctx)
                ctx["content"]=content
                html=render("cms_layout",ctx)
                self.write(html)
            else:
                self.redirect("cms_login")
            db.commit()
        except:
            import traceback
            traceback.print_exc()
            db.rollback()

Coupons.register()
