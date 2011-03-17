function lookupProduct(container, onProductSelect) {
    var $ = django.jQuery;
    var searchForm = $('form', container);
    var url = searchForm.attr('action');
    var timer;

    function initProductList() {
        $('.product', container).each(function() {
            $(this)
            .css({cursor: 'pointer'})
            .click(function() {
                onProductSelect($(this).find('.product-id').html().trim(), $(this));
                return false;
            });
            $(this).find('.product-id-container').hide();
        });
    };
    function searchProduct(q) {
        $.ajax({
            url: url,
            data: {
                q: q,
            },
            success: function(response) {
                var productList = $('#search-products', container);
                var html = filterHtml(response, '#search-products').html();
                $(productList).html(html);
                initProductList();
            }
        });
    };
    function submitForm() {
        var query = searchForm.find('input[name=q]').val();
        if(timer !== undefined) {
            clearTimeout(timer);
        }
        timer =  setTimeout(function() {
            searchProduct(query);
        }, 500);
    };
    $('input[name=q]', searchForm).keyup(function() { submitForm(); });
    $(searchForm).submit(function() { submitForm(); return false;});

    initProductList();
};

django.jQuery(function() {
    var $ = django.jQuery;
    $('.related-lookup').relatedLookup(lookupProduct, {
        responseContentSelector: '#search-products'
    });
});

