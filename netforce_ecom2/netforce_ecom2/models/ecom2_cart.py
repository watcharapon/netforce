from netforce.model import Model,fields,get_model
from netforce import access
from datetime import *
import time
from pprint import pprint
import json

class Cart(Model):
    _name="ecom2.cart"
    _string="Cart"
    _name_field="number"
    _audit_log=True
    _fields={
        "number": fields.Char("Number",required=True,search=True),
        "date": fields.DateTime("Date Created",required=True,search=True),
        "customer_id": fields.Many2One("contact","Customer",search=True),
        "lines": fields.One2Many("ecom2.cart.line","cart_id","Lines"),
        "ship_amount_details": fields.Json("Shipping Amount Details",function="get_ship_amount_details"),
        "amount_ship": fields.Decimal("Shipping Amount",function="get_amount_ship"),
        "amount_total": fields.Decimal("Total Amount",function="get_total"),
        "sale_orders": fields.One2Many("sale.order","related_id","Sales Orders"),
        "delivery_date": fields.Date("Delivery Date"),
        "ship_address_id": fields.Many2One("address","Shipping Address"),
        "bill_address_id": fields.Many2One("address","Billing Address"),
        "delivery_slot_id": fields.Many2One("delivery.slot","Peferred Delivery Slot"),
        "ship_method_id": fields.Many2One("ship.method","Shipping Method"),
        "pay_method_id": fields.Many2One("payment.method","Payment Method"),
        "logs": fields.One2Many("log","related_id","Audit Log"),
        "state": fields.Selection([["draft","Draft"],["confirmed","Confirmed"],["canceled","Canceled"]],"Status",required=True),
        "payment_methods": fields.Json("Payment Methods",function="get_payment_methods"),
        "delivery_delay": fields.Integer("Delivery Delay (Days)",function="get_delivery_delay"),
        "delivery_slots": fields.Json("Delivery Slots",function="get_delivery_slots"),
        "delivery_slots_str": fields.Text("Delivery Slots",function="get_delivery_slots_str"),
        "date_delivery_slots": fields.Json("Date Delivery Slots",function="get_date_delivery_slots"),
        "comments": fields.Text("Comments"),
        "transaction_no": fields.Char("Payment Transaction No.",search=True),
        "currency_id": fields.Many2One("currency","Currency",required=True),
        "invoices": fields.One2Many("account.invoice","related_id","Invoices"),
        "company_id": fields.Many2One("company","Company"),
        "voucher_id": fields.Many2One("sale.voucher","Voucher"),
        "ship_addresses": fields.Json("Shipping Addresses",function="get_ship_addresses"),
        "amount_voucher": fields.Decimal("Voucher Amount",function="get_amount_voucher",function_multi=True),
        "voucher_error_message": fields.Text("Voucher Error Message",function="get_amount_voucher",function_multi=True),
    }
    _order="date desc"

    def _get_number(self, context={}):
        seq_id = get_model("sequence").find_sequence(type="ecom_cart")
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

    def _get_currency(self,context={}):
        res=get_model("company").search([]) # XXX
        if not res:
            return
        company_id=res[0]
        access.set_active_company(company_id)
        settings=get_model("settings").browse(1)
        return settings.currency_id.id

    def _get_company(self,context={}):
        res=get_model("company").search([]) # XXX
        if res:
            return res[0]

    def _get_ship_method(self,context={}):
        res=get_model("ship.method").search([],order="sequence")
        if res:
            return res[0]

    _defaults={
        "date": lambda *a: time.strftime("%Y-%m-%d %H:%M:%S"),
        "number": _get_number,
        "state": "draft",
        "currency_id": _get_currency,
        "company_id": _get_company,
        "ship_method_d": _get_ship_method,
    }

    def get_ship_amount_details(self,ids,context={}):
        print("get_ship_amount_details",ids)
        vals={}
        for obj in self.browse(ids):
            delivs=[]
            for line in obj.lines:
                date=line.delivery_date
                meth_id=line.ship_method_id.id
                addr_id=line.ship_address_id.id or line.cart_id.ship_address_id.id
                if not date or not meth_id or not addr_id:
                    continue
                delivs.append((date,meth_id,addr_id))
            delivs=list(set(delivs))
            details=[]
            for date,meth_id,addr_id in delivs:
                ctx={
                    "ship_address_id": addr_id,
                }
                meth=get_model("ship.method").browse(meth_id,context=ctx)
                details.append({
                    "ship_method_id": meth.id,
                    "ship_amount": meth.ship_amount,
                })
            vals[obj.id]=details
        return vals

    def get_amount_ship(self,ids,context={}):
        print("get_amount_ship",ids)
        vals={}
        for obj in self.browse(ids):
            ship_amt=0
            for d in obj.ship_amount_details:
                ship_amt+=d["ship_amount"] or 0
            vals[obj.id]=ship_amt
        return vals

    def get_total(self,ids,context={}):
        vals={}
        for obj in self.browse(ids):
            amt=0
            for line in obj.lines:
                amt+=line.amount
            vals[obj.id]=amt+obj.amount_ship-obj.amount_voucher
        return vals

    def get_payment_methods(self,ids,context={}):
        res=[]
        for obj in get_model("payment.method").search_browse([]):
            res.append({
                "id": obj.id,
                "name": obj.name,
            })
        return {ids[0]: res}

    def confirm(self,ids,context={}):
        obj=self.browse(ids[0])
        user_id=context.get("user_id") # XX: remove this
        if user_id:
            user_id=int(user_id)
            user=get_model("base.user").browse(user_id)
            if user.contact_id:
                obj.write({"customer_id": user.contact_id.id})
        access.set_active_company(1) # XXX
        vals={
            "contact_id": obj.customer_id.id,
            "ship_address_id": obj.ship_address_id.id,
            "bill_address_id": obj.bill_address_id.id,
            "due_date": obj.delivery_date,
            "lines": [],
            "related_id": "ecom2.cart,%s"%obj.id,
            "delivery_slot_id": obj.delivery_slot_id.id,
            "pay_method_id": obj.pay_method_id.id,
            "other_info": obj.comments,
            "ref": obj.comments, # XXX
        }
        for line in obj.lines:
            prod=line.product_id
            if line.lot_id and line.qty_avail<=0:
                raise Exception("Lot is out of stock (%s)"%prod.name)
            if not prod.locations:
                raise Exception("Can't find location for product %s"%prod.code)
            location_id=prod.locations[0].location_id.id
            line_vals={
                "product_id": prod.id,
                "description": prod.description,
                "qty": line.qty,
                "uom_id": line.uom_id.id,
                "unit_price": line.unit_price,
                "location_id": location_id,
                "lot_id": line.lot_id.id,
                "due_date": line.delivery_date,
                "ship_address_id": line.ship_address_id.id,
            }
            vals["lines"].append(("create",line_vals))
        for ship in obj.ship_amount_details:
            meth_id=ship["ship_method_id"]
            amount=ship["ship_amount"]
            meth=get_model("ship.method").browse(meth_id)
            prod=meth.product_id
            if not prod:
                raise Exception("Missing product in shipping method %s"%meth.name)
            line_vals={
                "product_id": prod.id,
                "description": prod.description,
                "qty": 1,
                "uom_id": prod.uom_id.id,
                "unit_price": amount,
            }
            vals["lines"].append(("create",line_vals))
        sale_id=get_model("sale.order").create(vals)
        sale=get_model("sale.order").browse(sale_id)
        sale.confirm()
        obj.write({"state":"confirmed"})
        obj.trigger("confirm_order")
        return {
            "sale_id": sale_id,
        }

    def cancel_order(self,ids,context={}):
        obj=self.browse(ids[0])
        for sale in obj.sale_orders:
            if sale.state=="voided":
                continue
            for inv in sale.invoices:
                if inv.state!="voided":
                    raise Exception("Can not cancel order %s because there are linked invoices"%sale.number)
            for pick in sale.pickings:
                if pick.state=="voided":
                    continue
                pick.void()
            sale.void()
        for inv in obj.invoices:
            if inv.state!="voided":
                raise Exception("Can not cancel cart %s because there are linked invoices"%obj.number)
        obj.write({"state":"canceled"})

    def payment_received(self,ids,context={}):
        obj=self.browse(ids[0])
        if obj.state!="waiting_payment":
            raise Exception("Cart is not waiting payment")
        res=obj.sale_orders.copy_to_invoice()
        inv_id=res["invoice_id"]
        inv=get_model("account.invoice").browse(inv_id)
        inv.write({"related_id":"ecom2.cart,%s"%obj.id})
        inv.post()
        method=obj.pay_method_id
        if not method:
            raise Exception("Missing payment method in cart %s"%obj.number)
        if not method.account_id:
            raise Exception("Missing account in payment method %s"%method.name)
        transaction_no=context.get("transaction_no")
        pmt_vals={
            "type": "in",
            "pay_type": "invoice",
            "contact_id": inv.contact_id.id,
            "account_id": method.account_id.id,
            "lines": [],
            "company_id": inv.company_id.id,
            "transaction_no": transaction_no,
        }
        line_vals={
            "invoice_id": inv_id,
            "amount": inv.amount_total,
        }
        pmt_vals["lines"].append(("create",line_vals))
        pmt_id=get_model("account.payment").create(pmt_vals,context={"type": "in"})
        get_model("account.payment").post([pmt_id])
        obj.write({"state": "paid"})
        for sale in obj.sale_orders:
            for pick in sale.pickings:
                if pick.state=="pending":
                    pick.approve()

    def to_draft(self,ids,context={}):
        obj=self.browse(ids[0])
        obj.write({"state":"draft"})

    def set_qty(self,ids,prod_id,qty,context={}):
        print("Cart.set_qty",ids,prod_id,qty)
        obj=self.browse(ids[0])
        line_id=None
        for line in obj.lines:
            if line.product_id.id==prod_id and not line.lot_id:
                line_id=line.id
                break
        if line_id:
            if qty==0:
                get_model("ecom2.cart.line").delete([line_id])
            else:
                get_model("ecom2.cart.line").write([line_id],{"qty":qty})
        else:
            if qty!=0:
                get_model("ecom2.cart.line").create({"cart_id": obj.id, "product_id": prod_id, "qty": qty})

    def set_date_qty(self,ids,due_date,prod_id,qty,context={}):
        print("Cart.set_date_qty",ids,due_date,prod_id,qty)
        obj=self.browse(ids[0])
        line_id=None
        for line in obj.lines:
            if line.delivery_date==due_date and line.product_id.id==prod_id and not line.lot_id:
                line_id=line.id
                break
        if line_id:
            if qty==0:
                get_model("ecom2.cart.line").delete([line_id])
            else:
                get_model("ecom2.cart.line").write([line_id],{"qty":qty})
        else:
            if qty!=0:
                ctx={"cart_id":obj.id,"delivery_date":due_date}
                get_model("ecom2.cart.line").create({"cart_id": obj.id, "product_id": prod_id, "qty": qty, "delivery_date": due_date},context=ctx)

    def add_lot(self,ids,prod_id,lot_id,context={}):
        print("Cart.add_lot",ids,prod_id,lot_id)
        obj=self.browse(ids[0])
        line_id=None
        for line in obj.lines:
            if line.product_id.id==prod_id and line.lot_id.id==lot_id:
                line_id=line.id
                break
        if line_id:
            raise Exception("Lot already added to cart")
        get_model("ecom2.cart.line").create({"cart_id": obj.id, "product_id": prod_id, "lot_id": lot_id, "qty": 1})

    def remove_lot(self,ids,prod_id,lot_id,context={}):
        obj=self.browse(ids[0])
        line_id=None
        for line in obj.lines:
            if line.product_id.id==prod_id and line.lot_id.id==lot_id:
                line_id=line.id
                break
        if not line_id:
            raise Exception("Lot not found in cart")
        get_model("ecom2.cart.line").delete([line_id])

    def add_product(self,ids,prod_id,context={}):
        print("Cart.add_product",ids,prod_id)
        obj=self.browse(ids[0])
        exclude_lot_ids=[]
        for line in obj.lines:
            if line.lot_id:
                exclude_lot_ids.append(line.lot_id.id)
        prod=get_model("product").browse(prod_id)
        found_lot_id=None
        for lot in prod.stock_lots:
            if lot.id not in exclude_lot_ids:
                found_lot_id=lot.id
                break
        if found_lot_id:
            get_model("ecom2.cart.line").create({
                "cart_id": obj.id,
                "product_id": prod_id,
                "lot_id": found_lot_id,
                "qty": 1
            })
        else:
            found_line=None
            for line in obj.lines:
                if line.product_id.id==prod_id and not line.lot_id:
                    found_line=line
                    break
            if found_line:
                found_line.write({"qty":found_line.qty+1})
            else:
                get_model("ecom2.cart.line").create({"cart_id": obj.id, "product_id": prod_id, "qty": 1})

    def remove_product(self,ids,prod_id,context={}):
        print("Cart.remove_product",ids,prod_id)
        obj=self.browse(ids[0])
        del_line=None
        max_date=None
        for line in obj.lines:
            if line.product_id.id!=prod_id:
                continue
            lot=line.lot_id
            if lot:
                d=lot.received_date or "1900-01-01"
                if max_date is None or d>max_date:
                    max_date=d
                    del_line=line
            else:
                del_line=line
                break
        if not del_line:
            raise Exception("No cart line found to remove")
        if del_line.qty>1:
            del_line.write({"qty":del_line.qty-1})
        else:
            del_line.delete()

    def get_delivery_delay(self,ids,context={}):
        settings=get_model("ecom2.settings").browse(1)
        vals={}
        for obj in self.browse(ids):
            vals[obj.id]=max(l.delivery_delay for l in obj.lines) if obj.lines else 0
        return vals

    def get_delivery_slots(self,ids,context={}):
        print("get_delivery_slots",ids)
        obj=self.browse(ids[0])
        settings=get_model("ecom2.settings").browse(1)
        max_days=settings.delivery_max_days
        if not max_days:
            return {obj.id:[]}
        min_hours=settings.delivery_min_hours or 0
        d_from=date.today()+timedelta(days=obj.delivery_delay)
        d_to=d_from+timedelta(days=max_days)
        d=d_from
        slots=[]
        for slot in get_model("delivery.slot").search_browse([]):
            slots.append([slot.id,slot.name,slot.time_from])
        slot_num_sales={}
        for sale in get_model("sale.order").search_browse([["date",">=",time.strftime("%Y-%m-%d")]]):
            k=(sale.due_date,sale.delivery_slot_id.id)
            slot_num_sales.setdefault(k,0)
            slot_num_sales[k]+=1
        slot_caps={}
        for cap in get_model("delivery.slot.capacity").search_browse([]):
            k=(cap.slot_id.id,int(cap.weekday))
            slot_caps[k]=cap.capacity
        delivery_weekdays=None
        for line in obj.lines:
            prod=line.product_id
            if prod.delivery_weekdays:
                days=[int(w) for w in prod.delivery_weekdays.split(",")]
                if delivery_weekdays==None:
                    delivery_weekdays=days
                else:
                    delivery_weekdays=[d for d in delivery_weekdays if d in days]
        days=[]
        now=datetime.now()
        while d<=d_to:
            ds=d.strftime("%Y-%m-%d")
            res=get_model("hr.holiday").search([["date","=",ds]])
            if res:
                d+=timedelta(days=1)
                continue
            w=d.weekday()
            if w==6 or delivery_weekdays is not None and w not in delivery_weekdays:
                d+=timedelta(days=1)
                continue
            day_slots=[]
            for slot_id,slot_name,from_time in slots:
                t_from=datetime.strptime(ds+" "+from_time+":00","%Y-%m-%d %H:%M:%S")
                capacity=slot_caps.get((slot_id,w))
                num_sales=slot_num_sales.get((ds,slot_id),0)
                state="avail"
                if t_from<now or (t_from-now).seconds<min_hours*3600:
                    state="full"
                if capacity is not None and num_sales>=capacity:
                    state="full"
                day_slots.append([slot_id,slot_name,state,num_sales,capacity])
            days.append([ds,day_slots])
            d+=timedelta(days=1)
        print("days:")
        pprint(days)
        return {obj.id: days}

    def get_delivery_slots_str(self,ids,context={}):
        vals={}
        for obj in self.browse(ids):
            s=""
            for d,slots in obj.delivery_slots:
                s+="- Date: %s\n"%d
                for slot_id,name,state,num_sales,capacity in slots:
                    s+="    - %s: %s (%s/%s)\n"%(name,state,num_sales,capacity or "-")
            vals[obj.id]=s
        return vals

    def get_date_delivery_slots(self,ids,context={}):
        print("get_date_delivery_slots",ids)
        obj=self.browse(ids[0])
        slots=[]
        for slot in get_model("delivery.slot").search_browse([]):
            slots.append([slot.id,slot.name])
        dates=[]
        for line in obj.lines:
            d=line.delivery_date
            if d:
                dates.append(d)
        dates=list(set(dates))
        date_slots={}
        for d in dates:
            date_slots[d]=slots # TODO: use capacity?
        return {obj.id: date_slots}

    def get_ship_addresses(self,ids,context={}):
        obj=self.browse(ids[0])
        settings=get_model("ecom2.settings").browse(1)
        contact=obj.customer_id
        addrs=[]
        if contact:
            for a in contact.addresses:
                addr_vals={
                    "id": a.id,
                    "name": a.address,
                }
                if obj.ship_method_id: # TODO: handle general case for different shipping methods per order
                    meth_id=obj.ship_method_id.id
                    ctx={"ship_address_id": a.id}
                    meth=get_model("ship.method").browse(meth_id,context=ctx)
                    addr_vals["ship_amount"]=meth.ship_amount
                else:
                    addr_vals["ship_amount"]=0
                addrs.append(addr_vals)
        for a in settings.extra_ship_addresses:
            addr_vals={
                "id": a.id,
                "name": a.company+", "+a.address,
            }
            if obj.ship_method_id:
                meth_id=obj.ship_method_id.id
                ctx={"ship_address_id": a.id}
                meth=get_model("ship.method").browse(meth_id,context=ctx)
                addr_vals["ship_amount"]=meth.ship_amount
            else:
                addr_vals["ship_amount"]=0
            addrs.append(addr_vals)
        return {obj.id: addrs}

    def apply_voucher_code(self,ids,voucher_code,context={}):
        obj=self.browse(ids[0])
        res=get_model("sale.voucher").search([["code","=",voucher_code]])
        if not res:
            raise Exception("Invalid voucher code")
        voucher_id=res[0]
        obj.write({"voucher_id":voucher_id})

    def clear_voucher(self,ids,context={}):
        obj=self.browse(ids[0])
        obj.write({"voucher_id":None})

    def get_amount_voucher(self,ids,context={}):
        print("get_amount_voucher",ids)
        vals={}
        for obj in self.browse(ids):
            voucher=obj.voucher_id
            if voucher:
                ctx={
                    "contact_id": obj.customer_id.id,
                    "amount_total": 0,
                    "products": [],
                }
                for line in obj.lines:
                    ctx["amount_total"]+=line.amount
                    ctx["products"].append({
                        "product_id": line.product_id.id,
                        "unit_price": line.unit_price,
                        "qty": line.qty,
                        "uom_id": line.uom_id.id,
                        "amount": line.amount,
                    })
                ctx["amount_total"]+=obj.amount_ship
                res=voucher.apply_voucher(context=ctx)
                disc_amount=res.get("discount_amount",0)
                error_message=res.get("error_message")
            else:
                disc_amount=0
                error_message=None
            vals[obj.id]={
                "amount_voucher": disc_amount,
                "voucher_error_message": error_message,
            }
        return vals

    def update_date_delivery(self,ids,date,vals,context={}):
        print("cart.update_date_delivery",ids,date,vals)
        obj=self.browse(ids[0])
        for line in obj.lines:
            if line.delivery_date==date:
                line.write(vals)

    def empty_cart(self,ids,context={}):
        obj=self.browse(ids[0])
        obj.write({"lines":[("delete_all",)]})

Cart.register()
