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
from datetime import *
from dateutil.relativedelta import *
from netforce.access import get_active_company
from netforce.database import get_connection


def get_totals(date_from=None, date_to=None, excl_date_to=False, track_categ_ids=None, track_id=None, track2_id=None, contact_id=None, account_id=None, acc_type=None):
    pl_types = ("revenue", "other_income", "cost_sales", "expense", "other_expense")
    db = get_connection()
    q = "SELECT l.account_id,l.contact_id,l.track_id,l.track2_id,SUM(l.debit) AS total_debit,SUM(l.credit) AS total_credit FROM account_move_line l JOIN account_move m ON m.id=l.move_id JOIN account_account a ON a.id=l.account_id WHERE m.state='posted'"
    args = []
    if date_from:
        q += " AND m.date>=%s"
        args.append(date_from)
    if date_to:
        if excl_date_to:
            q += " AND m.date<%s"
        else:
            q += " AND m.date<=%s"
        args.append(date_to)
    if track_categ_ids:
        q += " AND l.track_id in %s"
        args.append(tuple(track_categ_ids))
    if track_id:
        q += " AND l.track_id=%s"
        args.append(track_id)
    if track2_id:
        q += " AND l.track2_id=%s"
        args.append(track2_id)
    if contact_id:
        q += " AND l.contact_id=%s"
        args.append(contact_id)
    if account_id:
        q += " AND l.account_id=%s"
        args.append(account_id)
    if acc_type == "pl":
        q += " AND a.type IN %s"
        args.append(pl_types)
    elif acc_type == "bs":
        q += " AND a.type NOT IN %s"
        args.append(pl_types)
    q += " GROUP BY l.account_id,l.contact_id,l.track_id,l.track2_id"
    res = db.query(q, *args)
    totals = []
    for r in res:
        totals.append({
            "account_id": r.account_id,
            "contact_id": r.contact_id,
            "track_id": r.track_id,
            "track2_id": r.track2_id,
            "debit": r.total_debit,
            "credit": r.total_credit,
        })
    return totals


