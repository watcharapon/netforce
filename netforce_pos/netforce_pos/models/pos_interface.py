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
from netforce.utils import print_color
from netforce.access import get_active_company


class Interface(Model):
    _name = "pos.interface"
    _store = False

    def download_products(self, shop_id, context={}):
        print_color("download_products shop_id=%s" % shop_id, "yellow")
        shop_id = shop_id or None
        if not shop_id:
            raise Exception('Missing shop')
        shop_id = int(shop_id)
        shop = get_model("pos.shop").browse([shop_id])[0]
        categ_id = shop.categ_id.id

        if not categ_id:
            raise Exception("Missing product category")
        field_names = ["name", "code", "sale_price"]
        products = get_model("product").search_read([["categs.id", "child_of", categ_id]], field_names)
        return products

    def download_product_by_register(self, register_id=None, context={}):
        print_color("download_products shop_id=%s" % register_id, "yellow")
        if not register_id:
            raise Exception('Missing Register')
        register_id = int(register_id)
        register = get_model("pos.register").browse([register_id])[0]
        shop_id = register.shop_id.id

        if not shop_id:
            raise Exception('Missing Shop')
        shop = get_model("pos.shop").browse([shop_id])[0]
        categ_id = shop.categ_id.id
        if not categ_id:
            raise Exception("Missing product category")

        field_names = ["name", "code", "sale_price"]
        products = get_model("product").search_read([["categs.id", "child_of", categ_id]], field_names)
        return products

    def upload_orders(self, orders, context={}):
        setting_obj = get_model("pos.settings")
        setting_ids = setting_obj.search([])
        if not setting_ids:
            raise Exception("Pos Setting not found.")

        # uom=get_model("uom").search_browse([['name','ilike','%Unit%']])
        # if not uom:
            #raise Exception("Unit not found in uom")
        # if not company_id:
            #raise Exception(" company not found.")

        setting = setting_obj.browse(setting_ids)[0]
        ref = setting.sale_ref or 'POS'
        global_account_id = setting.cash_account_id.id

        for order in orders:
            shop_id = order['shop_id']

            if not shop_id:
                raise Exception('Missing shop, ', order)

            shop_id = int(shop_id)
            shop = get_model("pos.shop").browse([shop_id])[0]
            company_id = shop.company_id.id

            if not company_id:
                raise Exception("Missing Company for shop: ", shop.name)

            company_id = None
            if shop.company_id:
                company_id = shop.company_id.id

            shop_account_id = shop.cash_account_id.id or global_account_id
            if not shop_account_id:
                raise Exception("Missing Shop account")

            # warehouse on sale order
            location_id = shop.location_id.id
            if not location_id:
                raise Exception('Missing Location')

            contact_id = order['contact_id']
            if contact_id:
                contact_id = int(contact_id)
            else:
                contact_id = setting.contact_id.id

            print_color("upload_order shop_id=%s contact_id=%s" % (shop_id, contact_id), "yellow")

            is_credit = order.get("is_credit", False)

            vals = {
                "contact_id": contact_id,
                "company_id": company_id,
                "date": order["date"][:10],
                "tax_type": "tax_in",
                "lines": [],
                "state": is_credit and "confirmed" or "done",
                "location_id": location_id,
                "ref": ref,
                "company_id": company_id,
            }

            for line in order["lines"]:
                prod_id = line["product_id"] or None
                name = line['name']
                qty = line['qty'] or 0
                price = line['unit_price'] or 0
                tax_id = None
                if prod_id:
                    prod = get_model("product").browse(prod_id)
                    prod_id = prod.id
                    name = prod.name
                    uom_id = prod.uom_id.id
                    tax_id = prod.sale_tax_id.id
                line_vals = {
                    "product_id": prod_id,
                    "description": name,
                    "qty": qty,
                    "uom_id": uom_id,
                    "unit_price": price,
                    "tax_id": tax_id,
                }
                print("line_vals ", line_vals)

                vals["lines"].append(("create", line_vals))
            print("sale vals", vals)
            sale_id = get_model("sale.order").create(vals)
            sale = get_model("sale.order").browse(sale_id)

            # starting copy sale to picking
            pick_vals = {
                "type": "out",
                'date': sale.date,
                "company_id": company_id,
                "ref": sale.number,
                "related_id": "sale.order,%s" % sale.id,
                "contact_id": sale.contact_id.id,
                "lines": [],
                "state": "draft",
                "company_id": company_id,
            }

            res = get_model("stock.location").search([["type", "=", "customer"]])
            if not res:
                raise Exception("Customer location not found")
            cust_loc_id = res[0]

            wh_loc_id = sale.location_id.id

            if not wh_loc_id:
                res = get_model("stock.location").search([["type", "=", "internal"]])
                if not res:
                    raise Exception("Warehouse not found")
                wh_loc_id = res[0]

            for line in sale.lines:
                prod = line.product_id
                if prod.type not in ("stock", "consumable"):
                    continue
                qty_remain = line.qty - line.qty_delivered
                if qty_remain < 0.001:
                    continue
                # FIXME
                cust_loc_id = line.location_id.id
                if not cust_loc_id:
                    cust_loc_id = location_id
                line_vals = {
                    "product_id": prod.id,
                    "qty": qty_remain,
                    "unit_price": line.unit_price or 0,
                    "uom_id": line.uom_id.id,
                    "location_from_id": wh_loc_id,
                    "location_to_id": cust_loc_id,
                }
                pick_vals["lines"].append(("create", line_vals))

            if pick_vals["lines"]:
                pick_id = get_model("stock.picking").create(pick_vals, context={"pick_type": "out"})
                pick = get_model("stock.picking").browse(pick_id)
                pick.set_done([pick_id])

                print("pick_id", pick_id)

            # starting copy sale to invoice
            # inv_id=sale.copy_to_invoice()["invoice_id"]
            inv_vals = {
                "type": "out",
                "inv_type": "invoice",
                "tax_type": sale.tax_type,
                "ref": sale.number,
                "related_id": "sale.order,%s" % sale.id,
                "contact_id": sale.contact_id.id,
                "currency_id": sale.currency_id.id,
                "company_id": company_id,
                "lines": [],
                "company_id": company_id,
            }
            for line in sale.lines:
                prod = line.product_id
                remain_qty = line.qty - line.qty_invoiced
                if remain_qty < 0.001:
                    print("remain_qty < 0.001")
                    continue
                # XXX Skip Discount
                # if not prod.id:
                    # continue
                line_vals = {
                    "product_id": prod.id,
                    "description": line.description,
                    "qty": remain_qty,
                    "uom_id": line.uom_id.id,
                    "unit_price": line.unit_price,
                    "amount": remain_qty * line.unit_price,
                    #"account_id": prod and prod.sale_account_id.id or shop__account_id, # FIXME find discount account
                    "tax_id": line.tax_id.id,
                }

                if prod.id:
                    line_vals['account_id'] = prod.sale_account_id.id or shop_account_id
                if line.description == "Discount":
                    if not shop.disc_account_id.id:
                        raise Exception("No discount account!")
                    line_vals['account_id'] = shop.disc_account_id.id

                inv_vals["lines"].append(("create", line_vals))
            inv_id = get_model("account.invoice").create(inv_vals, {"type": "out", "inv_type": "invoice"})
            inv = get_model("account.invoice").browse(inv_id)
            inv.write({"due_date": sale.date})  # FIXME should be sale date. Not close register date
            if not is_credit:
                # inv.write({"due_date":inv.date})
                get_model("account.invoice").approve([inv_id])
                # create payment
                vals = {
                    "contact_id": contact_id,
                    "company_id": company_id,
                    "type": "in",
                    "pay_type": "invoice",
                    "date": inv.date,
                    "account_id": shop_account_id,
                    "lines": [("create", {
                        "invoice_id": inv_id,
                        "amount": inv.amount_due or 0,
                    })]
                }
                print("payment vals ", vals)
                pmt_id = get_model("account.payment").create(vals, context={"type": "in"})
                get_model("account.payment").post([pmt_id])
            else:
                inv.write({"state": 'waiting_payment'})

    def download_shop(self, context={}):
        print_color("download_shop", "yellow")
        field_names = ["name", "registers"]
        shops = get_model("pos.shop").search_read([], field_names)
        reg_obj = get_model('pos.register')
        for shop in shops:
            line = []
            for reg in reg_obj.browse(shop['registers']):
                vals = {
                    'id': reg.id,
                    'name': reg.name,
                    "ask_note": reg.ask_note or False,
                    "print_receipt": reg.print_receipt or False,
                    "print_note_receipt": reg.print_note_receipt or False,
                    "show_discount": reg.show_discount or False,
                    "state": reg.state or '',
                }
                line.append(vals)
            shop['registers'] = line
        return shops

    def open_register(self, ids, context={}):
        print_color("Open register", "yellow")
        reg = get_model("pos.register").browse(ids)
        reg.write({"state": "open"})

    def close_register(self, ids, context={}):
        print_color("Close register", "yellow")
        reg = get_model("pos.register").browse(ids)
        reg.write({"state": "close"})

    def download_customer(self, context={}):
        print_color("download_customer", "yellow")
        field_names = ["name"]
        customers = get_model("contact").search_read([], field_names)
        return customers

    def search_customer(self, name, context={}):
        print_color("search_customer", "yellow")
        field_names = []
        res = get_model("contact").search_read([['name', 'ilike', name]], field_names)
        if res:
            contact_id = res[0]['id']
            field_names = ['street', 'sub_district', 'district', 'postal_code', 'city', 'country_id']
            address = get_model("address").search_read([['contact_id', '=', contact_id]], field_names)
            res[0]['address'] = None
            if address:
                res[0]['address'] = address[-1]
        return res

    def create_customer(self, mode, vals, context={}):
        print_color("create_customer", "yellow")
        if mode == 'create':
            new_contact_id = get_model('contact').create(vals)
            return new_contact_id
        elif mode == 'write':
            name = vals['name']
            contact_id = get_model("contact").search_read([['name', '=', name]], [])[0]['id']
            contact = get_model("contact").browse(contact_id)

            add_vals = vals['addresses'][0][1]
            del vals['addresses']

            contact.write(vals)
            address_obj = get_model("address").search_read([['contact_id', '=', contact_id]], [])
            # write exist address
            if address_obj:
                address_id = address_obj[0]['id']
                address = get_model("address").browse(address_id)
                address.write(add_vals)
            else:
                add_vals['contact_id'] = contact_id
                address = get_model("address").create(add_vals)

    def get_company(self, shop, context={}):
        print_color("get_company_profile", "yellow")

        # company_id=get_active_company()
        # if not company_id:
        #raise Exception(" company not found.")

        # FIXME
        shop_name = ''
        if shop and shop.get('shopId', None):
            shop_name = shop.get('shopName', '')
            print("Use address of Shop %s " % (shop_name))
            shop_id = int(shop.get('shopId'))
            address = get_model("pos.shop").get_address_str([shop_id])

        # comp=get_model('company').browse(company_id)
        # settings=get_model("settings").browse(1)
        # address=settings.get_address_str()
        data = {
            'name': shop_name,  # comp.name,
            'address': address,
        }

        return data

    def get_local_sign(self, context={}):
        print_color("get_local_sign", "yellow")
        settings = get_model("settings").browse(1)
        sign = settings.currency_id.sign
        data = {
            'sign': sign or '',
        }
        return data

    def download_country(self, name, context={}):
        print_color("download_country", "yellow")
        field_names = []
        condition = []
        country = get_model("country").search_read(condition, field_names)
        return country

Interface.register()
