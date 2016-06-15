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
from netforce.database import get_connection
from netforce import config, database
from random import choice
import urllib.request as request
import string
from netforce import access


class ForgotPasswd(Model):
    _name = "forgot.passwd"
    _transient = True
    _fields = {
        "email": fields.Char("Enter your email:", required=True),
        "key": fields.Char("Key"),
        "is_reset" : fields.Boolean("Reset"),
        "show_dbs": fields.Boolean("Show DBs"),
        "db_name": fields.Selection([], "Database", required=True),
    }

    def create(self, vals, **kw):
        db_name = vals.get("db_name")
        if not db_name:
            raise Exception("Missing db name")
        database.set_active_db(db_name)
        uid = access.get_active_user()
        try:
            access.set_active_user(1)
            return super().create(vals, **kw)
        finally:
            access.set_active_user(uid)

    def write(self,ids,vals,**kw):
        if ids:
            if vals.get("db_name"):
                database.set_active_db(vals.get("db_name"))
            else:
                database.set_active_db(self.browse(ids[0]).db_name)
            access.set_active_user(1)
            super().write(ids,vals,**kw)

    def get_databases(self, context={}):
        if config.get("database"):
            dbname = config.get("database")
            return [(dbname, dbname)]
        elif config.get("database_from_domain"):
            request_context = context["request"]
            host = request_context.host
            subdom = host.split(".", 1)[0]
            if subdom not in ("all", "clients"):  # XXX
                dbname = subdom.replace("-", "_")
                return [(dbname, dbname)]
        elif config.get("database_from_http_header"):
            request_context = context["request"]
            dbname = request_context.headers.get("X-Database")
            return [(dbname, dbname)]
        db_list = sorted(database.list_databases())
        return [(x, x) for x in db_list]

    def default_get(self, field_names=None, context={}, **kw):
        data={}
        chars = string.ascii_letters + string.digits
        length = 8
        key = ''.join([choice(chars) for _ in range(length)])
        data['key'] = key
        if context :
            data['show_dbs'] = get_model("login").get_show_dbs()
            data['db_name'] = get_model("login").get_db_name()
            if context.get("email"):
                data['email'] = context.get("email")
        return data

    def check_connectivity(self, reference):
        try:
            request.urlopen(reference, timeout=1)
            return True
        except request.URLError:
            return False

    def _send_email(self, ids, context={}):
        db = get_connection()
        request_context = context.get("request")
        #for check your internet connection
        try:
            access.set_active_user(1)
            obj = self.browse(ids[0])
            db.commit()
            # XXX "=" should be changed to "=ilike" later
            res = get_model("base.user").search((["email", "=ilike", obj.email.strip()]))
            if not res:
                raise Exception("User with given email doesn't exist in database")
            '''
                EX:
                    mgt.netforce.com/forgot_password?email=anas.t@almacom.co.th&url=1234567
            '''

            host = request_context.host
            protocol = request_context.protocol

            key = obj.key
            action = "change_passwd"
            #key is always change every time, dont worry for cache
            url='http://mgt.netforce.com/forgot_password?email=%s&host=%s&action=%s&key=%s&protocol=%s'%(obj.email,host,action,key,protocol)
            internet = self.check_connectivity('https://www.google.co.th/')
            if not internet:
                raise Exception("Please check your internet connection")
            try:
                rq=request.urlopen(url)
                data=rq.read()
                if data:
                    data = eval(data)
                    if data.get("status"):
                        return {"next": {"name": "forgot_passwd_done","email" : obj.email}}
                else:
                    raise Exception("Please contact support@netforce.com")
            except Exception as e:
                msg=e
                print("ERROR ", e)
                return {
                    'flash': 'ERROR: %s'%msg,
                    'type': 'error',
                }
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise Exception(e)

    def send_email(self, context={}):
        data = context.get("data")
        db_name = data.get("db_name")
        if not db_name:
            raise Exception("Missing db name")
        database.set_active_db(db_name)
        email = data.get("email")
        key = data.get("key")
        db = get_connection()
        request_context = context.get("request")
        #for check your internet connection
        try:
            access.set_active_user(1)
            # XXX "=" should be changed to "=ilike" later
            res = get_model("base.user").search((["email", "=ilike", email.strip()]))
            if not res:
                raise Exception("User with given email doesn't exist in database")
            '''
                EX:
                    mgt.netforce.com/forgot_password?email=anas.t@almacom.co.th&url=1234567
            '''

            host = request_context.host
            protocol = request_context.protocol

            action = "change_passwd"
            #key is always change every time, dont worry for cache
            url='http://mgt.netforce.com/forgot_password?email=%s&host=%s&action=%s&key=%s&protocol=%s&db_name=%s'%(email,host,action,key,protocol,db_name)
            internet = self.check_connectivity('https://www.google.co.th/')
            #create data
            self.create(data)
            db.commit()
            if not internet:
                raise Exception("Please check your internet connection")
            try:
                rq=request.urlopen(url)
                data=rq.read()
                if data:
                    data = eval(data)
                    if data.get("status"):
                        return {"next": {"name": "forgot_passwd_done","email" : email}}
                else:
                    raise Exception("Please contact support@netforce.com")
            except Exception as e:
                msg=e
                print("ERROR ", e)
                return {
                    'flash': 'ERROR: %s'%msg,
                    'type': 'error',
                }
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise Exception(e)

ForgotPasswd.register()
