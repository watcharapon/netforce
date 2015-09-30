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
import time
from netforce import access
import csv
import sys
from datetime import datetime, timedelta
import smtplib
from io import StringIO
from netforce.database import get_active_db
import os
import http.client
import urllib.request
import csv
import urllib.parse
from netforce.logger import audit_log
from netforce.utils import get_file_path

uth_handler = urllib.request.HTTPBasicAuthHandler()


class ImportAttendance(Model):
    _name = "hr.import.attendance"
    _string = "Import Attendance"

    _fields = {
        "import_type": fields.Selection([["manual", "Manual"], ["auto", "Auto"]], "Import From", required=True),
        "file": fields.File("CSV File", required=False),
        "machine_id": fields.Many2One("hr.attendance.config", "Machine Config"),
        "encoding": fields.Selection([["utf-8", "UTF-8"], ["tis-620", "TIS-620"]], "Encoding", required=True),
        "date": fields.Date("Date From"),
        "date_fmt": fields.Char("Date Format"),
        "comments": fields.One2Many("message", "related_id", "Comments"),
    }
    _order = "time desc"
    _defaults = {
        "import_type": "manual",
        "encoding": "utf-8",
        'date_fmt': '%Y-%m-%d %H:%M:%S'
    }

    def get_data(self, ids, context={}):
        machine = 1
        if context:
            if "machine_id" in context:
                machine = context["machine_id"]

        obj = get_model("hr.attendance.config").browse(machine)
        auth_handler = urllib.request.HTTPBasicAuthHandler()
        auth_handler.add_password(realm='Basic Authentication Application',
                                  uri="http://" + obj.ip_address,
                                  user=obj.user,
                                  passwd=obj.password)
        opener = urllib.request.build_opener(auth_handler)
        urllib.request.install_opener(opener)
        urllib.request.urlopen('http://' + obj.ip_address)
        post_data = {'uid': 'extlog.dat'}  # POST data for download attendance log
        conn = http.client.HTTPConnection(obj.ip_address)
        params = urllib.parse.urlencode(post_data)
        headers = {'Content-type': "application/x-www-form-urlencoded",
                   'Accept': 'text/plain'}
        conn.request('POST', obj.url_download, params, headers)
        response = conn.getresponse()
        log = response.read()
        res = log.decode('tis-620')
        lines = str(res).split('\r\n')
        if conn:
            conn.close()
        return lines

    def import_auto(self, ids, context={}):
        obj = self.browse(ids)[0]
        date = context.get('date', datetime.today())
        lines = obj.get_data(context=context)
        current_date = datetime.today()
        date_in = date.strftime("%Y-%m-%d 00:00:00")
        date_out = current_date.strftime("%Y-%m-%d 23:59:59")
        count = 0
        detail = []
        st = ""
        for line in lines:

            if line:
                st += line.replace("\t", ",")
                st += '\n'

            line = line.split('\t')
            if len(line) > 1:
                if line[1] >= date_in and line[1] <= date_out:
                    attendance_id = get_model("hr.employee").search([["attendance_id", "=", line[0]]])
                    dt_time = datetime.strptime(str(line[1]), "%Y-%m-%d %H:%M:%S")
                    dt_in = dt_time.strftime("%Y-%m-%d 00:00:00")
                    dt_out = dt_time.strftime("%Y-%m-%d 23:59:59")
                    if attendance_id:
                        employee = get_model("hr.employee").browse(attendance_id)[0]
                        have = []
                        have = get_model("hr.attendance").search(
                            [["employee_id", "=", employee.id], ["time", "=", line[1]]])
                        check = False
                        if not have:
                            bf_id = []
                            bf_id = get_model("hr.attendance").search(
                                [["employee_id", "=", employee.id], ["time", ">=", dt_in], ["time", "<=", dt_out], ["time", "<", line[1]]])
                            if not bf_id:
                                action = "sign_in"
                            elif bf_id:
                                attend = get_model("hr.attendance").browse(bf_id)[0]
                                date_get = datetime.strptime(attend.time, "%Y-%m-%d %H:%M:%S")
                                dt = date_get + timedelta(minutes=1)
                                date_check = datetime.strptime(
                                    str(dt), "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
                                if line[1] <= date_check:
                                    check = True
                                if attend.action == "sign_out":
                                    action = "sign_in"
                                elif attend.action == "sign_in":
                                    action = "sign_out"
                            if check is False:
                                count += 1
                                detail.append(
                                    {"name": employee.first_name + " " + employee.last_name, "date": line[1], "action": action})
                                vals = {
                                    "employee_id": employee.id,
                                    "time": line[1],
                                    "action": action,
                                }
                                get_model("hr.attendance").create(vals)
        audit_log("Add attendance %s record at %s employee: %s " % (count, date, str(detail)))

        open("/tmp/res.csv", "w").write(st)  # XXX
        return count

    def _import_data(self, ids, context={}):
        obj = self.browse(ids[0])
        count = 0
        if obj.import_type == 'auto':
            if not obj.machine_id:
                raise Exception("Select device to import from")

            context = ({"machine_id": obj.machine_id.id, "date": obj.date})
            count = self.import_auto(ids, context=context)
        else:
            if not obj.file:
                raise Exception("Please give csv file for import data")
            dbname = get_active_db()
            data = open(os.path.join("static", "db", dbname, "files", obj.file), "rb").read().decode(obj.encoding)
            found_delim = False
            for delim in (",", ";", "\t"):
                try:
                    try:
                        rd = csv.reader(StringIO(data), delimiter=delim)
                    except:
                        raise Exception("Invalid CSV file")
                    headers = next(rd)
                    headers = [h.strip() for h in headers]
                    for h in ["id", "date"]:
                        if not h in headers:
                            raise Exception("Missing header: '%s'" % h)
                    found_delim = True
                    break
                except:
                    pass
            if not found_delim:
                raise Exception("Failed to open CSV file")
            rows = [r for r in rd]
            if not rows:
                raise Exception("Statement is empty")
            formats = ["%Y-%m-%d  %H:%M:%S", "%d/%m/%Y  %H:%M:%S",
                       "%m/%d/%Y  %H:%M:%S", "%d/%m/%y  %H:%M:%S", "%m/%d/%y  %H:%M:%S"]
            date_fmt = None
            for fmt in formats:
                fmt_ok = True
                for row in rows:
                    vals = dict(zip(headers, row))
                    date = vals["date"].strip()
                    if not date:
                        continue
                    try:
                        datetime.strptime(date, fmt)
                    except:
                        fmt_ok = False
                        break
                if fmt_ok:
                    date_fmt = fmt
                    break
            if not date_fmt:
                raise Exception("Could not detect date format")
            for i, row in enumerate(rows):
                vals = dict(zip(headers, row))
                try:
                    date = vals["date"].strip()
                    if not date:
                        raise Exception("Missing date")
                    date = datetime.strptime(date, date_fmt).strftime("%Y-%m-%d %H:%M:%S")
                    date_in = datetime.strptime(date, date_fmt).strftime("%Y-%m-%d 00:00:00")
                    date_out = datetime.strptime(date, date_fmt).strftime("%Y-%m-%d 23:59:59")
                    id_employee = vals["id"].strip().replace(",", "")
                    if not id_employee:
                        raise Exception("missing employeeid")
                    attendance_id = get_model("hr.employee").search([["attendance_id", "=", id_employee]])
                    if attendance_id:
                        employee = get_model("hr.employee").browse(attendance_id)[0]
                        have_id = []
                        have_id = get_model("hr.attendance").search(
                            [["employee_id", "=", employee.id], ["time", "=", date]])
                        check = False
                        if not have_id:
                            bf_id = []
                            bf_id = get_model("hr.attendance").search(
                                [["employee_id", "=", employee.id], ["time", ">=", date_in], ["time", "<=", date_out], ["time", "<", date]])
                            if not bf_id:
                                action = "sign_in"
                            elif bf_id:
                                attend = get_model("hr.attendance").browse(bf_id)[0]
                                date_get = datetime.strptime(attend.time, date_fmt)
                                dt = date_get + timedelta(minutes=1)
                                date_check = datetime.strptime(str(dt), date_fmt).strftime("%Y-%m-%d %H:%M:%S")
                                if date <= date_check:
                                    check = True
                                if attend.action == "sign_out":
                                    action = "sign_in"
                                elif attend.action == "sign_in":
                                    action = "sign_out"
                            if check is False:
                                count += 1
                                vals = {
                                    "time": date,
                                    "employee_id": employee.id,
                                    "action": action,
                                }
                                get_model("hr.attendance").create(vals)

                except Exception as e:
                    audit_log("Failed to get attendance orders", details=e)
                    raise Exception("Error on line %d (%s)" % (i + 2, e))

        return {
            "next": {
                "name": "attend",
                "mode": "list",
            },
            "flash": "Import : %s records" % (count)
        }

    def set_att(self, ids, att_ids, context={}):
        index = 0
        for emp in get_model("hr.employee").search_browse([['work_status', '=', 'working']]):
            if index > len(att_ids) - 1:
                att_ids.append(index)  # XXX generate our-self
            emp.write({
                'attendance_id': att_ids[index],
            })
            print("update %s -> %s" % (emp.code, att_ids[index]))
            index += 1
        print("Done!")

    def import_data(self, ids, context={}):
        obj = self.browse(ids)[0]
        if obj.import_type == 'auto':
            obj.import_auto()
        else:
            if not obj.file:
                raise Exception("File not found")
            if obj.file.split(".")[-1] != 'csv':
                raise Exception("Wrong File")
            fpath = get_file_path(obj.file)
            data = open(fpath, "r").read().split("\n")
            att_ids = []
            records = {}
            for row in data:
                lines = row.split(",")
                if not lines:
                    continue
                size = len(lines)
                if size < 2:
                    continue
                if size > 2:
                    raise Exception("Wrong File")
                att_id = lines[0]
                att_date = lines[1]
                if not records.get(att_id):
                    records[att_id] = []
                records[att_id].append(att_date)
                continue
                # TODO Check format date
                if att_id not in att_ids:
                    att_ids.append(att_id)
            # self.set_att(ids,att_ids,context=context)
            emps = {emp['attendance_id']: emp['id']
                    for emp in get_model("hr.employee").search_read([], ['attendance_id'])}
            att = get_model("hr.attendance")
            at_ids = att.search([])
            # XXX testing
            att.delete(at_ids)
            for att_id, lines in records.items():
                att_id = int(att_id)
                date_list = []
                for line in lines:
                    datetime = line
                    date = datetime.split(" ")[0]
                    action = 'sign_in'
                    if date in date_list:
                        action = 'sign_out'
                        # FIXME find the last record and overwrite time
                    date_list.append(date)
                    att.create({
                        'employee_id': emps[att_id],
                        'action': action,
                        'time': datetime,
                    })
            print("Done!")

ImportAttendance.register()
