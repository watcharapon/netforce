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

from netforce.model import Model, fields


class Website(Model):
    _name = "website"
    _string = "Website"
    _fields = {
        "name": fields.Char("Website Title"),
        "parent_categ_id": fields.Many2One("product.categ", "Product Category"),
        "parent_group_id": fields.Many2One("product.group", "Product Group"),
        "contact_categ_id": fields.Many2One("contact.categ", "Customer Contact Category"),
        "user_profile_id": fields.Many2One("profile", "Customer User Profile"),
        "sale_account_id": fields.Many2One("account.account", "Sales Account"),
        "sale_tax_id": fields.Many2One("account.tax.rate", "Sales Tax"),
        "account_receivable_id": fields.Many2One("account.account", "Receivable Account"),
        "news_categ_id": fields.Many2One("contact.categ", "Newsletter Contact Category"),
        "target_list_id": fields.Many2One("mkt.target.list", "Newsletter Target List"),
        "invoice_flag": fields.Boolean("Use same invoice number as sale order number"),
        "ship_product_id": fields.Many2One("product", "Shipping Product"),
        "preview_doc_categ_id": fields.Many2One("document.categ", "Preview picture document category"),
        "invoice_template_id": fields.Many2One("report.template", "Invoice Template"),
        "payment_slip_template_id": fields.Many2One("report.template", "Payment Slip Template"),
        "auto_create_account": fields.Boolean("Auto-create customer account after checkout"),
        "ga_script": fields.Text("Google Analytic script"),
        "state": fields.Selection([["active", "Active"], ["inactive", "Inactive"]], "Status", required=True),
        "theme_id": fields.Many2One("theme", "Theme"),
        "settings": fields.One2Many("website.setting","website_id","Website Settings"),
        "sale_channel_id": fields.Many2One("sale.channel","Sales Channel"),
        "bank_method_id": fields.Many2One("payment.method","Bank Transfer",condition=[["type","=","bank"]]),
        "paypal_method_id": fields.Many2One("payment.method","Paypal",condition=[["type","=","paypal"]]),
        "paysbuy_method_id": fields.Many2One("payment.method","Paysbuy",condition=[["type","=","paysbuy"]]),
        "scb_method_id": fields.Many2One("payment.method","SCB Gateway",condition=[["type","=","scb_gateway"]]),
        "url": fields.Char("Website URL"),
    }
    _order="name"
    _defaults = {
        "state": "active",
    }

Website.register()
