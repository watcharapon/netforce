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

from netforce.controller import Controller
from netforce.model import get_model,clear_cache,fields
from netforce import database
from netforce import template
from netforce.action import get_action
from netforce.utils import get_data_path,set_data_path
from netforce.database import get_connection,get_active_db
from netforce import config
from netforce import static
from netforce import access
import json
from pprint import pprint
import os
import base64
import urllib
import netforce
import sys
import tempfile
from lxml import etree
import time

def parse_args(handler):
    res={}
    for path in handler.request.arguments:
        for v in handler.get_arguments(path):
            if v=="":
                continue
            set_data_path(res,path,v)
    return res

class Export(Controller): # TODO: cleanup
    _path="/export"

    def get(self):
        db=get_connection()
        if db:
            db.begin()
        try:
            clear_cache()
            ctx={
                "request": self.request,
                "request_handler": self,
                "dbname": get_active_db(),
            }
            data=self.get_cookies()
            if data:
                ctx.update(data)
            action_vals=parse_args(self)
            ctx.update(action_vals)
            name=action_vals.get("name")
            if name:
                action_ctx=action_vals
                action=get_action(name,action_ctx)
                for k,v in action.items():
                    if k not in action_vals:
                        action_vals[k]=v
            if "context" in action_vals:
                ctx.update(action_vals["context"])
            action_vals["context"]=ctx
            self.clear_flash()
            type=action_vals.get("type","view")
            if type=="export":
                print("XXX export")
                model=action_vals["model"]
                m=get_model(model)
                ids=action_vals.get("ids")
                if ids:
                    if ids[0]=="[": # XXX
                        ids=ids[1:-1]
                    ids=[int(x) for x in ids.split(",")]
                else:
                    condition=action_vals.get("condition")
                    if condition:
                        print("condition",condition)
                        condition=json.loads(condition)
                        ids=m.search(condition)
                    else:
                        ids=m.search([]) # XXX
                ctx=action_vals.copy()
                if ctx.get("export_fields"):
                    if isinstance(ctx["export_fields"],str):
                        ctx["export_fields"]=json.loads(ctx["export_fields"])
                else:
                    try:
                        view=get_xml_view(model=model,type="export")
                        doc=etree.fromstring(view["layout"])
                        field_names=[]
                        for el in doc.iterfind(".//field"):
                            name=el.attrib["name"]
                            field_names.append(name)
                        ctx["export_fields"]=field_names
                    except: # default export fields
                        req_field_names=[]
                        other_field_names=[]
                        for n,f in m._fields.items():
                            if isinstance(f,(fields.One2Many,fields.Many2Many)):
                                continue
                            if isinstance(f,fields.Json):
                                continue
                            if not f.store and not f.function:
                                continue
                            if f.required:
                                req_field_names.append(n)
                            else:
                                other_field_names.append(n)
                        ctx["export_fields"]=sorted(req_field_names)+sorted(other_field_names)
                data=m.export_data(ids,context=ctx)
                db=get_connection()
                if db:
                    db.commit()
                filename=action_vals.get("filename","export.csv")
                self.set_header("Content-Disposition","attachment; filename=%s"%filename)
                self.set_header("Content-Type","text/csv")
                self.write(data)
            else:
                raise Exception("Invalid action type: %s"%type)
        except Exception as e:
            import traceback
            traceback.print_exc(file=sys.stdout)
            db=get_connection()
            if db:
                db.rollback()
            raise e

Export.register()
