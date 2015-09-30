from netforce.template import register_helper
from urllib.parse import urlencode
from netforce.model import get_model

def ecom_products_url(this, categ_id=None, brand_id=None, supp_id=None, price=None, sort_by=None):
    #toggle_brand_id = brand_id
    categ_id=categ_id or this.data.get("categ_id")
    #brand_id=brand_id or this.data.get("brand_id")
    price=price or this.data.get("price")
    params={}
    if categ_id:
        params["categ_id"]=categ_id
    brand_ids = this.data.get("brand_id")[:]
    if brand_id:
        if brand_id in brand_ids:
            brand_ids.remove(brand_id)
        else:
            brand_ids.append(brand_id)
    if brand_ids:
        brand_ids =  ','.join(str(e) for e in brand_ids)
        params["brand_id"]=brand_ids

    supp_ids = this.data.get("supp_id")[:]
    if supp_id:
        if supp_id in supp_ids:
            supp_ids.remove(supp_id)
        else:
            supp_ids.append(supp_id)
    if supp_ids:
        supp_ids =  ','.join(str(e) for e in supp_ids)
        params["supp_id"]=supp_ids

    url="/ecom_products"
    if price and price != "clear_price":
        params["price"]=price
    if sort_by and sort_by != "clear_sort":
        params["sort_by"]=sort_by
    if params:
        url+="?"+urlencode(params)
    return url

register_helper("ecom_products_url",ecom_products_url)

def ifin(this, options, arg, lst=[]):
    if arg in lst:
        return options['fn'](this)
    else:
        return options['inverse'](this)

register_helper("ifin",ifin)

def active_dropdown(this, categ_id=None, class_name=None):
    if this.data.get("categ_id") and categ_id:
        categ = get_model("product.categ").browse(this.data.get("categ_id"))
        while categ.parent_id:
            if categ_id == categ.id:
                return class_name
            categ = categ.parent_id
    else:
        return ""

register_helper("active_dropdown",active_dropdown)
