odoo.define('request_quote.tracking', function(require) {
var rpc = require('web.rpc');
$(document).ready(function () {
    $(".oe_website_sale a.a-submit1").on('click', function(o) {
        var prod_id = $("input[name='product_id']").attr('value');
        var var1 = $("#custom_product_details .product_id").val(prod_id);
        $(this).closest('form').submit();

    });
}); 
$(document).ready(function () { 
var product_id = $("input[name='product_id']").attr('value');
    rpc.query({
          model: 'product.product',
          method: 'search_read',
          args: [[['id', '=', product_id]]],
          })
        .then(function (result) {
            $("input[name='product_name']").val(result[0].display_name);
        });
});
});
