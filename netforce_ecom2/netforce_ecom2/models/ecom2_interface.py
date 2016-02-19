from netforce.model import Model,fields,get_model

class EcomInterface(Model):
    _name="ecom2.interface"
    _store=False

    def sign_up(self,first_name,last_name,email,password,province_id,postal_code,address,subdistrict,context={}):
        print("EcomInterface.sign_up",first_name,last_name,email,password,province_id,postal_code,address)
        res=get_model("base.user").search([["email","=",email]])
        if res:
            raise Exception("User already exists with same email")
        res=get_model("contact").search([["email","=",email]])
        if res:
            raise Exception("Contact already exists with same email")
        vals={
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
        }
        contact_id=get_model("contact").create(vals)
        contact=get_model("contact").browse(contact_id)
        res=get_model("profile").search([["code","=","ECOM_CUSTOMER"]])
        if not res:
            raise Exception("Customer user profile not found")
        profile_id=res[0]
        vals={
            "name": "%s %s"%(first_name,last_name),
            "login": email,
            "profile_id": profile_id,
            "contact_id": contact_id,
            "password": password,
        }
        user_id=get_model("base.user").create(vals)
        addr_vals = {
        "first_name" :first_name,
        "last_name" : last_name,
        "province_id" : int(province_id),
        "type" : "billing",
        "postal_code" : postal_code, 
        "address" :address,
        "contact_id":contact_id,
        }
        subdistrict_id = int (subdistrict)
        if subdistrict_id:
            addr_vals['subdistrict_id'] = subdistrict_id
        addr = get_model("address").create(addr_vals)
        return {
            "user_id": user_id,
            "contact_id" : contact_id,
        }

    def login(self,email,password,context={}):
        print("EcomInterface.login",email,password)
        user_id=get_model("base.user").check_password(email,password)
        if not user_id:
            raise Exception("Invalid login")
        user=get_model("base.user").browse(user_id)
        contact=user.contact_id
        return {
            "user_id": user_id,
        }

EcomInterface.register()