class ReportTBDetails(Model):
    _name = "report.tb.details"
    _transient = True
    _fields = {
        "date": fields.Date("Date", required=True),
        "track_categ_id": fields.Many2One("account.track.categ", "Tracking Category",condition=[["parent_id","=",None]]),
        "track_id": fields.Many2One("account.track.categ", "Tracking-1", condition=[["type", "=", "1"]]),
        "track2_id": fields.Many2One("account.track.categ", "Tracking-2", condition=[["type", "=", "2"]]),
        "contact_id": fields.Many2One("contact", "Contact"),
        "account_id": fields.Many2One("account.account", "Account"),
        "group_track_categ": fields.Boolean("Group by Tracking Category"),
        "hide_period": fields.Boolean("Hide zero period"),
        "hide_ytd": fields.Boolean("Hide zero YTD"),
        "show_net": fields.Boolean("Show Net"),
    }

    _defaults = {
        "date": lambda *a: date.today().strftime("%Y-%m-%d"),
        "group_track_categ": False,
        "hide_period": False,
        "hide_ytd": False,
        "show_net": False,
    }

    def get_report_data(self, ids, context={}):
        company_id = get_active_company()
        comp = get_model("company").browse(company_id)
        if ids:
            params = self.read(ids, load_m2o=False)[0]
        else:
            params = self.default_get(load_m2o=False, context=context)
        settings = get_model("settings").browse(1)
        date_to = params.get("date")
        if not date_to:
            date_to = date.today().strftime("%Y-%m-%d")
        track_id = params.get("track_id")
        p_track = None
        if track_id:
            track = get_model('account.track.categ').browse(int(track_id))
            p_track = track
        track2_id = params.get("track2_id")
        p_track2 = None
        if track2_id:
            track2 = get_model('account.track.categ').browse(int(track2_id))
            p_track2 = track2
        track_categ_id = params.get("track_categ_id")
        track_categ_ids = track_categ = None
        if track_categ_id:
            track_categ_ids = get_model("account.track.categ").search([["id", "child_of", track_categ_id]])
            track_categ = get_model("account.track.categ").browse(int(track_categ_id))
        account_id = params.get("account_id")
        contact_id = params.get("contact_id")
        group_track_categ = params.get("group_track_categ")
        hide_period = params.get("hide_period")
        hide_ytd = params.get("hide_ytd")
        show_net = params.get("show_net")
        month_date_from = datetime.strptime(date_to, "%Y-%m-%d").strftime("%Y-%m-01")
        month_begin_date_to = (
            datetime.strptime(date_to, "%Y-%m-%d") + relativedelta(day=1) - timedelta(days=1)).strftime("%Y-%m-%d")
        year_date_from = get_model("settings").get_fiscal_year_start(date_to)
        totals_begin_bs = get_totals(date_from=None, date_to=month_begin_date_to, track_categ_ids=track_categ_ids,
                                     track_id=track_id, track2_id=track2_id, contact_id=contact_id, account_id=account_id, acc_type="bs")
        totals_begin_pl = get_totals(date_from=year_date_from, date_to=month_begin_date_to, track_categ_ids=track_categ_ids,
                                     track_id=track_id, track2_id=track2_id, contact_id=contact_id, account_id=account_id, acc_type="pl")
        totals_period = get_totals(date_from=month_date_from, date_to=date_to, track_categ_ids=track_categ_ids,
                                     track_id=track_id, track2_id=track2_id, contact_id=contact_id, account_id=account_id)
        totals_ytd_bs = get_totals(date_from=None, date_to=date_to, track_categ_ids=track_categ_ids,
                                     track_id=track_id, track2_id=track2_id, contact_id=contact_id, account_id=account_id, acc_type="bs")
        totals_ytd_pl = get_totals(date_from=year_date_from, date_to=date_to, track_categ_ids=track_categ_ids,
                                     track_id=track_id, track2_id=track2_id, contact_id=contact_id, account_id=account_id, acc_type="pl")
        totals_pl_prev = get_totals(date_from=None, date_to=year_date_from, excl_date_to=True, track_categ_ids=track_categ_ids,
                                    track_id=track_id, track2_id=track2_id, contact_id=contact_id, account_id=account_id, acc_type="pl")
        totals = {}
        for tot in totals_begin_bs:
            k = (tot["account_id"], tot["contact_id"], tot["track_id"], tot["track2_id"])
            vals = totals.setdefault(k, {})
            amt = tot["debit"] - tot["credit"]
            vals["begin_debit"] = amt > 0 and amt or 0
            vals["begin_credit"] = amt < 0 and -amt or 0
        for tot in totals_begin_pl:
            k = (tot["account_id"], tot["contact_id"], tot["track_id"], tot["track2_id"])
            vals = totals.setdefault(k, {})
            amt = tot["debit"] - tot["credit"]
            vals["begin_debit"] = amt > 0 and amt or 0
            vals["begin_credit"] = amt < 0 and -amt or 0
        for tot in totals_period:
            k = (tot["account_id"], tot["contact_id"], tot["track_id"], tot["track2_id"])
            vals = totals.setdefault(k, {})
            amt = tot["debit"] - tot["credit"]
            vals["period_debit"] = amt > 0 and amt or 0
            vals["period_credit"] = amt < 0 and -amt or 0
        for tot in totals_ytd_bs:
            k = (tot["account_id"], tot["contact_id"], tot["track_id"], tot["track2_id"])
            vals = totals.setdefault(k, {})
            amt = tot["debit"] - tot["credit"]
            vals["ytd_debit"] = amt > 0 and amt or 0
            vals["ytd_credit"] = amt < 0 and -amt or 0
        for tot in totals_ytd_pl:
            k = (tot["account_id"], tot["contact_id"], tot["track_id"], tot["track2_id"])
            vals = totals.setdefault(k, {})
            amt = tot["debit"] - tot["credit"]
            vals["ytd_debit"] = amt > 0 and amt or 0
            vals["ytd_credit"] = amt < 0 and -amt or 0
        settings = get_model("settings").browse(1)
        ret_acc_id = settings.retained_earnings_account_id.id
        if ret_acc_id:
            ret_amt = 0
            for tot in totals_pl_prev:
                ret_amt += tot["debit"] - tot["credit"]
            k = (ret_acc_id, None, None, None)
            vals = totals.setdefault(k, {})
            amt = vals.get("begin_debit", 0) - vals.get("begin_credit", 0)
            amt += ret_amt
            vals["begin_debit"] = amt > 0 and amt or 0
            vals["begin_credit"] = amt < 0 and -amt or 0
            amt = vals.get("ytd_debit", 0) - vals.get("ytd_credit", 0)
            amt += ret_amt
            vals["ytd_debit"] = amt > 0 and amt or 0
            vals["ytd_credit"] = amt < 0 and -amt or 0
            vals["no_link"] = True
        lines = []
        for (account_id, contact_id, track_id, track2_id), vals in totals.items():
            if hide_period and not vals.get("period_debit") and not vals.get("period_credit"): continue
            if hide_ytd and not vals.get("ytd_debit") and not vals.get("ytd_credit"): continue
            if show_net:
                vals = self.calc_net(vals=vals)
            lines.append({
                "account_id": account_id,
                "contact_id": contact_id,
                "track_id": track_id,
                "track2_id": track2_id,
                "begin_debit": vals.get("begin_debit", 0),
                "begin_credit": vals.get("begin_credit", 0),
                "period_debit": vals.get("period_debit", 0),
                "period_credit": vals.get("period_credit", 0),
                "ytd_debit": vals.get("ytd_debit", 0),
                "ytd_credit": vals.get("ytd_credit", 0),
                "no_link": vals.get("no_link"),
            })
        account_ids = list(set([l["account_id"] for l in lines]))
        contact_ids = list(set([l["contact_id"] for l in lines if l["contact_id"]]))
        track_ids = list(set([l["track_id"] for l in lines if l["track_id"]] + [l["track2_id"]
                                                                                for l in lines if l["track2_id"]]))
        accounts = {}
        for acc in get_model("account.account").browse(account_ids):
            accounts[acc.id] = acc
        contacts = {}
        for contact in get_model("contact").browse(contact_ids):
            contacts[contact.id] = contact
        tracks = {}
        for track in get_model("account.track.categ").browse(track_ids):
            tracks[track.id] = track
        categ_lines = {}
        for line in lines:
            account = accounts[line["account_id"]]
            contact = contacts[line["contact_id"]] if line["contact_id"] else None
            track = tracks[line["track_id"]] if line["track_id"] else None
            track2 = tracks[line["track2_id"]] if line["track2_id"] else None
            line["track_categ_code"] = track_categ.code if track_categ else None
            line["account_code"] = account.code
            line["account_name"] = account.name
            line["contact_name"] = contact.name if contact else None
            line["track_code"] = track.code if track else None
            line["track2_code"] = track2.code if track2 else None
            if group_track_categ:
                if account.id not in categ_lines:
                    categ_lines[account.id] = line
                    categ_lines[account.id]["no_link"] = True
                    categ_lines[account.id]["track_code"] = None
                    categ_lines[account.id]["track2_code"] = None
                    categ_lines[account.id]["contact_name"] = None
                    categ_lines[account.id]["track_id"] = None
                    categ_lines[account.id]["track2_id"] = None
                    categ_lines[account.id]["contact_id"] = None
                else:
                    categ_lines[account.id]["begin_debit"] += line["begin_debit"]
                    categ_lines[account.id]["begin_credit"] += line["begin_credit"]
                    categ_lines[account.id]["period_debit"] += line["period_debit"]
                    categ_lines[account.id]["period_credit"] += line["period_credit"]
                    categ_lines[account.id]["ytd_debit"] += line["ytd_debit"]
                    categ_lines[account.id]["ytd_credit"] += line["ytd_credit"]
        if group_track_categ:
            lines = []
            for acc_id,l in categ_lines.items():
                l = self.calc_net(vals=l)
                lines.append(l)
        lines.sort(
            key=lambda l: (l["account_code"], l["contact_name"] or "", l["track_code"] or "", l["track2_code"] or ""))
        totals = {
            "begin_debit": sum(l["begin_debit"] for l in lines),
            "begin_credit": sum(l["begin_credit"] for l in lines),
            "period_debit": sum(l["period_debit"] for l in lines),
            "period_credit": sum(l["period_credit"] for l in lines),
            "ytd_debit": sum(l["ytd_debit"] for l in lines),
            "ytd_credit": sum(l["ytd_credit"] for l in lines),
        }
        data = {
            "company_name": comp.name,
            "date": date_to,
            "month_date_from": month_date_from,
            "month_begin_date_to": month_begin_date_to,
            "track_name": p_track.name if p_track else None,
            "track_code": p_track.code if p_track else None,
            "track2_name": p_track2.name if p_track2 else None,
            "track2_code": p_track2.code if p_track2 else None,
            "lines": lines,
            "totals": totals,
        }
        return data

    def get_report_data_custom(self, ids, context={}):
        return self.get_report_data(ids, context=context)

    def calc_net(self,vals={}):
        if not vals: raise Exception("Missing Data")
        b_debit = vals.get('begin_debit') or 0
        b_credit = vals.get('begin_credit') or 0
        p_debit = vals.get('period_debit') or 0
        p_credit = vals.get('period_credit') or 0
        ytd_debit = vals.get('ytd_debit') or 0
        ytd_credit = vals.get('ytd_credit') or 0
        if (b_debit - b_credit) >= 0:
            vals["begin_debit"] = (b_debit - b_credit)
            vals["begin_credit"] = 0
        else:
            vals["begin_credit"] = (b_credit - b_debit)
            vals["begin_debit"] = 0
        if (p_debit - p_credit) >= 0:
            vals["period_debit"] = (p_debit - p_credit)
            vals["period_credit"] = 0
        else:
            vals["period_credit"] = (p_credit - p_debit)
            vals["period_debit"] = 0
        if (ytd_debit - ytd_credit) >= 0:
            vals["ytd_debit"] = (ytd_debit - ytd_credit)
            vals["ytd_credit"] = 0
        else:
            vals["ytd_credit"] = (ytd_credit - ytd_debit)
            vals["ytd_debit"] = 0
        return vals

ReportTBDetails.register()
