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
from netforce.access import get_active_company, get_active_user
from netforce_report import report_render_to_file


class SendWizard(Model):
    _name = "send.wizard"
    _transient = True
    _fields = {
        "print_model": fields.Char("Print Model", required=True),
        "print_id": fields.Integer("Print ID", required=True),
        "template": fields.Char("Template"),
        "template_method": fields.Char("Template Method"),
        "template_format": fields.Char("Template Format"),
        "out_format": fields.Selection([["pdf", "PDF"], ["odt", "ODT"], ["docx", "DOCX"], ["xlsx", "XLSX"]], "Output Format", required=True),
        "custom_template_type": fields.Char("Custom Template Type"),
        "custom_template_id": fields.Many2One("report.template", "Custom Report Template"),
        "email_contact_field": fields.Char("Email Contact Field"),
        "email_template_id": fields.Many2One("email.template", "Email Template"),
    }

    _defaults = {
        "out_format": "pdf",
        "print_model": lambda self, ctx: ctx.get("print_model"),
        "print_id": lambda self, ctx: int(ctx["refer_id"]),
        "template": lambda self, ctx: ctx.get("template"),
        "template_method": lambda self, ctx: ctx.get("template_method"),
        "template_format": lambda self, ctx: ctx.get("template_format"),
        "custom_template_type": lambda self, ctx: ctx.get("custom_template_type"),
        "email_contact_field": lambda self, ctx: ctx.get("email_contact_field"),
    }

    def send(self, ids, context={}):
        obj = self.browse(ids)[0]
        if not obj.email_template_id:
            raise Exception("Missing email template")
        template = None
        if obj.custom_template_id:
            template = obj.custom_template_id.name
            template_format = obj.custom_template_id.format
        elif obj.template:
            template = obj.template
            template_format = obj.template_format
        elif obj.template_method:
            m = get_model(obj.print_model)
            f = getattr(m, obj.template_method, None)
            if not f:
                raise Exception("Invalid method %s of %s" % (obj.template_method, obj.print_model))
            template = f([obj.print_id], context=context)
            template_format = obj.template_format
        report_fname = None
        if template:
            report_fname = report_render_to_file(
                model=obj.print_model, ids=[obj.print_id], template=template, template_format=template_format, out_format=obj.out_format)
        if not obj.email_contact_field:
            raise Exception("Missing email contact field")
        contact = get_model(obj.print_model).browse(obj.print_id)[obj.email_contact_field]
        if not contact:
            raise Exception("Missing contact")
        if not contact.email:
            raise Exception("Missing contact email (%s)" % contact.name)
        user_id = get_active_user()
        user = get_model("base.user").browse(user_id)
        settings = get_model("settings").browse(1)
        pobj = get_model(obj.print_model).browse(obj.print_id)
        attachments = []
        if report_fname:
            attachments.append({
                "file": report_fname,
            })
        data = {
            "user": user,
            "settings": settings,
            "obj": pobj,
            "attachments": attachments,
        }
        email_id = obj.email_template_id.create_email(data, related_id="%s,%d" % (obj.print_model, obj.print_id))
        return {
            "next": {
                "name": "email",
                "mode": "form",
                "active_id": email_id,
            },
        }

SendWizard.register()
