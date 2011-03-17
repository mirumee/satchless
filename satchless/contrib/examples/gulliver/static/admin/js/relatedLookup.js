function filterHtml(data, selector) {
    return django.jQuery("<div/>")
    .append(data.replace(/<script(.|\s)*?\/script>/g, ""))
    .find(selector);
};

django.jQuery.fn.relatedLookup = function(selectRelated, options) {
    var $ = django.jQuery;
    var defaults = {
        responseContentSelector: '#related-lookup'
    };
    var opts = $.extend({}, defaults, options);

    return $(this).each(function() {
        var dialog;
        var widget = $(this);

        function onRelatedSelect(id, selectedElement) {
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
                    var theCode = filterHtml(response, opts.responseContentSelector);
                    dialog.html(theCode);
                    dialog.dialog({
                        modal: true,
                        resizable: true,
                        width: '800px',
                        zIndex: 900
                    });
                    selectRelated(dialog.find(opts.responseContentSelector), onRelatedSelect);
                }
            });

            return false;
        });
    });
};

