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
from netforce.model import get_model, clear_cache
from netforce import database
from netforce import utils
from netforce import access
import xmlrpc


class XmlRpc(Controller):
    _path = "/xmlrpc"

    def post(self):
        params, r_method = xmlrpc.client.loads(self.request.body)
        db = database.get_connection()
        if db:
            db.begin()
        try:
            if r_method == "execute":
                model = params[0]
                method = params[1]
                args = params[2]
                if len(params) >= 4:
                    opts = params[3]
                else:
                    opts = {}
                if len(params) >= 7:
                    dbname = params[4]
                    user_id = params[5]
                    token = params[6]
                    if utils.check_token(dbname, user_id, token):
                        database.set_active_db(dbname)
                        access.set_active_user(user_id)
                m = get_model(model)
                f = getattr(m, method)
                res = f(*args, **opts)
            else:
                raise Exception("Invalid XML-RPC method")
            resp = xmlrpc.client.dumps((res,), methodresponse=True, allow_none=True)
            self.write(resp)
            db = database.get_connection()
            if db:
                db.commit()
        except Exception as e:
            db = database.get_connection()
            if db:
                db.rollback()
            import traceback
            traceback.print_exc()
            f = xmlrpc.client.Fault(0, str(e))
            self.write(xmlrpc.client.dumps(f, methodresponse=True, allow_none=True))

XmlRpc.register()
