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

from .model import get_model
from . import template
import os
from lxml import etree
import json
from . import module
import shutil
import pkg_resources
import py_compile
import sys

_xml_layouts = {}


def load_xml_layouts():
    print("loading layouts...")
    _xml_layouts.clear()
    loaded_modules = module.get_loaded_modules()
    for m in loaded_modules:
        if not pkg_resources.resource_exists(m, "layouts"):
            continue
        for fname in pkg_resources.resource_listdir(m, "layouts"):
            if not fname.endswith("xml"):
                continue
            data = pkg_resources.resource_string(m, "layouts/" + fname)
            try:
                root = etree.fromstring(data)
                vals = {
                    "module": m,
                }
                vals["name"] = fname.replace(".xml", "")
                vals["type"] = root.tag.lower()
                if root.attrib.get("model"):
                    vals["model"] = root.attrib["model"]
                if root.attrib.get("inherit"):
                    vals["inherit"] = root.attrib["inherit"]
                if root.attrib.get("priority"):
                    vals["priority"] = int(root.attrib["priority"])
                vals["layout"] = data.decode()
                _xml_layouts[vals["name"]] = vals
            except Exception as e:
                print("ERROR: Failed to load XML layout: %s/%s (%s)" % (m, fname, e))
    print("  %d layouts loaded"%len(_xml_layouts))


def layouts_to_json(modules=None):
    if modules is None:
        return _xml_layouts
    return {n:v for n,v in _xml_layouts.items() if v["module"] in modules}
