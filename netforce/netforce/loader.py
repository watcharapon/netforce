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

import pkg_resources
import os
from lxml import etree
from netforce.model import get_model
from netforce import database


def import_record(rec_el):
    model = rec_el.attrib["model"]
    vals = {}
    for field_el in rec_el.iterfind("field"):
        name = field_el.attrib["name"]
        if len(field_el) > 0:
            val = etree.tostring(field_el[0]).decode()
        else:
            val = field_el.text
        vals[name] = val
    # print("model",model,"vals",vals)
    m = get_model(model)
    m.merge(vals)


def import_xml(data=None):
    # print("import_xml",data)
    root = etree.fromstring(data)
    if root.tag == "record":
        import_record(root)
    else:
        for el in root.iterfind("record"):
            import_record(el)


def load_data(module=None):
    print("Loading data...")
    for data_dir in ("views", "actions", "data"):
        if not pkg_resources.resource_isdir(module, data_dir):
            continue
        for f in pkg_resources.resource_listdir(module, data_dir):
            if not f.endswith("xml"):
                continue
            path = os.path.join(data_dir, f)
            print("loading %s" % path)
            data = pkg_resources.resource_string(module, path).decode()
            import_xml(data)
    db = database.get_connection()
    db.commit()
