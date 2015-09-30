$(function(){

// Session
if(sessionStorage.countPage){
    sessionStorage.countPage=Number(sessionStorage.countPage)+1;
}else{
    sessionStorage.countPage=1;
}

// Global variable
App=function(){
    this.editOrder={
        cid:null,
        field: 'qty',
        value: 0,
    };
    this.orders=null;
    this.calTitle='';
    this.products=null;
    this.visiblePopover='';
    this.payments='';
    this.products=new ProductCollection();
    this.parkCid=0;
    this.showPop;
    this.mainInput='';
    this.isOnLine=false;
    this.changeRg=false;
    this.selectedShop={};
};

// Pagination
var number=1;
var pagination;
var lenPage=0;

var Register=Backbone.Model.extend({
    defaults: function(){
        return {
            number:'',
            created_date: timeStamp(),
            orders:new Order(),
            payments:new Payment(),
            discount: [],
            customerId: '',
        }
    },
});

var RegisterList=Backbone.Collection.extend({
    model: Register,
    localStorage: new Backbone.LocalStorage("register-collection-backbone"),
});

var Shop=Backbone.Model.extend({
    defaults: {
        shopId:'',
        name: '',
    }
});

var ShopList=Backbone.Collection.extend({
    model: Shop,
});

var Customer=Backbone.Model.extend({
    defaults: {
        name: '',
    }
});

var CustomerList=Backbone.Collection.extend({
    model: Customer, 
});

function createCustomer(mode, vals,cb){
    var args=[mode, vals];
    var opts={};
    rpc_execute("pos.interface","create_customer",args,opts,function(err) {
        if (cb) cb(err);
    });
}

var CustomerView=Backbone.View.extend({
    template: Handlebars.compile($("#customer-view-template").html()),
    events: {
        "click #cus-btn-save": "save",
        "click #cus-radio-female": "cusRadioFemale",
        "click #cus-radio-male": "cusRadioMale",
        "keypress #cus-birthday-mm": "digitValidate",
        "keypress #cus-birthday-dd": "digitValidate",
        "keypress #cus-birthday-yyyy": "digitValidate",
        "keypress #cus-zip": "digitValidate",
        "blur #cus-email": "cusEmail",
    },

    cusEmail: function(e){
        var email=this.$el.find("#cus-email").val();
        if(email){
            var res=this.validateEmail(email);
            if(!res){
                this.$el.find("#cus-email-error").html("Wrong Email");
                $(e.target).focus();
                return;
            }
        }
        this.$el.find("#cus-email-error").empty();
    },

    digitValidate: function(e){
    /*e.preventDefault();*/
        if (e.which != 8 && e.which != 0 && (e.which < 48 || e.which > 57)) {
         return false;
        }
    }, 

    cusRadioMale: function(e){
        e.preventDefault();
        this.$el.find("#cus-radio-female").attr("checked",false);
        this.$el.find("#cus-radio-male").attr("checked",true);
    },

    cusRadioFemale: function(e){
        e.preventDefault();
        this.$el.find("#cus-radio-female").attr("checked",true);
        this.$el.find("#cus-radio-male").attr("checked",false);
    },

    validateEmail: function(email){
            var reg = /^([A-Za-z0-9_\-\.])+\@([A-Za-z0-9_\-\.])+\.([A-Za-z]{2,4})$/;
            if(reg.test(email)){
                return true;
            }else{
                return false;
            }
    },

    save: function(e){
        e.preventDefault();
        var name=this.$el.find("#cus-first").val();
        var last=this.$el.find("#cus-last").val();
        var company=this.$el.find("#cus-company").val();
        var code=this.$el.find("#cus-code").val();
        var address1=this.$el.find("#cus-address1").val();
        var address2=this.$el.find("#cus-address2").val();
        var postal_code=this.$el.find("#cus-postal_code").val();
        var state=this.$el.find("#cus-state").val();
        var city=this.$el.find("#cus-city").val();
        var phone=this.$el.find("#cus-phone").val();
        var email=this.$el.find("#cus-email").val();
        var female=this.$el.find("#cus-radio-female").attr("checked");
        var male=this.$el.find("#cus-radio-male").attr("checked");
        var dd=this.$el.find("#cus-birthday-dd").val();
        var mm=this.$el.find("#cus-birthday-mm").val();
        var yyyy=this.$el.find("#cus-birthday-yyyy").val();
        /*var country=this.$el.find("#cus-country").find(":selected").val();*/
        var country_id=this.$el.find("#cus-country").find(":selected").attr("value");

        if(!name){
            this.$el.find("#cus-first").css("background-color", "#ff6666");
            return;
        }else{
            this.$el.find("#cus-first").css("background-color", "#d2d2ff");
        }

        if(!city){
            this.$el.find("#cus-city").css("background-color", "#ff6666");
            return;
        }else{
            this.$el.find("#cus-city").css("background-color", "#d2d2ff");
        }

        if(country_id==0){
            this.$el.find("#cus-country").css("background-color", "#ff6666");
            return ;
        }else{
            this.$el.find("#cus-country").css("background-color", "#d2d2ff");
        }
        
        this.$el.find("#cus-birthday-dd").css("background-color", "#ff6666");

        this.$el.find("#cus-birthday-mm").css("background-color", "white");
        this.$el.find("#cus-birthday-yyyy").css("background-color", "white");
        this.$el.find("#cus-birthday-dd").css("background-color", "white");

        var pass=false;

        if(dd){
            if(!mm){
                this.$el.find("#cus-birthday-mm").css("background-color", "#ff6666");
                pass=true;
            }
            if(!yyyy){
                this.$el.find("#cus-birthday-yyyy").css("background-color", "#ff6666");
                pass=true;
            }else if(yyyy < 1000){
                this.$el.find("#cus-birthday-yyyy").css("background-color", "#ff6666");
                pass=true;
            }
            if(pass) return;
        }

        if(mm){
            if(!dd){
                this.$el.find("#cus-birthday-dd").css("background-color", "#ff6666");
                pass=true;
            }
            if(!yyyy){
                this.$el.find("#cus-birthday-yyyy").css("background-color", "#ff6666");
                pass=true;
            }else if(yyyy < 1000){
                this.$el.find("#cus-birthday-yyyy").css("background-color", "#ff6666");
                pass=true;
            }
            if(pass) return;
        }

        if(yyyy){
            if(!dd){
                this.$el.find("#cus-birthday-dd").css("background-color", "#ff6666");
                pass=true;
            }
            if(!mm){
                this.$el.find("#cus-birthday-mm").css("background-color", "#ff6666");
                pass=true;
            }
            if(pass) return;
        }
        
        var address=[];
        var mode=this.model.mode;
        if (city && country_id){
            address=[[mode,
                    {
                        country_id: eval(country_id),
                        city: city,
                        postal_code: postal_code,
                        street:address1,
                        sub_district: address2,
                        district: state,
                    }, 
                ]];
        }

        var birthDay=null;
        if (yyyy && mm && dd){ birthDay=new Date(yyyy+'-'+mm+'-'+dd); }

        var vals={
            name: name,
            code: code,
            last_name: last,
            customer: true,
            industry: company, // XXX
            phone: phone,
            fax: '',
            email: email,
            birth_date: birthDay,
            addresses: address,
        }

        createCustomer(mode, vals,function(err){
            if(err){
                alert("ERROR " + err['message']);
            }else{
                $('.modal').modal('hide'); 

                function cb(){
                    var customer=App.customer.findWhere({name: name});
                    var customer=customer.toJSON();
                    App.order.customer=customer;
                    var msg="No Customer Selected";
                    if(customer){
                        msg='<a href="#" style="text-decoration:underline;">'+ (customer ? customer.name : '') +"</a>";
                        App.order.customer=customer;
                    }
                    App.view.$el.find("#order-cus-msg").html(msg);
                    App.view.$el.find("#customer-input").html(name);
                }
                search_customer(name,cb);
            }
        });

        $("#customer-input").val(name);
    },

    render:function(){
        var that=this;

        download_country(function(data){
            var country_id=that.model.country_id;
            var ctx=that.model;
            var html=that.template(ctx);
            that.$el.html(html);
            $("#content").append(that.el);

            var modal=that.$el.find(".modal");
            modal.modal();

            var $country=that.$el.find("#cus-country");
            $country.empty();
            $country.append('<option value="country"> Select Country </option>');
            _.each(data,function(d){
                var id=d.id;
                var code=d.code || "";
                var name=d.name || "";
                $country.append('<option value="'+ id + '">' + name + '</option>');
            });
            // FIXME use country_id to set Country name
            if(country_id){
                $country.val(country_id);
            }
        });
    },

});

var ProgressBarView=Backbone.View.extend({
    template: Handlebars.compile($("#progressbar-view-template").html()),
    render:function(){
        var ctx={};
        var html=this.template(ctx);
        this.$el.html(html);
        $("#content").append(this.el);
        var modal=this.$el.find(".modal");
        modal.modal({ backdrop: 'static' });
    },

});

var CloseRegisterview=Backbone.View.extend({
    template: Handlebars.compile($("#close-register-view-template").html()),
    id: "close-register-view-id",
    events: {
        "click .btn-close-register": "click_close_register"
    },

    render:function(){
        var ctx={};
        var html=this.template(ctx);
        this.$el.html(html);
        var shop=JSON.parse(localStorage.getItem('shop'));
        var shopName=shop.shopName;
        var registerName=shop.registerName;
        var openRegisterDate=shop.openRegisterDate;
        var closeDate=timeStamp();
        this.$el.find("#close-register-shop").html(shopName);
        this.$el.find("#close-register-shop-register").html(registerName);
        this.$el.find("#close-open-date").html(openRegisterDate);
        this.$el.find("#close-closed-date").html(closeDate);

        var totalOrder=0;
        var totalPayment=0;
        var totalDiscount=0;
        var totalCash=0;
        var totalCredit=0;
        var collection=new RegisterList();

        var shop=JSON.parse(localStorage.getItem('shop')); 
        var registerId=shop.registerId;

        collection.fetch();
        collection.each(function(model){
            var vals=model.toJSON();
            if(vals.registerId == registerId){
                var orders=vals.orders;
                for(var i=0; i< orders.length;i++){
                    if(orders[i]['name']=='Discount'){
                        totalDiscount+= orders[i]['total'] || 0.0;
                    }else{
                        totalOrder+=orders[i]['total'] || 0.0;
                    }
                }

                var payments=vals.payments;
                for(var i=0; i< payments.length; i++){
                    var amt=Number(payments[i]['amt']) || 0.0; 
                    var name=payments[i]['name'] || "";
                    var pay_method=payments[i]['pay_method'] || "";

                    if(name=='Cash'){
                        totalCash+=amt
                    }else if(name=='Credit Card'){
                        totalCredit+=amt
                    }else{
                        if(pay_method=="Cash"){
                            totalCash+=amt;
                        }else{
                            totalCredit+=amt
                        }
                    }
                }
            }// if
        });

        totalPayment=totalCredit+totalCash;
        var saleLine=this.$el.find("#close-sale-line");
        tr='';
        tr+='<tr><td>New Sales</td><td class="currency">'+totalOrder+'</td></tr>';
        tr+='<tr><td>Discount</td><td class="currency">'+totalDiscount+'</td></tr>';
        tr+='<tr><td>Payments</td><td class="currency">'+totalPayment+'</td></tr>';
        saleLine.empty();
        saleLine.append(tr);

        var symbol=JSON.parse(localStorage.getItem('symbol'));
        if(symbol){
            symbol=symbol.sign;
        }

        var that=this;
        this.$el.find("#close-cash-total").html(totalCash);
        this.$el.find("#close-input-cash-total").val(totalCash);
        this.$el.find("#close-credit-total").html(totalCredit);
        this.$el.find("#close-input-credit-total").val(totalCredit);
        that.$el.find(".currency").formatCurrency({ symbol: symbol, colorize:true });

        this.$el.find("#close-print").click(function(e){
            e.preventDefault();
            window.print();
        });
    },

    click_close_register: function(e) {
        e.preventDefault();

        var ans=confirm("Warning!! This action will copy your order to the backend. It will create sale order, account invoice and goods issues. \nAre you sure to close this register?")
        if(!ans){ return }

        e.stopPropagation();
        var that=this;

        var progress=new ProgressBarView({model: {len: 100}});
        progress.render();

        function resetProgress(){
            progress.$el.find(".modal").hide();
            $(".in").remove();
        }

        upload_orders(function(err) {
            if (err) {
                resetProgress();
                var msg=err['message'];
                alert("ERROR [BACKEND]:  "+ msg);
                resetProgress();
                return;
            }else{
            /*alert("Upload orders completed!!!");*/
                resetProgress();

                var regList=new RegisterList();
                regList.fetch();
                for(var i=0; i< App.regCidLine.length; i++){
                    var id=App.regCidLine[i];
                    var model=regList.get(id);
                    model.destroy();
                    console.log('delete ', model.toJSON()); 
                }
                if(App.order){
                    App.order.reset();
                    App.order.payment.reset();
                    App.order.note='';
                }
                that.render();
            }

        });

    }
});

function upload_orders(cb) {
    console.log("upload_orders");
    // XXX save order and then send to backen
    if(!localStorage.shop){ return;}
    var orders=[];
    var shop=JSON.parse(localStorage.getItem('shop'));
    var shopId=shop.shopId;
    var registerId=shop.registerId;
    var customerId='';
    var regList=new RegisterList();
    regList.fetch();
    App.regCidLine=[];

    function compare(a,b){
        var res=-1;
        if (a.qty < b.qty){
            res=1;
        }
        return res;
    }
     
    var index=1;
    regList.each(function(reg){
        index++;
        if(reg.get("registerId")==registerId){
            var order={};
            var orderLine=[];
            customerId=reg.get('customerId');
            var vals=reg.get('orders');
            // Discount should be the last of lines
            vals.sort(compare);
            console.log(":::> reg ", reg);
            for(var i=0; i<vals.length; i++){
                productId=vals[i]['productId'];
                qty=vals[i]['qty'] || 0;
                price=vals[i]['price'] || 0.0;
                name='';
                if(qty < 0 && productId == ''){
                    name='Discount';
                    price=price*qty;
                    qty=qty*-1;
                }
                orderLine.push({
                    product_id: productId,
                    qty: qty,
                    unit_price: price,
                    name: name,
                })
            }
            App.regCidLine.push(reg.id);
            order={
                date: timeStamp(),
                lines: orderLine,
                contact_id: customerId,
                shop_id: shopId,
            }

            order.is_credit=false;
            var payments=reg.get("payments");
            for(var i=0;i<payments.length;i++){
                if (payments[i].pay_method=='Credit Card'){
                    order.is_credit=true;
                    break;
                }
            }
            orders.push(order);

        }
    });

    var opts={};
    console.log("uploading...", orders);
    rpc_execute("pos.interface","upload_orders",[orders],opts,function(err) {
        console.log("finished uploading orders");
        if (cb) cb(err);
    });

}

var Product=Backbone.Model.extend({
    defaults:function(){
        return {
            productId: null,
            code:'',
            name:'',
            qty:0,
            price:0.0,
            type: 'add',
        }
    },
});

var ProductCollection=Backbone.Collection.extend({
    model: Product,
    localStorage: new Backbone.LocalStorage("product-collection-backbone"),
});

var ProductView=Backbone.View.extend({
    template: Handlebars.compile($("#product-view-template").html()),
    render: function(){
        var ctx={};
        var html=this.template(ctx);
        this.$el.html(html);
        $el=this.$el;
        var product=this.model.toJSON();
        $el.find("#product-name").text(product.name);
        $el.find("#product-code").text(product.code);
        $el.find("#product-price").text("$"+toFixed(product.price,2));
    },
});


function rpc_execute(model,method,args,opts,cb) {
    console.log("RPC",model,method,args,opts);
    var params=[model,method];
    params.push(args);
    if (opts) {
        params.push(opts);
    }
    $.ajax({
        url: "/json_rpc",
        type: "POST",
        data: JSON.stringify({
            id: (new Date()).getTime(),
            method: "execute",
            params: params
        }),
        dataType: "json",
        contentType: "application/x-www-form-urlencoded; charset=UTF-8",
        success: function(data) {
            if (data.error) {
                console.log("RPC ERROR",model,method,data.error.message);
            } else {
                console.log("RPC OK", model, method);
            }
            if (cb) {
                cb(data.error,data.result);
            }
        },
        error: function() {
            console.log("RPC ERROR",model,method);
        }
    });
}

function search_customer(name, cb) {
    if(!name){ name='';}
    var args=[name];
    var opts={};
    rpc_execute("pos.interface","search_customer",args,opts,function(err,data) {
        if(err) {
            alert("ERROR" + err['message']);
            return;
        }
        App.customer=new CustomerList(data);
        if(cb) cb();
    });

}

function download_country(cb) {
    if(!name){ name='';}
    var args=[name];
    var opts={};
    rpc_execute("pos.interface","download_country",args,opts,function(err,data) {
        if(err) {
            alert("ERROR" + err['message']);
            return;
        }
        if(cb) cb(data);
    });
}

function download_local_sign(cb) {
    var args=[];
    var opts={};
    rpc_execute("pos.interface","get_local_sign",args,opts,function(err,data) {
        if(err) {
            alert("ERROR" + err['message']);
            return;
        }
        if(cb) cb(data);
    });
}

function download_company(cb) {
    var shop=JSON.parse(localStorage.getItem('shop')); 
    var args=[];
    var opts={shop:shop};
    rpc_execute("pos.interface","get_company",args,opts,function(err,data) {
        if(err) {
            alert("ERROR" + err['message']);
            return;
        }
        App.company=data;
        if(cb) cb();
    });
}

function download_customer(cb) {
    var args=[];
    var opts={};
    rpc_execute("pos.interface","download_customer",args,opts,function(err,data) {
        if(err) {
            alert("ERROR" + err['message']);
            return;
        }
        if(cb) cb();
    });
}

function loadShopMenu() {
        var menuList='';
        App.shops.each(function(shop){
            var menu ='<li><a href="#" class="pos-shop-group-menu"';
            menu+='shop-id='+ shop.get('id')+"";
            menu+=' >';
            menu+=shop.get('name');
            menu+='</a></li>';
            menuList+=menu;
        });

        $("#pos-shop-menu").empty();
        $("#pos-shop-menu").append(menuList);

        $(".pos-shop-group-menu").click(function(e){
            e.preventDefault();

            App.mainInput='';
            // pagination
            number=1;

            var self=$(this);
            var shopId=self.attr("shop-id");

            var shop=App.shops.get(shopId);

            var name=self.text();

            var registers=shop.get('registers');
            var registerId='';
            var vals={
                shopId: shopId,
                shopName: name,
            }
            App.selectedShop=vals;

            $(".modal").remove();
            var register=new ShopRegisterView({collection: new ShopRegisterList(registers)});
            register.render();
        });

        var vals=JSON.parse(localStorage.getItem('shop')); 
        if(!vals){
            alert("No shop found, please select or create it from the backend.");
            return;
        }
        if(vals!=null){
            $("#pos-shop").html(vals.shopName);
            $(".pos-shop-register").html(vals.registerName);
            download_product_by_register(renderProduct);
        }
}

function download_shop(cb) {
    var args=[];
    var opts={};
    rpc_execute("pos.interface","download_shop",args,opts,function(err,data) {
        if (err) {
            alert("ERROR" + err['message']);
            return;
        } 
        App.shops=new ShopList();
        _.each(data,function(shop){
            App.shops.add(data);
        });
        if(cb){ cb()}
    });
}

function download_product_by_register(cb) {
    console.log("download_product_by_register");
    var shop=JSON.parse(localStorage.getItem('shop'));
    var registerId=shop.registerId;
    var args=[registerId];
    var opts={};
    rpc_execute("pos.interface","download_product_by_register",args,opts,function(err,data) {
        console.log("finished downloading products");
        App.products=new ProductCollection();
        App.products.fetch();

        // FIXME destroy all model in collection
        var model;
        while(model=App.products.first()){
            model.destroy();
        }

        _.each(data,function(prod) {
            var vals={
                name: prod.name,
                productId: prod.id,
                code: prod.code,
                price: prod.sale_price,
            };
            var product=new Product(vals);
            App.products.add(product);
            product.save();
        });
        if (cb) cb();
    });
}

function download_products(cb) {
    console.log("download_products");
    if(!localStorage.shop){
        alert("Please select Shop!");
        return;
    }
    var shop=JSON.parse(localStorage.getItem('shop'));
    var shop_id=shop.shopId;
    var args=[shop_id];
    var opts={};
    rpc_execute("pos.interface","download_products",args,opts,function(err,data) {
        console.log("finished downloading products");
        App.products=new ProductCollection();
        App.products.fetch();

        // FIXME destroy all model in collection
        var model;
        while(model=App.products.first()){
            model.destroy();
        }

        _.each(data,function(prod) {
            var vals={
                name: prod.name,
                productId: prod.id,
                code: prod.code,
                price: prod.sale_price,
            };
            var product=new Product(vals);
            App.products.add(product);
            product.save();
        });
        if (cb) cb();
    });
}

var PaymentLine=Backbone.Model.extend({
    defaults: function(){
        return {
            pay_method:'Cash',
            name: '',
            amt: 0,
        };
    },

});

var PaymentView=Backbone.View.extend({
    template: Handlebars.compile($("#payment-view-template").html()),
    render:function(){
        var model=this.model.toJSON();
        var html=this.template(model);
        this.$el.html(html);
    }
});

var ShopRegister=Backbone.Model.extend({
    defaults: {
        name: '',
    }
});

var ShopRegisterList=Backbone.Collection.extend({
    model: Register,
});

var ShopView=Backbone.View.extend({
    template: Handlebars.compile($("#shop-view-template").html()),
    id: "shop-view-id",

    events:{
        "click .shop-item":"shopItem",
    },

    shopItem: function(e){
        e.preventDefault();
    },

    render:function(){
        var ctx={};
        var html=this.template(ctx);
        this.$el.html(html);
        $("#content").append(this.el);
        var modal=this.$el.find(".modal");
        modal.modal({ backdrop: 'static' });
    },

});

var ShopRegisterView=Backbone.View.extend({
    template: Handlebars.compile($("#shop-register-view-template").html()),
    id: "register-view-id",

    events:{
        "click .register-item":"regItem",
    },

    regItem: function(e){
        e.preventDefault();
        var id=$(e.target).parents("tr").attr("data-id");
        var name=$(e.target).html();

        // render & download product
        // clear order, payment, customer, note, park(reset & copy to somewhere)
        if(!App.order){ App.order=new Order();}
        App.order.reset();
        App.order.note='';
        App.order.customer={};
        App.order.payment.reset();

        // read shop
        var vals=App.selectedShop;
        $("#pos-shop").text(vals.shopName);
        vals.registerId=id;
        vals.registerName=name;
        vals.openRegisterDate=timeStamp();

        $(".pos-shop-register").text(name);

        // store shop
        localStorage.setItem('shop',JSON.stringify(vals));

        this.$el.find('.modal').modal("hide");

        var page=Backbone.history.fragment;
        var router=new PosRouter;
        if(page=='close_register'){
            location.reload();
        }else if(page=='retrieve_sale'){
            location.reload();
        }else{
            App.view.render();
        }
        download_product_by_register(renderProduct);
    },

    render:function(){
        var collection=this.collection;
        var ctx={
            line: collection.toJSON(),
        };
        var html=this.template(ctx);
        this.$el.html(html);
        $("#content").append(this.el);
        var modal=this.$el.find(".modal");
        modal.modal({ backdrop: 'static' });
    },
});

var ReceiptView=Backbone.View.extend({
    template: Handlebars.compile($("#receipt-view-template").html()),
    render: function() {
        var that=this;
        var ctx={};
        var html=that.template(ctx);
        that.$el.html(html);
    },
});

var Payment=Backbone.Collection.extend({
    model: PaymentLine,
    localStorage: new Backbone.LocalStorage("payment-collection-backbone"),
});

var PaymentListView=Backbone.View.extend({
    template: Handlebars.compile($("#payment-list-view-template").html()),
    id:"mypayment",

    render: function() {
        var that=this;
        var ctx={};
        var html=that.template(ctx);
        that.$el.html(html);
        var total=0;

        this.collection.each(function(model){
            var amt=model.get('amt');
            amt=toFixed(amt,2);
            // FIXME parse string to float
            amt=parseFloat(amt);
            total+=amt;
            model.set({amt: amt});
            var view=new PaymentView({model:model});
            view.render();
            that.$el.find("#payment-line").append(view.el);
        });
       
        var totalOrder=0.0;
        App.order.each(function(line){
            totalOrder+=line.get('total');
        });

        total=totalOrder-total;
        var symbol=JSON.parse(localStorage.getItem('symbol'));
        if(symbol){
            symbol=symbol.sign;
        }

        that.$el.find("#total-payment").text(total).formatCurrency({symbol: symbol, colorize:true });

        if(total<0){
            that.$el.find("#total-payment").css("color","red");
        }
    },
});

var OrderLine=Backbone.Model.extend({
    defaults:function(){
        return {
            productCid: null,
            productId:null,
            name: '',
            qty: 0,
            price: 0.0,
            seq: 0, // Use to sort order
        }
    },
});

var OrderLineView=Backbone.View.extend({
    template: Handlebars.compile($("#order-line-view-template").html()),
    tagName:"tr",
    className: "order-line-group",
    events:{
        "click .edit-price":"editPrice",
        "click .order-line-detail":"orderDetail",
        "click .edit-qty":"editQty",
        "mouseenter .edit-price, .edit-qty":"mouseEnter",
        "mouseleave .edit-price, .edit-qty":"mouseLeave",
        "mouseenter .icon-remove":"iconRemoveMouseEnter",
        "mouseleave .icon-remove":"iconRemoveMouseLeave",
    },
    
    orderDetail: function(e){
        e.preventDefault();
        var name=$(e.target).text();
        var product=App.products.findWhere({name: name});
        if(!product){ return; }
        var view=new ProductView({model: product});
        view.render();
        $("body").append(view.el);
        $el=view.$el;
        $el.find(".modal").modal();
    },

    iconRemoveMouseEnter:function(e){
        var span=$(e.target).parents("span.badge");
        span.css("background-color","#c61b2a");
    },

    iconRemoveMouseLeave:function(e){
        var span=$(e.target).parents("span.badge");
        span.css("background-color","#c47775");
    },

    mouseEnter: function(e){
        $(e.target).addClass("circle");
    },

    mouseLeave: function(e){
        $(e.target).removeClass("circle");
    },

    editPrice: function(e){
        e.preventDefault();
        $(e.target).addClass("circle");

        var tr=$(e.target).parents("tr");
        var cid=tr.find("td:first").text();
        var value=$(e.target).text();
        value=value.replace("@","");
        var vals={
            cid: cid,
            field: 'price',
            value: value.replace("@",""),
        }
        App.editOrder=vals;
        var calRes=$("#cal-result");
        calRes.val(value);
        calRes.focus();
        calRes.select();

        $(".btn-percent").addClass("btn-percent-hide");
        $(".btn-del").removeClass("btn-del-hide");
    },

    editQty: function(e){
        e.preventDefault();
        $(e.target).addClass("circle");

        var tr=$(e.target).parents("tr");
        var cid=tr.find("td:first").text();
        var value=$(e.target).text();
        var vals={
            cid: cid,
            field: 'qty',
            value: value,
        }

        App.editOrder=vals;
        var calRes=$("#cal-result");
        calRes.val(value);
        calRes.focus();
        calRes.select();

        $(".btn-percent").addClass("btn-percent-hide");
        $(".btn-del").removeClass("btn-del-hide");
    },

    render:function(){
        var order=this.model.toJSON();
        order.cid=this.model.cid;
        order.price=toFixed(order.price,2);
        order.total=toFixed(order.total,2);
        var html=this.template(order);
        this.$el.html(html);
        this.$el.find(".order-line-total").formatCurrency({symbol: ""});
    }
});

var Order=Backbone.Collection.extend({
    model: OrderLine,
    payment: new Payment(),
    note: '',
    customer:{},
    localStorage: new Backbone.LocalStorage("order-collection-backbone"),
});

var OrderView=Backbone.View.extend({
    id: "order-view-id",
    template: Handlebars.compile($("#order-view-template").html()),
    events:{
        "click #park-order":"parkOrder",
        "click #note-order":"noteOrder",
        "click #pay-order":"payOrder",
        "keyup #main-input":"mainInput",
        "click #void-order":"voidOrder",
        "click #discount-order":"discOrder",
        "click .add-order":"addOrder",
        "click .remove-order":"removeOrder",
        "click .product-item": "addProduct2Order",
        "click .previous":"previous",
        "click .next":"next",
        "click .order-add-customer":"addCustomer",
        "keyup #customer-input": "customerInput",
        "click #order-cus-msg": "editCustomer",
    },
    
    editCustomer: function(e){
        e.preventDefault();
        var cusName=this.$el.find("#order-cus-msg > a").html();
        if(cusName){
            function cb(){
                var customer=App.customer.findWhere({name: cusName});
                var customer=customer.toJSON();
                var address=customer.address;
                var birth_date=customer.birth_date;
                var vals={
                    first: cusName,
                    last: customer.last_name,
                    code: customer.code,
                    company: customer.industry,
                    email: customer.email,
                    phone: customer.phone,
                    mode: 'write',
                };

                if (birth_date){
                    var date=birth_date.split('-');    
                    if(date.length == 3){
                        var yyyy=date[0];
                        var mm=date[1];
                        var dd=date[2];
                        vals.birthDay_yyyy=yyyy;
                        vals.birthDay_mm=mm;
                        vals.birthDay_dd=dd;
                    }
                }
                if (address){
                    vals.address1=address.street;
                    vals.address2=address.sub_district;
                    vals.postal_code=address.postal_code;
                    vals.state=address.district;
                    vals.city=address.city;

                    //'country_id': [1, 'Thailand']
                    if(address.country_id.length == 2){
                        vals.country_id=address.country_id[0];
                    }
                }
                var view=new CustomerView({model: vals});
                view.render();
                $("body").append(view.el);
                view.$el.find(".modal").modal();
            }

            search_customer(cusName, cb)
        }
    },

    customerInput: function(e){
        e.preventDefault();
        var name=$(e.target).val();
        var isKey=e.keyCode==13 || e.keyCode == 8;
        if (isKey && name==''){
            App.order.customer={};
            var msg="No Customer Selected";
            $el.find("#order-cus-msg").html(msg);
        };
    },

    addCustomer: function(e){
        e.preventDefault();
        var cusName=this.$el.find("#customer-input").val();
        var vals={
            first: cusName,
            last: '',
            code: '',
            company: '',
            address1: '',
            address2: '',
            postal_code: '',
            state: '',
            email: '',
            phone: '',
            city: '',
            country: '',
            birthDay_mm: '',
            birthDay_dd: '',
            birthDay_yyyy: '',
            country_id: '',
            mode: 'create', // XXX
        };

        var view=new CustomerView({model: vals});
        view.render();
        $("body").append(view.el);
        view.$el.find(".modal").modal();
    },

    previous: function(e){
        e.preventDefault();
        number--;
        if(number<=1){ number=1; }
        loadProduct(number);
    },

    next: function(e){
        e.preventDefault();
        number++;
        if(number>=lenPage){ number=lenPage; }
        loadProduct(number);
    },

    discOrder: function(e){
        e.preventDefault();
        $(".btn-percent").removeClass("btn-percent-hide");
        $(".btn-del").removeClass("btn-del-hide");
    },

    voidOrder: function(e){
         var conf = confirm("This will clear the current sale. All items and payments on this sale will be lost. \n Are you sure?");
         if(conf==true){
            if(App.parkId){
                var pkcol=new ParkCollection();
                pkcol.fetch();
                var pk=pkcol.findWhere({id: App.parkId});
                if(pk){
                    console.log('destroy', pk.toJSON());
                    pk.destroy();
                    // reset
                    App.parkId=undefined;
                    App.note='';
                }
            }

            App.order=App.order.reset();
            App.order.customer={};
            App.order.payment=App.order.payment.reset();
            App.view.render();
            $("#main-input").val('');
            $("#main-input").focus();
         }
    },

    addProduct2Order:function(e){
        var cid=$(e.target).attr("data-cid");
        var products=App.products.where({code: cid});
        var product=products[0].toJSON();
        $("#main-input").val(product.name);
        this.addOrder(e);
    },

    removeOrder:function(e){
        e.preventDefault();
        var tr=$(e.target).parents("tr");
        var cid=tr.find("td:first").text();
        var order=this.collection.get(cid);
        this.collection.remove(order);
        this.render();
    },

    mainInput: function(e){
       e.preventDefault();
       if (e.keyCode==13 && (App.isBar || App.isBar==undefined)) {
           this.addOrder(e);
       };
       App.isBar=undefined;
    },

    payOrder: function(e){
        var view=new OrderPayView({collection:this.collection});
        view.render();
        $("body").append(view.el);
        view.$el.find(".modal").modal();
    },

    parkOrder:function(e){
      var view=new OrderParkView({collection:this.collection});
      view.render();
      $("body").append(view.el);
      view.$el.find(".modal").modal();
    },

    noteOrder: function(e){
        var view=new OrderNoteView({collection:this.collection});
        view.render();
        $("body").append(view.el);
        view.$el.find(".modal").modal();
    },

    addOrder: function(e){
        e.preventDefault();
        // FIXME barcode
        App.isBar=true;
        var val=$("#main-input").val();
        App.mainInput=val;

        var product=App.products.findWhere({name: val});

        if(!product){
            product=App.products.findWhere({code: val});
        }

        if(!product){
            console.log("Missing Product");
            $("#main-input").focus();
            $("#main-input").select();
        }else{
            var vals={
                productCid: product.cid,
                productId: product.get('productId'),
                name: product.get('name'),
                qty: 1,
                price: product.get('price'),
                total: product.get('price'),
            }
            var line=new OrderLine(vals);
            var order=this.collection;

            // sort order
            if(order.length < 1){
                line.set({seq: 1});
            }else{
                var lastOrder=order.min(function(line){ return line.get('seq');});
                lastOrder=lastOrder.toJSON();
                var nextSeq=(lastOrder.seq)*-1;
                nextSeq++;
                line.set({seq: -nextSeq});
            }
            order.add(line);
            this.render();
            /*this.$el.find("#order-lines").find("tr:first").fadeOut("fast").fadeIn();*/
        }
    },
    
    showSummary: function(){
        var order=this.collection;
        var payment=order.payment;
        var $el=this.$el;
        var $payment=$el.find("#order-payment");
        var $paymentLine=$el.find("#order-payment-line");
        var $container=$el.find("#order-container");
        var $productList=$el.find("#product-list");
        /*// number of payment line*/
        // clear line && reset size
        $paymentLine.empty();

        var trSize=37;
        $container.css({
                "height": 350,
                });
        $payment.css({
                "maxHeight": 215, 
                "height": 215, 
                });
        $productList.css({
                "height": 595, 
                "marginTop": -400, 
                });

        var limit=4;
        var count=0;
        payment.each(function(line){
            vals=line.toJSON();
            var symbol=JSON.parse(localStorage.getItem('symbol')) || '';
            if(symbol){
                symbol=symbol.sign;
            }
            var amt=symbol+toFixed(vals.amt,2);

            if(count<limit){
                $paymentLine.append('<tr><td>'+vals.name+'</td><td style="text-align: right; width: 120px;">'+amt+'</td></tr>');

                var max=parseInt($payment.css("maxHeight"));
                $payment.css("maxHeight",max+trSize);
                $payment.height($payment.height()+trSize);
                
                $container.height($container.height()-trSize);

                var marginTopProduct=parseInt($productList.css("marginTop"));
                $productList.css("marginTop",marginTopProduct+trSize);
            }else{
                $paymentLine.append('<tr><td>'+vals.name+'</td><td style="text-align: right; width: 120px;">'+amt+'</td></tr>');
                $payment.height($payment.height()+trSize);
                var max=parseInt($payment.css("maxHeight"));
                $payment.css("maxHeight",max+trSize);
            }
            count++;
        });

    },

    render: function() {
        var symbol=JSON.parse(localStorage.getItem('symbol')) || '$';
        if(symbol){
            symbol=symbol.sign;
        }
        var that=this;
        App.view=that;
        var order=this.collection;
        var ctx={};
        var html=this.template(ctx);
        that.$el.html(html);
        var $el=that.$el;
        var subTotal=0;
        var taxAmt=0;

        order.each(function(line){
            var icon='remove';
            var vals=line.toJSON();
            var total=vals.qty*vals.price;
            subTotal+=total;
            var nTotal=total*-1;
            if(total<0){
                isPlus=false;
            }else{
                isPlus=true;
            }

            line.set({icon:icon, total: total, nTotal: toFixed(nTotal,2), isPlus:isPlus});
            var view=new OrderLineView({model:line});
            view.render();
            var $line=$el.find("#order-lines");
            $line.append(view.el);
            $line.find("tr:last").css("border-bottom","1px solid #dddddd");
        });

        var totalAmt=subTotal+taxAmt;
        $el.find("#order-sub-total").text(subTotal).formatCurrency({symbol: symbol, colorize:true });
        $el.find("#order-tax").text(taxAmt).formatCurrency({symbol: symbol, colorize:true });
        $el.find("#order-total").text(totalAmt).formatCurrency({symbol: symbol, colorize:true });

        var paidAmt=0;
        order.payment.each(function(line){
            vals=line.toJSON();
            paidAmt+=vals.amt;
        });
        $el.find("#order-to-pay").text(totalAmt-paidAmt).formatCurrency({symbol: symbol, colorize:true });
        
        this.showSummary();

        $con=$el.find("#order-container");

        // Summary & amount of order should be the same
        var $sum=$el.find("#order-summary");
        if($con.get(0).scrollHeight > $con.height()){
            $sum.css("marginLeft",-100);
        }else{
            $sum.css("marginLeft",-80);
        }

        // XXX focus select product first
        $el.find("#main-input").val(App.mainInput);
        $el.find("#main-input").focus();
        $el.find("#main-input").select();

        // Show calculator for edit qty & unit price
        $el.find("[rel='popover']").popover({
            content: function(){
                    var calView=new CalculatorView();
                    calView.render();
                    return calView.el;
            }
            ,
            placement: function(e) {
                if(App.calTitle=='Disc'){ return 'top'; }
                return 'right';
            },
            html: true,
            container: 'body',
            trigger: 'manual',

        }).click(function(e){
            // FIXME click other position should remove popover
            var top=$(this).offset().top;
            var left=$(this).offset().left;
            var position=top*left;
            if (App.position==undefined || App.position==position){
                // click them-self
                $(this).popover("toggle");     
            }else{
                $(".popover").toggleClass("in").remove();                                                                                                   
                $(this).popover("show");     
            }
            App.position=position;
        }).on("show.bs.popover",function(){
            var title='';
            var edit_qty=$(this).hasClass("edit-qty");
            var disc=$(this).text();
            if(edit_qty){
                title='Quantity';
            }else if(disc=='Disc'){
                title='Disc';
            }else{
                title='Price';
            }
            App.calTitle=title;
        });

        // Auto complete
        $el.find('#main-input').typeahead({
            source: function(query,process){
                vals=[];
                map={};
                var that=this;
                var products=[];
                if (App.products!=null){
                    products=App.products.toJSON();
                }

                $.each(products,function(index,model){
                    map[model.name]=model
                    vals.push(model.name);
                });

                process(vals);

            },

            matcher: function(item) {
                if (item.toLowerCase().indexOf(this.query.trim().toLowerCase()) != -1) {
                    return true;
                }
            },

            highlighter: function(item){ return map[item].name; },
                // after select item
            updater: function(item){
                return item;
            },
        });
        
        $el.find('#customer-input').typeahead({
            source: function(query,process){
                vals=[];
                map={};
                var customers=[];

                if(!App.isOnLine){
                   alert("Internet not available"); 
                   return;
                }
                
                function cb(){
                    customers=App.customer.toJSON();
                    $.each(customers,function(index,model){
                        map[model.name]=model
                        vals.push(model.name);
                    });
                    process(vals);
                }
                search_customer(query,cb);
            },

            matcher: function(item) {
                if (item.toLowerCase().indexOf(this.query.trim().toLowerCase()) != -1) {
                    return true;
                }
            },

            highlighter: function(item){ return map[item].name; },
                // after select item
            updater: function(item){
                var customer=App.customer.findWhere({name: item});
                var customer=customer.toJSON();
                that.collection.customer=customer;
                var msg="No Customer Selected";
                if(customer){
                    msg='<a href="#" style="text-decoration:underline;">'+ (customer ? customer.name : '') +"</a>";
                    App.order.customer=customer;
                }
                $el.find("#order-cus-msg").html(msg);
                return item;
            },
        });
       
        // XXX remove popover if not necessary
        $("body").click(function(e){
            var res=$(e.target).attr("rel")
            if(res!='popover' && !App.showPop){
                $(".popover").toggleClass("in").remove();                                                                                                   
            }
        });


        var cusMsg='No Customer Selected';
        var customer=App.order.customer;
        var customerName='';

        if(customer.id){
            cusMsg='<a href="#" style="text-decoration:underline;">'+(customer ? customer.name : '')+"</a>";
            customerName=customer.name;
        }
        $el.find("#customer-input").val(customerName);
        $el.find("#order-cus-msg").html(cusMsg);

        renderProduct();
    },
    
});

function loadProduct(number){
        if(!pagination){ return; }
        if(pagination.length < 1){ return; }

        number--;
        var page=pagination;
        var begin=page[number][0];
        var count=page[number].length;
        var end=page[number][count-1]+1;

        var col=4;
        var tr='';
        var row='';
        var products=App.products.slice(begin,end);
       
        var isLast=false;
        if (number==lenPage-1){ isLast=true; }

        for(var nrow=0; nrow < products.length; nrow++){
            var product=products[nrow].toJSON();
            var button='';
            var res=(nrow % (col));
            if(res==0){
               button="<button type='button' data-cid='"+product.code+"' class='product-item prod-item-first'>"+ product.name+"</button>";
            }else{
               button="<button type='button' data-cid='"+product.code+"' class='product-item prod-item-next'>"+ product.name+"</button>";
            }
            if(nrow % col == 0 && nrow != 0){
                tr+='<tr>'+row+'</tr>';
                //row='<td>'+ button + '</td>';
                if(isLast){
                    row='<td style="width: 147px;">'+ button + '</td>';
                }else{
                    row='<td>'+ button + '</td>';
                }
            }else{
                /*row+='<td>'+ button + '</td>';*/
                if(isLast){
                    row+='<td style="width: 147px;">'+ button + '</td>';
                }else{
                    row+='<td>'+ button + '</td>';
                }
            }
        }

        tr+='<tr>'+row+'</tr>';

        if(App.view){
            $el=App.view.$el;
            $el.find("#list-product").empty();
            $el.find("#list-product").append(tr);
           
            // previous
            if(number<1){
                $el.find(".previous").addClass("disabled"); 
            }else{
                $el.find(".previous").removeClass("disabled"); 
            }
            // next
            if(number>=lenPage-1){
                $el.find(".next").addClass("disabled"); 
            }else{
                $el.find(".next").removeClass("disabled"); 
            }
            var page=number+1+"/"+lenPage
            $el.find("#pageNumber").html(page);
        }
}

function renderProduct(){
        var list=[];
        var i=0;
        var j=0;
        var maxItem=36;

        App.products=new ProductCollection();
        App.products.fetch();
        // XXX !! have to reset if not it will store the older data.
        pagination=[];
        App.products.each(function(product){
            if(i % maxItem == 0 && i != 0){
                pagination[j]=list;
                list=[];list.push(i);
                j++;
            }else{
                list.push(i);
            }
            i++;
        });
        pagination[j]=list;
        lenPage=pagination.length;

        loadProduct(number);
}

function getCompany(){
    console.log('getCompany ', App.company);
    var company=JSON.stringify(App.company);
    localStorage.setItem("company", company);
}

var OrderPayView=Backbone.View.extend({
    template: Handlebars.compile($("#order-pay-popup-view-template").html()),
    payOption:{
        printReceipt:function(){
            console.log('printing receipt....');
            var orders=[];
            var subTotal=0;
            var paymentLine=[];
            var tax=0;
            var closeDate=App.order.closeDate;
            var shop=JSON.parse(localStorage.getItem('shop')); 
            var registerName=shop.registerName;
            var shopName=shop.shopName;

            App.order.each(function(line){
                    var vals=line.toJSON();
                    subTotal+=vals['total'];
                    orders.push(vals);
            });
            
            var payTotal=0.0;
            App.order.payment.each(function(line){
                    payTotal+=Number(line.get('amt'));
                    var vals=line.toJSON();
                    if(Number(vals['amt']) > 0){
                        vals['isPlus']=true;
                    }else{
                        vals['isPlus']=false;
                    }
                    paymentLine.push(vals);
            });
        
            var invNumber=1;

            download_company(getCompany);

            var note=App.order.note || '';
            var customer='';
            if(App.order.customer){
                customer=App.order.customer;
                console.log("customer ", customer);
                if(customer.id && customer.name){
                    customer=customer.name;
                }else{
                    customer='Walk in Customer';
                }

                if(customer=='Not entered'){
                    customer='Walk in Customer';
                }
            }

            var data={
                    invNumber: invNumber,
                    closeDate: closeDate,
                    total: subTotal-tax,
                    subTotal: subTotal,
                    toPay:0,
                    tax: 0,
                    orderLine: orders,
                    paymentLine: paymentLine,
                    note: note,
                    shop: shopName, 
                    registerName: registerName,
                    customer: customer,
            }
            // send data to receitp.html
            data=JSON.stringify(data);
            localStorage.setItem("data", data);

            $('#receipt-report').attr("src","receipt.html");
            $('#receipt-report').load(function(){
                this.contentWindow.print();
            });
            return;
        },

        createRegister: function(){
            var register=new Register();
            
            App.order.each(function(line){
                    line=line.toJSON();
                    line=new OrderLine(line);
                    register.get('orders').add(line);
            });

            App.order.payment.each(function(line){
                    line=line.toJSON();
                    line=new PaymentLine(line);
                    register.get('payments').add(line);
            });

            var regList=new RegisterList();
            regList.fetch();

            var number=1;
            if(regList.length > 0){
                number=regList.last().get('number')+1;
            }
            var customerId='';
            var customerName='';
            var customer=App.order.customer;
            if(customer){
                customerId=customer.id;
                customerName=customer.name;
            }

            var shop=JSON.parse(localStorage.getItem('shop')); 
            var registerId=shop.registerId;
            register.set({
                number: number,
                customerId: customerId,
                customerName: customerName,
                registerId: registerId,
                note: App.order.note,
            });

            regList.add(register);
            register.save();

            // remove current park
            if(App.parkId){
                var pkcol=new ParkCollection();
                pkcol.fetch();
                var pk=pkcol.findWhere({id: App.parkId});
                if(pk){
                    pk.destroy();
                    // reset
                    App.parkId=undefined;
                    App.note='';
                }
            }
        },

        validate: function(name){
            var symbol=JSON.parse(localStorage.getItem('symbol'));
            if(symbol){
                symbol=symbol.sign;
            }

            var name=name;
            var amount=$("#order-to-pay-amt2").val() || 0;
            amount=parseFloat(amount);

            var totalOrder=0.0;
            App.order.each(function(line){
                var total=line.get('total');
                totalOrder+=total;
            });

            var totalPaid=amount;
            App.order.payment.each(function(line){
                var amt=line.get('amt');
                totalPaid-=amt;
            });

            App.order.closeDate=timeStamp();

            if(totalPaid==0 && totalPaid==totalOrder){
                // not do anything
                return;

            } else if(totalPaid!=0 && totalPaid==totalOrder){
                var vals={name: name, amt: amount, pay_method: name};
                App.order.payment.push(new PaymentLine(vals));
                
                // print receipt
                this.printReceipt();
                this.createRegister();

                // clear every thing
                $('.modal').modal('hide');
                App.order=App.order.reset();
                App.order.customer={};
                App.order.note='';
                App.order.payment=App.order.payment.reset();
                App.view.render();

                $("#main-input").val("");
                $("#main-input").focus();

            }else{
                var vals={name: name, amt: amount, pay_method: name};
                App.order.payment.push(vals);

                var view=new PaymentListView({collection: App.order.payment});
                view.render();
                var html=view.el;


                $("#to-pay-list").empty();
                $("#to-pay-list").append(view.el);
                
                var toPay=view.$el.find("#total-payment").asNumber();
                $("#order-to-pay-amt2").val(toPay);
                $("#order-to-pay-amt2").select();
                $("#order-to-pay-amt2").focus();

                if(toPay<=0){
                    var closeModal=true;
                    if (toPay < 0){
                        var conf=confirm("Have you issued the customer change of  $"+Math.abs(toPay)+" ?");
                        closeModal= (conf!=true) ? false : true ;
                        if(conf){
                            var vals={name: 'Change', amt: toPay, pay_method: name};
                            var payment=new PaymentLine(vals);
                            App.order.payment.push(payment);
                        }
                    }

                    if(closeModal){
                        toPay=0;

                        $('.modal').modal('hide');

                        this.printReceipt();
                        this.createRegister();

                        App.order=App.order.reset();
                        App.order.customer={};
                        App.order.note='';
                        App.order.payment=App.order.payment.reset();
                        App.view.render();

                        $("#main-input").val("");
                        $("#main-input").focus();

                    }else{
                        $("#order-to-pay-amt2").val(toPay);
                        $("#order-to-pay-amt2").select();
                        $("#order-to-pay-amt2").focus();
                    }
                }

                if(toPay < 0){
                    $("#order-to-pay").css("color","red");
                    $("#order-pay-msg").text('Change / refund');
                    /*$("#order-to-pay").text("("+Math.abs(toPay)+")");*/
                    $("#order-to-pay").text(toPay).formatCurrency({symbol: symbol, colorize:true });
                }else{
                    $("#order-to-pay").css("color","black");
                    $("#order-to-pay").text(toPay).formatCurrency({symbol: symbol, colorize:true });
                    $("#order-pay-msg").text("");
                }
            }
            App.view.showSummary();
       },
    },
    
    events:{
        "click #btn-order-pay-cash": "cash",
        "click #btn-order-pay-credit-card": "creditCard",
        "keypress #order-to-pay-amt2": "pressPay",
    },

    pressPay: function(e){
        if (e.which != 46 && e.which != 8 && e.which != 0 && (e.which < 48 || e.which > 57)) {
            this.$el.find("#order-pay-msg").html("Digits Only").show().fadeOut("slow");
         return false;
        }
    },

    cash: function(e){
        e.preventDefault();
        var name='Cash';
        this.payOption.validate(name);
    },

    creditCard: function(e){
        e.preventDefault();
        var name='Credit Card';
        this.payOption.validate(name);
    },

    render:function(){
        var ctx={};
        var html=this.template(ctx);
        this.$el.html(html);
        var modal=this.$el.find(".modal");

        var symbol=JSON.parse(localStorage.getItem('symbol'));
        if(symbol){
            symbol=symbol.sign;
        }

        modal.on("show.ps.modal",function(){
            var view=new PaymentListView({collection: App.order.payment});
            view.render();
            $("#to-pay-list").empty();
            $("#to-pay-list").append(view.el);

            var totalAmt=0.0;
            App.order.each(function(line){
                var total=line.get('total');
                totalAmt+=total;
            });
            App.order.payment.each(function(payment){
                var amt=payment.get('amt');
                totalAmt-=amt;
            });
            
            totalAmt=toFixed(totalAmt,2);
            $("#order-to-pay-amt2").val(totalAmt);
            $("#order-to-pay-amt2").select();
            $("#order-to-pay-amt2").focus();
            
            view.$el.find("#total-payment").text(totalAmt).formatCurrency({ symbol: symbol, colorize:true });

        });

        modal.on("hidden.ps.modal",function(){
            this.remove();
        });
    },

});

var OrderNoteView=Backbone.View.extend({
    template: Handlebars.compile($("#order-note-popup-view-template").html()),
    events:{
        "click #order-note-save": "save",
    },
    
    save: function(e){
        e.preventDefault();
        var note=this.$el.find("#order-note-note").val();
        this.collection.note=note;
    },

    render:function(){
        var ctx={};
        var html=this.template(ctx);
        this.$el.html(html);
        var that=this;
        $note=this.$el.find("#order-note-note");
        var modal=this.$el.find(".modal");
        modal.on("shown.ps.modal",function(){
            $note.val(that.collection.note || '');
            $note.focus();
            $note.select();
        });
    },
    
});

var OrderParkView=Backbone.View.extend({
    template: Handlebars.compile($("#order-park-popup-view-template").html()),
    events: {
        "click #order-park-save":"save",
        "click #order-park-skip":"skip",
        "click #order-park-back-to-sale":"backToSale",
    },
    
    save: function(e){
        // TODO copy order, clear list
        var notes=$("#order-park-note").val();
        var order=this.collection;
        if(order.length < 1){ return };
        var copyOrder=[];
        order.each(function(order){
            var vals=order.toJSON();
            vals.cid=order.cid;
            copyOrder.push(vals);
        });

        var copyPayment=[];
        order.payment.each(function(payment){
            var vals=payment.toJSON();
            vals.cid=payment.cid;
            copyPayment.push(vals);
        });

        var shop=JSON.parse(localStorage.getItem('shop')); 
        var registerId=shop.registerId;
        
        var vals={
            date_time: timeStamp(),
            state: 'saved',
            user: null,
            code:'',
            total:0,
            note: notes,
            order: copyOrder,
            payment: copyPayment,
            icon:'remove',
            customer: order.customer,
            registerId:registerId,
        }
        
        var collection=new ParkCollection();
        console.log('parked ', vals); 
        // Save existing Park
        if(App.parkId){
            console.log('save exist park');
            collection.fetch();
            var pk=collection.findWhere({id: App.parkId});
            if(pk){
                pk.set(vals);
                pk.save();
            }
            App.parkId=undefined;
        // Save new park
        }else{
            console.log('save new park');
            var model=new Park(vals);
            collection.add(model);
            model.save();
        }

        /*window.location.href = "#retrieve_sale";*/
        App.order.customer={};
        App.order.note='';
        App.order=App.order.reset();
        App.order.payment=App.order.payment.reset();

        App.view.render();
        $("#main-input").val('');
        $("#main-input").focus();
        $("#main-input").select();
    },

    skip: function(e){
        console.log("skip");
    },

    backToSale: function(e){
        e.preventDefault();
    },

    render:function(){
        var ctx={};
        var html=this.template(ctx);
        var that=this;
        this.$el.html(html);
        $note=this.$el.find("#order-park-note");
        var modal=this.$el.find(".modal");
        modal.on("shown.ps.modal",function(){
            $note.val(that.collection.note || '');
            $note.focus();
            $note.select();
        });
        modal.on("hidden.ps.modal",function(){
            this.remove();
        });
    },
});


var CalculatorView=Backbone.View.extend({
    template: Handlebars.compile($("#calculator-view-template").html()),
    /*tagName:"div",*/
    id: 'pos-cal-view',
    events:{
       "click .btn-cal": "calVal", 
       "click .btn-inc": "incVal", 
       "click .btn-desc": "descVal", 
       "click .btn-abs": "absVal", 
       "click .btn-del": "delVal", 
       "click .btn-dblzero": "dblZeroVal", 
       "click .btn-dot": "dotVal", 
       "click .btn-return": "returnVal", 
       "click .btn-percent": "percentVal", 
       "mouseover": "mouseover",
       "mouseout": "mouseout",
       "keypress #cal-result": "calResult",
    },

    calResult: function(e){
        if (e.which != 46 && e.which != 8 && e.which != 0 && (e.which < 48 || e.which > 57)) {
            this.$el.find("#errMsg").html("Digits Only").show().fadeOut("slow");
         return false;
        }
    },
    
    percentVal: function(e){
        e.preventDefault();
        var res=this.$el.find("#cal-result");
        var val=res.val();
        if(val.indexOf("%") < 0){
            val+="%";
        }
        res.val(val);
    },

    calVal:function(e){
        e.preventDefault();
        var target=$(e.target);
        var txt=$("#cal-result");
        var val=txt.val();
        if(mcount>1){
            if(val.indexOf("%")>0){
                val=val.replace("%","");
                val+=target.text()+"%";
            }else{
                val+=target.text();
            }
        }else{
            val=target.text();
        }
        val=parseFloat(val);
        txt.val(val);
        mcount+=1;
    },

    incVal:function(e){
        e.preventDefault();
        var txt=$("#cal-result");
        var val=txt.val();
        val=parseFloat(val || 0)+1;
        txt.val(val);
    },

    descVal:function(e){
        e.preventDefault();
        var txt=$("#cal-result");
        var val=txt.val();
        val=parseFloat(val || 0)-1;
        txt.val(val);
    },

    absVal:function(e){
        e.preventDefault();
        var txt=$("#cal-result");
        var res=txt.val();
        var value=App.editOrder.value;
        res=res=='NaN'? value : res;
        res=parseFloat(res || 0)*-1;
        txt.val(res);
    },

    delVal:function(e){
        e.preventDefault();
        var txt=$("#cal-result");
        var val=txt.val();
        if(val!="NaN"){
            txt.val(val.slice(0,val.length-1));
        }else{
            txt.val(0);
        }
    },
    
    dblZeroVal:function(e){
        e.preventDefault();
        var target=$(e.target);
        var txt=$("#cal-result");
        var val=txt.val();
        if(mcount>1){
            val+=target.text();
        }else{
            val=target.text();
        }
        txt.val(val);
        mcount+=1;
    },

    dotVal:function(e){
        e.preventDefault();
        var target=$(e.target);
        var txt=$("#cal-result");
        var val=txt.val();
        if(mcount>1){
            val+=target.text();
        }else{
            val=target.text();
        }
        txt.val(val);
        mcount+=1;
    },

    returnVal:function(e){
        e.preventDefault();

        var res=$("#cal-result");
        var val=res.val();
        $("*").removeClass("circle");
        mcount=0;

        $("[rel='popover']").popover("hide");
        
        var removeFirst=false;
        if(App.order.length < 1){
            removeFirst=true;
            if(val.indexOf("%") > 0){
                return;
            }
        }

        if(val==''){ return }

        var order=App.order;
        var disc=(App.calTitle=='Disc');

        if(disc){
            // get seq
            if(order.length < 1){
                order.set({seq: 1});
            }else{
                var lastOrder=order.min(function(order){ return order.get('seq');});
                lastOrder=lastOrder.toJSON();
                var nextSeq=(lastOrder.seq)*-1;
                nextSeq++;
            }
            if(val.indexOf("%") > 0){
                val=val.replace("%","");
                var subtotal=$("#order-sub-total").asNumber();
                subtotal=subtotal;
                val=(val/100.00)*subtotal;
            }
            var vals={
                productCid: '',
                productId: '',
                name: "Discount",
                qty: -1,
                price: val,
                total: -val,
                seq: -nextSeq,
            }
            var line=new OrderLine(vals);
            order.add(line);
        }else{
            order.each(function(line){
                var update=App.editOrder; 
                var cid=update.cid;
                var field=update.field;
                var value=val;
                if(cid==line.cid){
                    var vals={};
                    if(field=='qty'){
                        vals={qty: value, total: value*line.get("price"), }; 
                    }else{
                        vals={price: value, total: line.get("qty")*value, }; 
                    }
                    line.set(vals);
                }
            });
        }

        // TODO no order it put 2 line ??
        if(removeFirst){
            console.log(App.order.toJSON());
            var first=App.order.first();
            var last=App.order.last();
            var seq=first.get('seq');
            last.set({seq: seq});
            first.destroy();
            console.log('remove first!');
        }

        App.view.render();
    },

    initialize:function () {
        _.bindAll(this,'mouseover', 'mouseout');
    },

    mouseover: function(e){
        App.showPop=true;
    },

    mouseout: function(e){
        App.showPop=false;
    },

    render:function(){
        // use for first enter val
        mcount=1;
        var lines=[];
        var ctx={
            lines: lines,
        };
        var html=this.template(ctx);
        this.$el.html(html);
        this.$el.find("#cal-title").text(App.calTitle);

        if(App.calTitle=="Disc"){
            this.$el.find("#cal-result").attr("placeholder","E.g. 20% or 2.50");
        }
    },

});

var Park=Backbone.Model.extend({
    defaults:function(){
        return {
            date_time: timeStamp(),
            state: 'draft',
            user: null,
            code:'',
            total:0,
            note: '',
            order: []
        }
    }

});

var ParkPopupView=Backbone.View.extend({
    template: Handlebars.compile($("#park-popup-view-template").html()),

    events:{
       "click #park-popup-void": "void", 
       "click #park-popup-park": "park", 
    },

    park: function(e){
        e.preventDefault();
        console.log("park");
        var order=App.view.collection;
        var note=order.note;

        if(order.length < 1){ return };
        var copyOrder=[];
        order.each(function(order){
            var vals=order.toJSON();
            vals.cid=order.cid;
            copyOrder.push(vals);
        });

        var copyPayment=[];
        order.payment.each(function(payment){
            var vals=payment.toJSON();
            vals.cid=payment.cid;
            copyPayment.push(vals);
        });

        var shop=JSON.parse(localStorage.getItem('shop')); 
        var registerId=shop.registerId;
        var vals={
            date_time: timeStamp(),
            state: 'saved',
            user: null,
            code:'',
            total:0,
            note: note,
            order: copyOrder,
            payment: copyPayment,
            icon:'remove',
            customer: order.customer,
            registerId: registerId,
        }
        
        var collection=new ParkCollection();
        
        // Save existing Park
        if(App.parkId){
            collection.fetch();
            var pk=collection.findWhere({id: App.parkId});
            if(pk){
                pk.set(vals);
                pk.save();
            }
            App.parkId=undefined;
        // Save new park
        }else{
            var model=new Park(vals);
            collection.add(model);
            model.save();
        }

        // copy park to current sale 
        App.order=App.order.reset();
        App.order.payment=App.order.payment.reset();

        var that=this;

        var order=that.model.get("order");
        for(var i=0;i<order.length; i++){
            var vals={
                productCid: order[i].productCid,
                productId: order[i].productId,
                name: order[i].name,
                qty: order[i].qty,
                price: order[i].price,
            }
            App.order.push(new OrderLine(vals));
        }

        var payment=that.model.get('payment');
        for(var i=0;i < payment.length;i++){
            vals={
                name: payment[i]['name'],
                amt: payment[i]['amt'],
            }
            App.order.payment.add(vals);
        }

        var note=that.model.get('note');
        App.order.note=note;

        // Show customer relate from park on the current sale
        var customer=that.model.get("customer");
        App.order.customer=customer; 

        // copy park id  for next checking
        App.parkId=that.model.id;
        
        // rerender order
        App.view.render();

    },
    
    void: function(e){
        e.preventDefault();
        // void current sale
        App.order=App.order.reset();
        App.order.customer={};
        App.order.payment=App.order.payment.reset();

        if(App.parkId){
            var pkcol=new ParkCollection();
            pkcol.fetch();
            var pk=pkcol.findWhere({id: App.parkId});
            if(pk){
                console.log('destroy..');
                console.log(pk.toJSON());
                console.log('.........');
                pk.destroy();
                // reset
                App.parkId=undefined;
                App.note='';
            }
        }
        
        // copy new order from park
        var that=this;
        var customer=JSON.stringify(that.model.get('customer'));
        App.order.customer=customer; 

        var order=that.model.get("order");
        for(var i=0;i<order.length; i++){
            var vals={
                productCid: order[i].productCid,
                productId: order[i].productId,
                name: order[i].name,
                qty: order[i].qty,
                price: order[i].price,
            }
            App.order.push(new OrderLine(vals));
        }

        var payment=that.model.get('payment');
        for(var i=0;i < payment.length;i++){
            vals={
                name: payment[i]['name'],
                amt: payment[i]['amt'],
            }
            App.order.payment.add(vals);
        }

        var note=that.model.get('note');
        App.order.note=note;

        // copy park id  for next checking
        App.parkId=that.model.id;
        
        // rerender order
        App.view.render();
    },

    render:function(){
        var ctx={};
        var html=this.template(ctx);
        this.$el.html(html);
        $("#content").append(this.el);
        var modal=this.$el.find(".modal");
        modal.modal({ backdrop: 'static' });
    },

});

var ParkView=Backbone.View.extend({
    template: Handlebars.compile($("#park-view-template").html()),
    tagName:"tr",
    events:{
       "click .park-note": "parkNote", 
       "click .remove-park": "removePark", 
    },
    
    parkNote: function(e){
        e.preventDefault();
        // XXX check current order
        var currentOrder=App.order;
        var that=this;

        var router = new PosRouter;
        router.navigate("current_sale",{trigger: true, replace: true});
        App.view.render();

        if(!currentOrder) { currentOrder=new Order() ; }

        if(currentOrder.length > 0 && that.model.id != App.parkId){
            var view=new ParkPopupView({model: this.model});
            view.render(); 
            $el=view.$el;
            var oldOrder=this.model.get("order");
            $el.find("#park-popup-old-order").html(oldOrder.length);
            $el.find("#park-popup-new-order").html(currentOrder.length);

        }else{
            // reset order && copy new order from park
            if(App.parkId==that.model.id){
                return;
            }

            var that=this;
            var customer=new Customer(that.model.get('customer'));
            console.log('park notes ', that.model);
            App.order.customer=customer.toJSON();

            var order=that.model.get("order");
            for(var i=0;i<order.length; i++){
                var vals={
                    productCid: order[i].productCid,
                    productId: order[i].productId,
                    name: order[i].name,
                    qty: order[i].qty,
                    price: order[i].price,
                }
                App.order.push(new OrderLine(vals));
            }

            var payment=that.model.get('payment');
            for(var i=0;i < payment.length;i++){
                vals={
                    name: payment[i]['name'],
                    amt: payment[i]['amt'],
                }
                App.order.payment.add(vals);
            }

            var note=that.model.get('note');
            App.order.note=note;

            // copy park id  for next checking
            App.parkId=that.model.id;
            
            // rerender order
            App.view.render();

        } // else

    },

    removePark: function(e){
        e.preventDefault();
        if (confirm('Are you sure you want to delete this item?')) {
        // Save it!
            this.model.destroy();
        } else {
            // Do nothing!
        }
    },

    render:function(){
        var park=this.model;
        var cid=park.cid;
        var order=this.model.get('order');
        var total=0.0;
        for(var i=0;i<order.length;i++){
            var qty=order[i]['qty'] || 0;
            var price=order[i]['price'] || 0.0;
            total+= qty*price;
        }
        var ctx=this.model.toJSON();
        ctx.cid=cid;
        ctx.total=total;
        var html=this.template(ctx);
        this.$el.html(html);
        this.$el.find(".currency").formatCurrency({symbol:"", colorize: true});
    },
});

var ParkCollection=Backbone.Collection.extend({
    model: Park,
    localStorage: new Backbone.LocalStorage("park-collection-backbone"),
});

var ParkSaleLine=Backbone.Model.extend({
    defaults: {
        created_date: '',
        customer:'Walk in Customer',
        order: '',
        payment: '',
    }
});

var ParkSaleLineView=Backbone.View.extend({
    template: Handlebars.compile($("#park-sale-line-view-template").html()),
    tagName: "tr",
    events: {
        "click .park-show-sub": "showSub",
        "click .park-sale-remove": "removeOrder",
    },

    removeOrder: function(e){
        e.preventDefault(); 
        var $tr=$(e.target).parents("tr");
        var msg="Are you sure to delete?";
        var conf = confirm(msg);
        if(conf){
            var id=this.model.get('regId');
            var collection=new RegisterList();
            collection.fetch();

            var cid=this.model.cid;
            var selector='#park-slide-'+cid;

            console.log('removed ', selector);
            $(selector).empty();

            var model=collection.get(id);
            model.destroy();
            $tr.remove();


            len=collection.length-1;
            var title='Completed Sale';
            if(len>0){
                title='Completed Sale('+len+')';
            }
            $("#park-collection-sale-title").html(title);

        }
    },

    showSub: function(e){
        e.preventDefault();
        var cid=$(e.target).attr("data-cid"); 
        var selector='#park-slide-'+cid;
        $(selector).slideToggle("fast");
    },

    render:function(){
        var symbol=JSON.parse(localStorage.getItem('symbol'));
        if(symbol){
            symbol=symbol.sign;
        }
        var cid=this.model.cid;
        var ctx=this.model.toJSON();
        ctx.cid=cid;
        var html=this.template(ctx);
        this.$el.html(html);
        this.$el.find(".currency").formatCurrency({symbol: symbol, colorize: true});
    },
});

var ParkSaleLineSubView=Backbone.View.extend({
    template: Handlebars.compile($("#park-sale-line-sub-view-template").html()),
    tagName: "tr",
    events: {
        "click #park-sale-line-sub-print": "subPrint",
    },
    
    subPrint: function(e){
        e.preventDefault();
        var order=this.model.get('orders');
        var payment=this.model.get('payments');
        var note=this.model.get("note");
        var customer=this.model.get('customer');

        App.order=new Order(order);
        App.order.note=note;
        App.order.payment=new Payment(payment);
        App.order.customer=customer;
        
        var closeDate=this.model.get("created_date");
        App.order.closeDate=closeDate;
        var view=new OrderPayView({collection:App.order});
        view.payOption.printReceipt();
    },

    render:function(){
        var symbol=JSON.parse(localStorage.getItem('symbol'));
        if(symbol){
            symbol=symbol.sign;
        }
        var cid=this.model.cid;
        var ctx=this.model.toJSON();
        ctx.cid=cid;
        
        var html=this.template(ctx);
        this.$el.html(html);
        this.$el.find(".currency").formatCurrency({symbol: symbol, colorize: true});
    },
});

var ParkCollectionView=Backbone.View.extend({
    template: Handlebars.compile($("#park-collection-view-template").html()),
    id:"park-collection-view-id",

    render: function() {
        var that=this;
        this.collection=new ParkCollection();
        var total_order=0;
        var shop=JSON.parse(localStorage.getItem('shop')); 
        if(!shop){
            alert("No shop found, please select or create it from the backend.");
            return;
        }
        var registerId=shop.registerId;
        this.collection.fetch({
            success: function() {
                var ctx={};
                var html=that.template(ctx);
                that.$el.html(html);
                var no=1;
                that.collection.each(function(model) {
                    // filter register
                    if(model.get('registerId') == registerId){
                        model.set({no: no});
                        var view=new ParkView({model:model});
                        view.render();
                        that.$el.find("#park-line").append(view.el);
                        no+=1;
                    }
                    /*that.$el.find("#park-total-order").text(total_order);*/
                });
                that.collection.bind("reset add remove",function() {
                    that.render();
                });
            },
            error: function() {
                alert("failed to fetch parked order");
            }
        });

        this.collection=new RegisterList();

        this.collection.fetch({
            success: function() {
                $saleLine=that.$el.find("#park-sale-line");
                $saleLine.empty();
                var count=0;
                that.collection.each(function(model) {
                    if(model.get('registerId') == registerId){
                        var customer=model.get('customerName');
                        if(!customer){ customer='Not entered';}

                        var vals=model.toJSON();
                        vals.customer=customer;
                        vals.numberOrder=model.get('orders').length;
                        vals.numberPayment=model.get('payments').length;
                        vals.regId=model.id;

                        var order=vals['orders'];
                        var orderTotal=0;
                        for(var i=0; i<order.length;i++){
                            orderTotal+=order[i]['total'];
                        }

                        vals.orderTotal=orderTotal;

                        model=new ParkSaleLine(vals); 

                        var view=new ParkSaleLineView({model:model});
                        view.render();
                        $saleLine.append(view.el);

                        var view=new ParkSaleLineSubView({model:model});
                        view.render();
                        $saleLine.append(view.el);

                        count++;
                    }
                });
                var title='Completed Sale';
                if(count>0){
                    title='Completed Sale('+count+')';
                }
                that.$el.find("#park-collection-sale-title").html(title);
            },
            error: function() {
                alert("failed to fetch parked order");
            }
        });
    },


});


var PosRouter = Backbone.Router.extend({
    routes: {
        '': 'index',
        "current_sale": "currentSale",
        "retrieve_sale": "retrieveSale",
        "close_register": "closeRegister",
    },

    index: function(){
        var router = new PosRouter;
        router.navigate("current_sale",{trigger: true, replace: true});
    },

    currentSale: function() {
        if(App.order==null){
            App.order=new Order();
        }

        App.order.comparator="seq";
        var orders=App.order;
        var view=new OrderView({collection:orders});
        view.render();
        App.view=view;
        var html='<div class="row"><div class="span8" id="left-row"></div></div>';
        $("#content").empty();
        $("#content").height(566);
        $("#content").append(html);
        $("#left-row").append(App.view.el);
        $(".navbar li").removeClass("active");
        $("#menu1").addClass("active");
        $("#main-input").val('');
        $("#main-input").focus();
        download_shop(loadShopMenu);
    },

    retrieveSale: function() {
        var view=new ParkCollectionView();
        view.render();
        $("#content").empty();
        $("#content").height(566);
        $("#content").append(view.el);
        $(".navbar li").removeClass("active");
        $("#menu2").addClass("active");
        download_shop(loadShopMenu);
    },

    closeRegister: function() {
        var view=new CloseRegisterview();
        view.render();
        $("#content").empty();
        $("#content").height(630);
        $("#content").append(view.el);
        $(".navbar li").removeClass("active");
        $("#menu3").addClass("active");
        download_shop(loadShopMenu);
    },
});

var router = new PosRouter;

// Start Backbone history a necessary step for bookmarkable URL's
Backbone.history.start();

// Copy link and new page
if(navigator.onLine){
    $(".online").css("background-color","#54ba54");
    $(".online").html('online');
    App.isOnLine=true;
}else{
    $(".online").css("background-color","#ff9900");
    $(".online").html('offline');
    App.isOnLine=false;
}

// Checking status while working on POS
window.addEventListener("offline", function(e) {
    $(".online").css("background-color","#ff9900");
    $(".online").html('offline');
    App.isOnLine=false;
}, false);

window.addEventListener("online", function(e) {
    $(".online").css("background-color","#54ba54");
    $(".online").html('online');
    App.isOnLine=true;
}, false);

download_local_sign(function(data){
    localStorage.setItem('symbol',JSON.stringify(data));
    console.log('write symbol', data);
});


});

