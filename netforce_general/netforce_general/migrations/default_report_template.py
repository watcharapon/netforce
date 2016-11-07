import os
import random
import requests

from netforce.model import get_model
from netforce import migration
from netforce.database import get_connection, get_active_db

def get_rand():
    return int(random.random()*10000)

class Migration(migration.Migration):
    _name="default.report.template"
    _version="3.1.0"

    def migrate(self):
        """
            Copy from from MGT to local
        """
        url="http://mgt.netforce.com/get_report_template?%s"%(get_rand())
        res=requests.get(url)
        if res.status_code!=200:
            raise Exception("Wrong url")
        lines=eval(res.text)
        dbname=get_active_db()
        for line in lines:
            try:
                fname=line['file']
                url="http://mgt.netforce.com/static/db/ctrl/files/%s?%s"%(fname,get_rand())
                res2=requests.get(url)
                if res2.status_code!=200:
                    raise Exception("Wrong url")

                path=os.path.join(os.getcwd(), "static", "db", dbname, "files")
                if not os.path.exists(path):
                    os.makedirs(path)
                path=os.path.join(path,fname)

                #data=str(res2.content,'utf-8')
                data=res2.content
                open(path,"wb").write(data)

                vals={
                    'name': line['name'],
                    'file': fname,
                    'type': line['type'],
                    'default': True,
                    'format': line['format'],
                    'method': line['method'],
                }
                print('load: ', path, ' => OK')
                res3=get_model("report.template").search([['name','=',vals['name']]])
                if not res3:
                    new_id=get_model("report.template").create(vals)
                    print('new default report template ', vals['name'])
            except Exception as e:
                print("ERROR ", e, line['name'])


Migration.register()
