# Netforce Developer Guide

## A. Architecture

* Database: Postgresql
* Programming languages: Python 3 / Javascript
* Web server: Tornado
* Client-side MVC: Backbone.js
* Templates: Handlebars.js

## B. Module components

### 1. Models

```
from netforce.model import Model,fields

class Product(Model):
    _name=”product”
    _string=”Product”
    _fields={
        “code”: fields.Char(“Product Code”,required=True),
        “name”: fields.Char(“Product Name”,required=True),
        “description”: fields.Text(“Description”),
    }
    _order=”code”

Product.register()
```

Models are stored in the “models” directory of the module (1 .py file per model).

### 2. Actions

```
<action>
    <field name="view_cls">multi_view</field>
    <field name="string">Products</field>
    <field name="model">product</field>
    <field name="menu">product_menu</field>
</action>
```

Actions are stored in the “actions” directory of the module (1 .xml file per action).

### 3. View Layouts

```
<list model=”product”>
    <field name=”code”/>
    <field name=”name”/>
</list>
```

```
<form model=”product”>
    <field name=”code”/>
    <field name=”name”/>
    <separator/>
    <field name=”description”/>
</form>
```

View layouts are stored in the “layouts” directory of the module (1 .xml file per layout).

### 4. Controllers

**Note**: most modules don’t need to define custom controllers

```
from netforce.controller import Controller

class Hello(Controller):
    _path=”/hello”

    def get(self):
        self.write(“Hello world!”)

Hello.register()
```

netforce.controller.Controller inherits from tornado.web.RequestHandler

More details about Tornado: http://www.tornadoweb.org

Controllers are stored in the “controllers” directory of the module (1 .py file per controller).

### 5. Views

**Note**: most modules don’t need to define custom views

```
var Hello=NFView.extend({
    _name: "hello",

    render: function() {
        this.$el.text(“Hello World!”);
    }
});

Hello.register();
```

NFView inherits from Backbone.View

More details about Backbone: http://backbonejs.org/

Views are stored in the “views” directory of the module (1 .js file per view).

### 6. Templates

**Note**: most modules don’t need to define custom templates

```
<h3>{{title}}</h3>
{{#if morning}}
    <p>Good morning, {{name}}</p>
{{/if}}
{{#if evening}}
    <p>Good evening, {{name}}</p>
{{/if}}
```

More details about Handlebars: http://handlebarsjs.com/

Templates are stored in the “templates” directory of the module (1 .hbs file per template).

### 7. Migrations

```
from netforce import migration

class Migration(migration.Migration):
    _name="product.example_migration"
    _version="1.150.0"

    def migrate(self):
        print("do something...")

Migration.register()
```

Migrations are stored in the "migrations" directory of the module (1 .py file per migration).

### 8. Unit tests

```
from netforce.test import TestCase

class Test(TestCase):
    _name="example.test"
    _description="An example unit test"

    def run_test(self):
        print("test something...")

Test.register()
```

Unit tests are stored in the "tests" directory of the module (1 .py file per unit tet).

## C. Running in production

run.py script:

```
#!/usr/bin/env python3
import netforce

modules=[
    "netforce_ui",
    "netforce_report",
    "netforce_xmlrpc",
    "netforce_jsonrpc",
    "netforce_general",
    "netforce_contact",
    "netforce_service",
    "netforce_product",
    "netforce_account",
    "netforce_account_report",
    "netforce_stock",
    "netforce_stock_cost",
    "netforce_sale",
    "netforce_purchase",
    "netforce_mfg",
    "netforce_marketing",
    "netforce_hr",
    "netforce_document",
    "netforce_messaging",
    "netforce_cms",
    "netforce_pos",
]

netforce.load_modules(modules)
netforce.run_server()
```

server.conf file:

```
[server]
host: 127.0.0.1
port: 9999
db_user: almacom
db_password: 1234
super_password: 5678
```

nginx config:

```
server {
    server_name nf7.netforce.com;

    gzip on;
    gzip_min_length 1000;
    gzip_proxied any;
    gzip_types text/plain text/html text/css text/xml application/x-javascript application/xml application/atom+xml text/javascript application/json;

    location ^~ /static/ {
            root /home/almacom/netforce;
            expires 1h;

            location /static/ui_params.json {
                    expires 1s;
            }

            location ~ /static/db/.*/ui_params_db.json {
                    expires 1s;
            }
    }

    location / {
            proxy_pass_header Server;
            proxy_set_header Host $http_host;
            proxy_redirect off;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Scheme $scheme;
            proxy_pass http://127.0.0.1:9999;
            if_modified_since off;
            add_header Last-Modified "";
            add_header Cache-Control no-cache;
    }
}
```

add line in nginx.conf:
```
client_max_body_size 50M;
```

add line in postgresql.conf:
```
statement_timeout 300000
```

Install jodconverter:

```
sudo apt-get install jodconverter
```

Script to start libreoffice in headless mode:
```
#!/bin/sh
soffice "--accept=socket,port=8100;urp;" --headless
```

backup_dbs.sh script:
```
#!/bin/bash
DBS=`psql template1 --tuples-only -P format=unaligned -c "SELECT datname FROM pg_database WHERE NOT datistemplate AND datname!='postgres' and not datname~'_demo[0-9]*$' and not datname~'^old_'"`
echo $DBS
for db in ${DBS}; do
        echo "backing up $db..."
        d=`date +%Y-%m-%d`
        f=/tmp/$db-$d.sql.gz
        echo $f
        pg_dump $db | gzip > $f
        s3cmd put $f s3://backup-nf4/
        rm $f
done
```

backup_files.sh script: (TODO: update to backup files of all dbs)
```
#!/bin/bash
find /home/almacom/netforce/static/db/antares/files/ -mindepth 1 -mtime -2 | while read line; do
    echo "backing up file $line..."
    s3cmd put "$line" s3://backup-bkkbase-files/
done
```

jasper reports:
need netforce_report.jar + openjdk-6-jdk package
