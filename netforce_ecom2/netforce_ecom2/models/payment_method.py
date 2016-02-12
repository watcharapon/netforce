from netforce.model import Model,fields,get_model
from netforce import database
from netforce.logger import audit_log

class PaymentMethod(Model):
    _inherit="payment.method"

    def payment_received(self,context={}):
        res=super().payment_received(context=context)
        if res:
            return res
        transaction_no=context.get("transaction_no")
        audit_log("Payment received: transaction_no=%s"%transaction_no)
        amount=context.get("amount")
        currency_id=context.get("currency_id")
        pay_type=context.get("type")
        res=get_model("ecom2.cart").search([["transaction_no","=",transaction_no]])
        if not res:
            print("Cart not found for transaction_no=%s"%transaction_no)
            return
        cart_id=res[0]
        print("Found cart %d for transaction_no=%s"%(cart_id,transaction_no))
        cart=get_model("ecom2.cart").browse(cart_id)
        if cart.state=="waiting_payment":
            if currency_id and currency_id!=cart.currency_id.id:
                raise Exception("Received cart payment in wrong currency (pmt: %s, cart: %s)"%(currency_id,cart.currency_id.id))
            method=cart.pay_method_id
            if not method:
                raise Exception("Missing cart payment method")
            if method.type!=pay_type:
                raise Exception("Received cart payment with wrong method (pmt: %s, cart: %s)"%(pay_type,method.type))
            audit_log("Creating payment for cart %s: transaction_no=%s"%(cart.number,transaction_no))
            cart.payment_received()
        return {
            "next_url": "/ui#name=ecom2_cart&mode=form&active_id=%d"%cart_id,
        }

    def payment_pending(self,context={}):
        res=super().payment_pending(context=context)
        if res:
            return res
        transaction_no=context.get("transaction_no")
        res=get_model("ecom2.cart").search([["transaction_no","=",transaction_no]])
        if not res:
            return
        cart_id=res[0]
        return {
            "next_url": "/ui#name=ecom2_cart&mode=form&active_id=%d"%cart_id,
        }

    def payment_error(self,context={}):
        res=super().payment_error(context=context)
        if res:
            return res
        transaction_no=context.get("transaction_no")
        res=get_model("ecom2.cart").search([["transaction_no","=",transaction_no]])
        if not res:
            return
        cart_id=res[0]
        return {
            "next_url": "/ui#name=ecom2_cart&mode=form&active_id=%d"%cart_id,
        }

PaymentMethod.register()
