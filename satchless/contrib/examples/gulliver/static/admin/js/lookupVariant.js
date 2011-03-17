function lookupVariant(container, onVariantSelect) {
    var $ = django.jQuery;
    var searchForm = $('form', container);
    var url = searchForm.attr('action');
    var timer;

    function initProductList() {
        $('.product', container).each(function() {
            $(this).find('.variants').click(function() {
                onVariantSelect($(this).find('.variant-id').html().trim(), $(this));
                return false;
            });
            $(this).find('.product-id-container').hide();
            $(this).find('.variant-id').hide();
        });
    };
    function searchProduct(q) {
        $.ajax({
            url: url,
            data: {
                q: q,
            },
            success: function(response) {
                var productList = $('#products', container);
                var html = filterHtml(response, '#products').html();
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
    $('.related-lookup').relatedLookup(lookupVariant, {
        responseContentSelector: '#search-products'
    });
});

