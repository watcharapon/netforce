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

import csv
import xlrd
import tempfile
import os.path
from io import StringIO

from netforce.model import Model, fields, get_model
from netforce.database import get_active_db
from netforce.utils import get_file_path

def excel2csv(ExcelFile):
    x,fname=tempfile.mkstemp()
    path=get_file_path(ExcelFile)
    workbook = xlrd.open_workbook(path)
    SheetName = workbook.sheet_names()[-1] # always first sheet
    worksheet = workbook.sheet_by_name(SheetName)
    with open(fname,'w') as csvfile:
        wr = csv.writer(csvfile, delimiter=',')
        for rownum in range(worksheet.nrows):
            rows=[]
            for x in worksheet.row_values(rownum):
                if isinstance(x, (str)):
                    x.encode("utf-8")
                rows.append(x)	
            wr.writerow(rows)
        #csvfile.close()
    data=open(fname,"r").read()
    os.remove(fname)	
    return data

class Import(Model):
    _name = "import.data"
    _transient = True
    _fields = {
        "model": fields.Char("Model", required=True),
        "next": fields.Char("Next"),
        "title": fields.Char("Title"),
        "file": fields.File("File to import"),
        'col_lines': fields.One2Many("import.data.col","import_id","Col Lines"),
        'log_lines': fields.One2Many("import.data.log","import_id","Log Lines"),
        'state': fields.Selection([['to_verify','To Veriry'],['done','Done']], 'State'),
        'user_id': fields.Many2One("base.user","User"),
    }
    
    def get_default_next(self, context={}):
        return context.get("next")

    def get_default_title(self, context={}):
        model = context["import_model"]
        m = get_model(model)
        title = "Import"
        if m._string:
            title += " " + m._string
        else:
            title += " " + m._name.title()
        return title

    def get_default_model(self, context={}):
        model = context["import_model"]
        return model

    def get_col_lines(self, context={}):
        model = context["import_model"]
        lines=[
            {
                'model': model
            },
        ]
        return lines

    _defaults={
        "model": get_default_model,
        "title": get_default_title,
        "next": get_default_next,
        "col_lines": get_col_lines,
        'state': 'to_verify',
    }

    def onchange_file(self, context={}):
        data=context['data']
        f=data['file']
        suffix=f.split(".")[-1]
        print('suffix ', suffix)
        csv_data=''
        if suffix=='csv':
            path=get_file_path(f)
            csv_data=open(path,"r").read()
        elif suffix in ('xlsx','xls'):
            csv_data=excel2csv(f)
        # check type xlsx or csv
        f = StringIO(csv_data)
        rd = csv.reader(f)
        headers = next(rd)
        headers = [h.strip() for h in headers]
        data['col_lines']=[]
        lines=[]
        for head in headers:
            print('head ', head)
            lines.append({
                'col': head,
                'model': data['model'],
                'file': data['file'],
            })
        data['col_lines']=lines
        return data

    def get_data(self, context={}):
        model = context["import_model"]
        m = get_model(model)
        title = "Import"
        if m._string:
            title += " " + m._string
        return {
            "model": model,
            "title": title,
            "next": context.get("next"),
        }

    def do_import(self, ids, context={}):
        obj = self.browse(ids[0])
        if not obj.file:
            raise Exception("Missing file!")
        dbname = get_active_db()
        data = open(os.path.join("static", "db", dbname, "files", obj.file), "rU", errors="replace").read()
        m = get_model(obj.model)
        m.import_data(data)
        if obj.next:
            return {
                "next": {
                    "name": obj.next,
                },
                "flash": "Data imported successfully",
            }

Import.register()
