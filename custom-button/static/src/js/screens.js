odoo.define('custom-button.screens', function (require) {
"use strict";
var core = require('web.core');
var screens = require('point_of_sale.screens');
var gui = require('point_of_sale.gui');
var popup = require('point_of_sale.popups');


screens.ActionpadWidget.include ({
//    init: function(parent, options) {
//        var self = this;
//        this._super(parent, options);
//
//        this.pos.bind('change:selectedClient', function() {
//            self.renderElement();
//        });
//    },
    renderElement: function () {
        var self = this;
        this._super ();
        console.log(self)
        this.$('.set-customer-invoice').click(function(){
            self.gui.show_screen('clientlist');
        });
    },
//    click_custom_print: function () {
//        this.gui.show_screen ('print_receipt');
//    }
});

});
