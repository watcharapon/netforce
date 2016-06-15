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
from netforce.access import set_active_user, get_active_user
from netforce import database
import re

def check_password(p):
    if len(p) < 5:
        raise Exception("Password must be at least 5 characters")
    if not re.search("\d", p):
        raise Exception("Password must contain at least 1 digit")
    if not re.search("[A-Z]", p):
        raise Exception("Password must contain at least 1 uppercase letter")
    if not re.search("[a-z]", p):
        raise Exception("Password must contain at least 1 lowercase letter")
    return True

class ChangePasswd(Model):
    _name = "change.passwd"
    _transient = True
    _fields = {
        "key": fields.Char("Key", required=True),
        "new_password": fields.Char("Enter new password:", required=True),
        "new_password_repeat": fields.Char("Confirm new password:", required=True),
        "is_reset" : fields.Boolean("Reset"),
        "db_name": fields.Char("Database", required=True),
    }

    def create(self, vals, **kw):
        db_name = vals.get("db_name")
        if not db_name:
            raise Exception("Missing db name")
        database.set_active_db(db_name)
        uid = get_active_user()
        try:
            set_active_user(1)
            return super().create(vals, **kw)
        finally:
            set_active_user(uid)

    def write(self,ids,vals,**kw):
        if ids:
            set_active_user(1)
            super().write(ids,vals,**kw)

    def default_get(self, field_names=None, context={}, **kw):
        data = {}
        if context:
            key = context.get('key')
            db_name = context.get("db_name")
            if not db_name:
                raise Exception("Missing Database")
            database.set_active_db(db_name)
            if db_name:
                data['db_name'] = db_name
            if key:
                set_active_user(1)
                forgots = get_model("forgot.passwd").search_browse([["key", "=", key]])
                if forgots:
                    forgot = forgots[0]
                    data['is_reset'] = forgot.is_reset
                data['key'] = key
                return data
        return data

    def _change_passwd(self, ids, context={}):
        set_active_user(1)
        obj = self.browse(ids)[0]
        res = get_model("forgot.passwd").search([["key", "=", obj.key]])
        if not res:
            raise Exception("Invalid key")
        forgot_passwd = get_model("forgot.passwd").browse(res[0])
        forgot_passwd.write({
            'is_reset' : True
        })
        res = get_model("base.user").search([["email", "=", forgot_passwd.email]])
        if not res:
            raise Exception("Invalid email")
        user_id = res[0]
        new_password = obj.new_password
        new_password_repeat = obj.new_password_repeat
        #check password character
        check_password(new_password)
        #check matching
        if new_password != new_password_repeat:
            raise Exception("Passwords are not matching")
        get_model("base.user").write([user_id], {"password": new_password})
        return {
            "next": {
                "name": "login"
            },
            "flash": {
                "message" : "Your password has been changed",
                "type" : "info"
            }
        }

    def change_passwd(self, context={}):
        data = context.get("data")
        key = data['key']
        db_name = data['db_name']
        database.set_active_db(db_name)
        new_password = data['new_password']
        new_password_repeat = data['new_password_repeat']
        set_active_user(1)
        res = get_model("forgot.passwd").search([["key", "=", key]])
        if not res:
            raise Exception("Invalid key")
        forgot_passwd = get_model("forgot.passwd").browse(res[0])
        forgot_passwd.write({
            'is_reset' : True
        })
        res = get_model("base.user").search([["email", "=", forgot_passwd.email]])
        if not res:
            raise Exception("Invalid email")
        user_id = res[0]
        #check password character
        check_password(new_password)
        #check matching
        if new_password != new_password_repeat:
            raise Exception("Passwords are not matching")
        get_model("base.user").write([user_id], {"password": new_password})
        return {
            "next": {
                "name": "login"
            },
            "flash": {
                "message" : "Your password has been changed",
                "type" : "info"
            }
        }
ChangePasswd.register()
