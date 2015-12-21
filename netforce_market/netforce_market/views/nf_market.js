var Market=NFView.extend({
    _name: "nf_market",

    render: function() {
        log("Market.render");
        NFView.prototype.render.call(this);
        this.$el.find("iframe").on("load",this.resize_iframe.bind(this));
    },

    resize_iframe: function() {
        var obj=this.$el.find("iframe")[0];
        obj.style.height = obj.contentWindow.document.body.scrollHeight + 'px';
    }
});

Market.register();
