# Copyright (c) 2012-2015 Netforce Co. Ltd.
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
# OR OTHER DEALINGS IN THE SOFTWARE.

from netforce.model import Model, fields, get_model
import time
from netforce import database
from netforce.access import get_active_user, set_active_user
from netforce.access import get_active_company
from pprint import pprint


class Move(Model):
    _name = "stock.move"
    _string = "Stock Movement"
    _name_field = "number"
    _multi_company = True
    _key = ["company_id", "number"]
    _fields = {
        "ref": fields.Char("Ref", search=True),  # XXX: deprecated
        "product_id": fields.Many2One("product", "Product", required=True, search=True),
        "location_from_id": fields.Many2One("stock.location", "From Location", required=True, search=True),
        "location_to_id": fields.Many2One("stock.location", "To Location", required=True, search=True),
        "qty": fields.Decimal("Qty", required=True, scale=6),
        "uom_id": fields.Many2One("uom", "UoM", required=True),
        "picking_id": fields.Many2One("stock.picking", "Picking", on_delete="cascade"),
        "date": fields.DateTime("Date", required=True, search=True),
        "cost_price_cur": fields.Decimal("Cost Price (Cur)",scale=6), # in picking currency
        "cost_price": fields.Decimal("Cost Price", scale=6),  # in company currency
        "unit_price": fields.Decimal("Cost Price", scale=6),  # deprecated  change to cost_price
        "cost_amount": fields.Decimal("Cost Amount"), # in company currency
        "cost_fixed": fields.Boolean("Cost Fixed"), # don't calculate cost
        "state": fields.Selection([("draft", "Draft"), ("pending", "Planned"), ("approved", "Approved"), ("done", "Completed"), ("voided", "Voided")], "Status", required=True),
        "stock_count_id": fields.Many2One("stock.count", "Stock Count"),
        "move_id": fields.Many2One("account.move", "Journal Entry"),
        "user_id": fields.Many2One("base.user", "User"),
        "contact_id": fields.Many2One("contact", "Contact"),
        "comments": fields.One2Many("message", "related_id", "Comments"),
        "serial_no": fields.Char("Serial No.", search=True),  # XXX: deprecated
        "lot_id": fields.Many2One("stock.lot", "Lot / Serial Number"),
        "container_from_id": fields.Many2One("stock.container", "From Container"),
        "container_to_id": fields.Many2One("stock.container", "To Container"),
        "packaging_id": fields.Many2One("stock.packaging", "Packaging"),
        "num_packages": fields.Integer("# Packages"),
        "notes": fields.Text("Notes"),
        "qty2": fields.Decimal("Qty2"),
        "company_id": fields.Many2One("company", "Company"),
        "invoice_id": fields.Many2One("account.invoice", "Invoice"),
        "related_id": fields.Reference([["sale.order", "Sales Order"], ["purchase.order", "Purchase Order"], ["job", "Service Order"], ["account.invoice", "Invoice"], ["pawn.loan", "Loan"]], "Related To"),
        "number": fields.Char("Number", required=True, search=True),
        "journal_id": fields.Many2One("stock.journal", "Journal", required=True, search=True),
        "alloc_costs": fields.One2Many("landed.cost.alloc","move_id","Allocated Costs"),
        "alloc_cost_amount": fields.Decimal("Allocated Costs",scale=6,function="get_alloc_cost_amount"),
        "track_id": fields.Many2One("account.track.categ","Track"),
        "cogs_account_id": fields.Many2One("account.account","COGS Account",function="_get_related",function_context={"path":"product_id.cogs_account_id"},function_search="_search_related",search=True),
    }
    _order = "date desc,id desc"

    def _get_loc_from(self, context={}):
        print("_get_loc_from", context)
        data = context.get("data")
        settings = get_model("settings").browse(1)
        if data:
            journal_id = data.get("journal_id")
            if journal_id:
                journal = get_model("stock.journal").browse(journal_id)
                if journal.location_from_id:
                    return journal.location_from_id.id
        pick_type = context.get("pick_type")
        if pick_type == "in":
            journal = settings.pick_in_journal_id
        elif pick_type == "out":
            journal = settings.pick_out_journal_id
        elif pick_type == "internal":
            journal = settings.pick_internal_journal_id
        else:
            journal = None
        if journal and journal.location_from_id:
            return journal.location_from_id.id
        if pick_type != "in":
            return None
        res = get_model("stock.location").search([["type", "=", "supplier"]],order="id")
        if not res:
            return None
        return res[0]

    def _get_loc_to(self, context={}):
        print("_get_loc_to", context)
        data = context.get("data")
        settings = get_model("settings").browse(1)
        if data:
            journal_id = data.get("journal_id")
            if journal_id:
                journal = get_model("stock.journal").browse(journal_id)
                if journal.location_to_id:
                    return journal.location_to_id.id
        pick_type = context.get("pick_type")
        pick_type = context.get("pick_type")
        if pick_type == "in":
            journal = settings.pick_in_journal_id
        elif pick_type == "out":
            journal = settings.pick_out_journal_id
        elif pick_type == "internal":
            journal = settings.pick_internal_journal_id
        else:
            journal = None
        if journal and journal.location_from_id:
            return journal.location_to_id.id
        if pick_type != "out":
            return None
        res = get_model("stock.location").search([["type", "=", "customer"]])
        if not res:
            return None
        return res[0]

    def _get_number(self, context={}):
        seq_id = get_model("sequence").find_sequence("stock_move",context=context)
        if not seq_id:
            return None
        while 1:
            num = get_model("sequence").get_next_number(seq_id,context=context)
            res = self.search([["number", "=", num]])
            if not res:
                return num
            get_model("sequence").increment_number(seq_id,context=context)

    _defaults = {
        "state": "draft",
        "date": lambda *a: time.strftime("%Y-%m-%d %H:%M:%S"),
        "location_from_id": _get_loc_from,
        "location_to_id": _get_loc_to,
        "cost_price": 0,
        "cost_amount": 0,
        "company_id": lambda *a: get_active_company(),
        "number": _get_number,
    }

    def create(self, vals, context={}):
        pick_id = vals.get("picking_id")
        if pick_id:
            pick = get_model("stock.picking").browse(pick_id)
            vals["date"] = pick.date
            vals["picking_id"] = pick.id
            vals["journal_id"] = pick.journal_id.id
        new_id = super().create(vals, context=context)
        self.function_store([new_id])
        prod_id = vals["product_id"]
        user_id = get_active_user()
        set_active_user(1)
        get_model("product").write([prod_id], {"update_balance": True})
        set_active_user(user_id)
        return new_id

    def write(self, ids, vals, context={}):
        prod_ids = []
        if "qty" in vals or "state" in vals: # XXX: change this
            for obj in self.browse(ids):
                prod_ids.append(obj.product_id.id)
                #if obj.related_id:
                #    obj.related_id.function_store() # XXX: very slow, change this (DON'T UNCOMMENT)
        super().write(ids, vals, context=context)
        prod_id = vals.get("product_id")
        if prod_id:
            prod_ids.append(prod_id)
        self.function_store(ids)
        user_id = get_active_user()
        set_active_user(1)
        get_model("product").write(prod_ids, {"update_balance": True})
        set_active_user(user_id)

    def delete(self, ids, **kw):
        prod_ids = []
        job_ids = []
        for obj in self.browse(ids):
            prod_ids.append(obj.product_id.id)
            if obj.related_id and obj.related_id._model == 'job':
                job_ids.append(obj.related_id.id)
        move_ids=[]
        for obj in self.browse(ids):
            if obj.move_id:
                move_ids.append(obj.move_id.id)
        move_ids=list(set(move_ids))
        for move in get_model("account.move").browse(move_ids):
            move.void()
            move.delete()
        super().delete(ids, **kw)
        user_id = get_active_user()
        set_active_user(1)
        get_model("product").write(prod_ids, {"update_balance": True})
        set_active_user(user_id)
        # update service order cost
        get_model("job").function_store(job_ids)

    def view_stock_transaction(self, ids, context={}):
        obj = self.browse(ids[0])
        next = {}
        if obj.picking_id:
            pick = obj.picking_id
            next=pick.view_picking()['next']
        elif obj.stock_count_id:
            next = {
                "name": "stock_count",
                "mode": "form",
                "active_id": obj.stock_count_id.id,
            }
        elif obj.related_id:
            rel=obj.related_id
            name=rel._model
            action_name=''
            if name=='stock.picking':
                action_name='view_picking'
            elif name=='sale.order':
                action_name='sale'
            elif name=='stock.count':
                action_name='stock_count'
            elif name=='purchase.order':
                action_name='purchase'
            elif name=='account.invoice':
                action_name='view_invoice'
            elif name=='account.payment':
                action_name='payment'
            else:
                pass
            if action_name:
                next={
                    'name': action_name,
                    'mode': 'form',
                    'active_id': rel.id,
                }
        else:
            raise Exception("Invalid stock move")
        return {"next": next}

    def set_done(self,ids,context={}):
        print("stock_move.set_done",ids)
        settings=get_model("settings").browse(1)
        prod_ids=[]
        self.write(ids,{"state":"done"},context=context)
        for obj in self.browse(ids):
            prod=obj.product_id
            pick=obj.picking_id
            prod_ids.append(prod.id)
            vals={}
            if not obj.qty2 and prod.qty2_factor:
                qty2=get_model("uom").convert(obj.qty,obj.uom_id.id,prod.uom_id.id)*prod.qty2_factor
                vals["qty2"]=qty2
            elif prod.require_qty2 and obj.qty2 is None:
                raise Exception("Missing secondary qty for product %s"%prod.code)
            if pick and pick.related_id and not obj.related_id:
                vals["related_id"]="%s,%d"%(pick.related_id._model,pick.related_id.id)
            if pick and not pick.related_id and not obj.related_id:
                vals["related_id"]="%s,%d"%(pick._model,pick.id)
            if obj.location_from_id.type=="view":
                raise Exception("Source location '%s' is a view location"%obj.location_from_id.name)
            if obj.location_to_id.type=="view":
                raise Exception("Destination location '%s' is a view location"%obj.location_to_id.name)
            if prod.require_lot and not obj.lot_id:
                raise Exception("Missing lot for product %s"%prod.code)
            if vals:
                obj.write(vals=vals,context=context)
            # change state in borrow requests # XXX: remove this
            if not obj.related_id:
                if pick.related_id._model=="product.borrow":
                    if pick.related_id.is_return_item:
                        pick.related_id.write({"state": "done"})
            elif obj.related_id._model=="product.borrow":
                if obj.related_id.is_return_item:
                    obj.related_id.write({"state": "done"})
        prod_ids=list(set(prod_ids))
        if prod_ids and settings.stock_cost_auto_compute:
            get_model("stock.compute.cost").compute_cost([],context={"product_ids": prod_ids})
        if settings.stock_cost_mode=="perpetual" and not context.get("no_post"):
            self.post(ids,context=context)
        self.update_lots(ids,context=context)
        self.set_reference(ids,context=context)
        self.check_periods(ids,context=context)
        print("<<<  stock_move.set_done")

    def check_periods(self,ids,context={}):
        for obj in self.browse(ids):
            d=obj.date[:10]
            res=get_model("stock.period").search([["date_from","<=",d],["date_to",">=",d],["state","=","posted"]])
            if res:
                raise Exception("Failed to validate stock movement because stock period already posted")

    def set_reference(self,ids,context={}):
        for obj in self.browse(ids):
            if obj.ref or not obj.related_id:
                continue
            ref=obj.related_id.name_get()[0][1]
            obj.write({"ref":ref})

    def reverse(self,ids,context={}):
        move_ids=[]
        for obj in self.browse(ids):
            if obj.state!="done":
                raise Exception("Failed to reverse stock movement: invalid state")
            vals={
                "journal_id": obj.journal_id.id,
                "product_id": obj.product_id.id,
                "qty": obj.qty,
                "uom_id": obj.uom_id.id,
                "location_from_id": obj.location_to_id.id,
                "location_to_id": obj.location_from_id.id,
                "cost_price_cur": obj.cost_price_cur,
                "cost_price": obj.cost_price,
                "cost_amount": obj.cost_amount,
                "qty2": obj.qty2,
                "ref": "Reverse: %s"%obj.ref if obj.ref else None,
                "related_id": "%s,%s"%(obj.related_id._model,obj.related_id.id) if obj.related_id else None,
                "picking_id": obj.picking_id.id,
            }
            move_id=self.create(vals)
            move_ids.append(move_id)
        self.set_done(move_ids)

    def get_alloc_cost_amount(self,ids,context={}):
        vals={}
        for obj in self.browse(ids):
            amt=0
            for alloc in obj.alloc_costs:
                if alloc.landed_id.state!="posted":
                    continue
                amt+=alloc.amount or 0
            vals[obj.id]=amt
        return vals

    def post(self,ids,context={}):
        print("StockMove.post",ids)
        accounts={}
        post_date=None
        move=None
        pick_ids=[]
        n=0
        for move in self.browse(ids):
            n+=1
            print("post stock move %d/%d"%(n,len(ids)))
            if move.move_id:
                raise Exception("Journal entry already create for stock movement %s"%move.number)
            date=move.date[:10]
            if post_date is None:
                post_date=date
            else:
                if date!=post_date:
                    raise Exception("Failed to post stock movements because they have different dates")
            prod=move.product_id
            #desc="[%s] %s @ %s %s "%(prod.code,prod.name,round(move.qty,2),move.uom_id.name) # XXX: too many lines in JE
            desc="Inventory costing"
            acc_from_id=move.location_from_id.account_id.id
            if move.location_from_id.type=="customer":
                if prod.cogs_account_id:
                    acc_from_id=prod.cogs_account_id.id
                elif prod.categ_id and prod.categ_id.cogs_account_id:
                    acc_from_id=prod.categ_id.cogs_account_id.id
            elif move.location_from_id.type=="internal":
                if prod.stock_account_id:
                    acc_from_id=prod.stock_account_id.id
                elif prod.categ_id and prod.categ_id.stock_account_id:
                    acc_from_id=prod.categ_id.stock_account_id.id
            if not acc_from_id:
                raise Exception("Missing input account for stock movement %s (date=%s, ref=%s, product=%s)"%(move.id,move.date,move.ref,prod.name))
            acc_to_id=move.location_to_id.account_id.id
            if move.location_to_id.type=="customer":
                if prod.cogs_account_id:
                    acc_to_id=prod.cogs_account_id.id
                elif prod.categ_id and prod.categ_id.cogs_account_id:
                    acc_to_id=prod.categ_id.cogs_account_id.id
            elif move.location_to_id.type=="internal":
                if prod.stock_account_id:
                    acc_to_id=prod.stock_account_id.id
                elif prod.categ_id and prod.categ_id.stock_account_id:
                    acc_to_id=prod.categ_id.stock_account_id.id
            if not acc_to_id:
                raise Exception("Missing output account for stock movement %s (date=%s, ref=%s, product=%s)"%(move.id,move.date,move.ref,prod.name))
            track_from_id=move.location_from_id.track_id.id
            track_to_id=move.track_id.id or move.location_to_id.track_id.id # XXX
            amt=move.cost_amount or 0
            if move.qty: # XXX: avoid create double journal entry for LC
                accounts.setdefault((acc_from_id,track_from_id,desc),0)
                accounts.setdefault((acc_to_id,track_to_id,desc),0)
                accounts[(acc_from_id,track_from_id,desc)]-=amt
                accounts[(acc_to_id,track_to_id,desc)]+=amt
            if move.picking_id:
                pick_ids.append(move.picking_id.id)
        lines=[]
        for (acc_id,track_id,desc),amt in accounts.items():
            lines.append({
                "description": desc,
                "account_id": acc_id,
                "track_id": track_id,
                "debit": amt>0 and amt or 0,
                "credit": amt<0 and -amt or 0,
            })
        vals={
            "narration": "Inventory costing",
            "date": post_date,
            "lines": [("create",vals) for vals in lines],
        }
        if move and move.related_id:
            vals['related_id']='%s,%s'%(move.related_id._model,move.related_id.id)
        pick_ids=list(set(pick_ids))
        if len(pick_ids)==1:
            vals["related_id"]="stock.picking,%s"%pick_ids[0]
        # sequence number should correspond date
        if move:
            context.update({
                'date': move.date,
            })
        pprint(vals)
        print("creating draft cost journal entry (%d lines)..."%len(lines))
        move_id=get_model("account.move").create(vals,context=context)
        print("post cost journal entry")
        get_model("account.move").post([move_id])
        print(">> finished post cost journal entry")
        get_model("stock.move").write(ids,{"move_id":move_id})
        return move_id

    def to_draft(self,ids,context={}):
        move_ids=[]
        for obj in self.browse(ids):
            if obj.move_id:
                move_ids.append(obj.move_id.id)
        move_ids=list(set(move_ids))
        for move in get_model("account.move").browse(move_ids):
            move.void()
            move.delete()
        self.write(ids,{"state":"draft"})
        # change state in borrow requests
        for obj in self.browse(ids):
            if obj.related_id._model=="product.borrow":
               if not obj.related_id.is_return_item:
                    obj.related_id.write({"state": "approved"})

    def update_lots(self,ids,context={}):
        for obj in self.browse(ids):
            lot=obj.lot_id
            if not lot:
                continue
            if obj.location_from_id.type!="internal" and obj.location_to_id.type=="internal":
                lot.write({"received_date": obj.date})

    # XXX
    def get_unit_price(self,ids,context={}):
        settings=get_model("settings").browse(1)
        vals={}
        for obj in self.browse(ids):
            pick=obj.picking_id
            if pick:
                if pick.currency_rate:
                    currency_rate = pick.currency_rate
                else:
                    if pick.currency_id.id == settings.currency_id.id:
                        currency_rate = 1
                    else:
                        rate_from = pick.currency_id.get_rate(date=pick.date)
                        if not rate_from:
                            raise Exception("Missing currency rate for %s" % pick.currency_id.code)
                        rate_to = settings.currency_id.get_rate(date=pick.date)
                        if not rate_to:
                            raise Exception("Missing currency rate for %s" % settings.currency_id.code)
                        currency_rate = rate_from / rate_to
                price=obj.unit_price_cur or 0
                price_conv=get_model("currency").convert(price,pick.currency_id.id,settings.currency_id.id,rate=currency_rate)
            else:
                price_conv=None
            vals[obj.id]=price_conv
        return vals

Move.register()
