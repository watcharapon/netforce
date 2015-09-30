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
from netforce.model import get_model
from netforce.database import get_connection
from netforce_report import report_render_xls
import time


class ExportXLS(Controller):
    _path = "/report_export_xls"

    def get(self):
        db = get_connection()
        try:
            model = self.get_argument("model")
            active_id = self.get_argument("active_id")
            active_id = int(active_id)
            method = self.get_argument("method", "get_report_data")
            tmpl_name = self.get_argument("template")
            fast_render = self.get_argument("fast_render", None)
            m = get_model(model)
            f = getattr(m, method, None)
            ctx = {}  # XXX
            data = f([active_id], context=ctx)
            out = report_render_xls(tmpl_name, data, fast_render=fast_render)
            db.commit()
            fname = tmpl_name + "-" + time.strftime("%Y-%m-%dT%H:%M:%S") + ".xlsx"
            self.set_header("Content-Disposition", "attachment; filename=%s" % fname)
            self.set_header("Content-Type", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            self.write(out)
        except:
            import traceback
            traceback.print_exc()
            db.rollback()

ExportXLS.register()
