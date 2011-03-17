function filterHtml(data, selector) {
    return django.jQuery("<div/>")
    .append(data.replace(/<script(.|\s)*?\/script>/g, ""))
    .find(selector);
};

django.jQuery.fn.relatedLookup = function(selectRelated, options) {
    var $ = django.jQuery;
    var defaults = {
        selectRelatedBodySelector: '#related-lookup'
    };
    var opts = $.extend({}, defaults, options);

    return $(this).each(function() {
        var dialog;
        var widget = $(this);

        function onRelatedSelect(id) {
            widget.prev('input').val(id);
            dialog.dialog("destroy");
            dialog.remove();
        };

        $(this).click(function() {
            dialog = $('<div title=""></div>');
            var url = $(this).attr("href");
            $.ajax({
                url: url,
                data: {},
                type: 'GET',
                success: function (response, textStatus, xhr) {
                    var theCode = filterHtml(response, opts.selectRelatedBodySelector);
                    dialog.html(theCode);
                    dialog.dialog({
                        modal: true,
                        resizable: true,
                        width: '620px',
                        zIndex: 900
                    });
                    selectRelated(dialog.find(opts.selectRelatedBodySelector), onRelatedSelect);
                }
            });

            return false;
        });
    });
};

