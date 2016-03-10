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

    def checkEmail(self,login,context={}):
        print("EcomInterface.CheckEmail",login)
        res = get_model("base.user").search_browse([['login','=',login]])
        if res:
            id = res[0].id
            reset_code = res.password_reset(id)
            vals = {
            "body":"Please click the link to reset the code: http://localhost/reset_password?code=%s"%reset_code,
            "from_addr":"demo@netforce.com",
            "subject" : "Paleo Reset Code",
            "type": "out",
            "state":"to_send",
            "to_addrs":login,
            "mailbox_id":1,
            }
            get_model('email.message').create(vals)            
        else: 
            raise Exception("Email Not Found");
        return 

    def set_new_password(self,reset_code,new_password,context={}):
        print("EcomInterface.set_new_password",reset_code,new_password) 
        res = get_model("base.user").search([["password_reset_code","=",reset_code]])
        if not res:
            raise Exception("Can not find user")
        user = get_model("base.user").browse(res[0])
        user.write({"password": new_password})

    def add_request_product_groups(self,contact_id,prod_group_id,context={}):
        print("Ecom2Interface.add_request_product_group",contact_id,prod_group_id)
        #contact_id=context.get("contact_id")
        contact=get_model("contact").browse(contact_id)
        contact.write({"request_product_groups":[("add",[prod_group_id])]})

    def remove_request_product_groups(self,contact_id,prod_group_id,context={}):
        print("Ecom2Interface.remove_request_product_group",contact_id,prod_group_id)
        #contact_id=context.get("contact_id")
        contact=get_model("contact").browse(contact_id)
        contact.write({"request_product_groups":[("remove",[prod_group_id])]})

    def add_exclude_product_groups(self,contact_id,prod_group_id,context={}):
        print("Ecom2Interface.exclude_product_groups",contact_id,prod_group_id)
        #contact_id=context.get("contact_id")
        contact=get_model("contact").browse(contact_id)
        contact.write({"exclude_product_groups":[("add",[prod_group_id])]})

    def remove_exclude_product_groups(self,contact_id,prod_group_id,context={}):
        print("Ecom2Interface.remove_request_product_group",contact_id,prod_group_id)
        #contact_id=context.get("contact_id")
        contact=get_model("contact").browse(contact_id)
        contact.write({"exclude_product_groups":[("remove",[prod_group_id])]})
EcomInterface.register()
