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

    return $(this).live('click', function() {
        var widget = $(this);
        var dialog = $('<div></div>');
        var url = $(this).attr("href");
        $.ajax({
            url: url,
            data: {},
            type: 'GET',
            success: function (response, textStatus, xhr) {
                var theCode = filterHtml(response, opts.responseContentSelector);
                var pageTitle = filterHtml(response, 'title').text();
                dialog.html(theCode);
                dialog.dialog({
                    height: 'auto',
                    minWidth: 850,
                    modal: true,
                    resizable: true,
                    title: pageTitle,
                    zIndex: 900
                });
                selectRelated(dialog.find(opts.responseContentSelector), onRelatedSelect);
            }
        });

        function onRelatedSelect(id, selectedElement, initWidget) {
            widget.prev('input').val(id);
            dialog.dialog("destroy");
            dialog.remove();
            if(initWidget !== undefined)
                initWidget(widget, selectedElement);
        };
        return false;
    });
};

django.jQuery.fn.multipleRelatedLookup = function(selectRelated, options) {
    var $ = django.jQuery;
    var defaults = {
        responseContentSelector: '#related-lookup'
    };
    var opts = $.extend({}, defaults, options);

    return $(this).live('click', function() {
        var widget = $(this);
        var dialog = $('<div></div>');
        var url = $(this).attr("href");
        $.ajax({
            url: url,
            data: {},
            type: 'GET',
            success: function (response, textStatus, xhr) {
                var theCode = filterHtml(response, opts.responseContentSelector);
                var pageTitle = filterHtml(response, 'title').text();
                dialog.html(theCode);
                dialog.dialog({
                    height: 'auto',
                    minWidth: 500,
                    modal: true,
                    resizable: true,
                    title: pageTitle,
                    zIndex: 900
                });
                selectRelated(dialog.find(opts.responseContentSelector), onRelatedSelect);
            }
        });

        function onRelatedSelect(id, selectedElement, initWidget) {
            var val = widget.prev('input').val();
            if(val !== '') {
                widget.prev('input').val(val + ',' + id);
            } else {
                widget.prev('input').val(id);
            }
            dialog.dialog("destroy");
            dialog.remove();
            if(initWidget !== undefined)
                initWidget(widget, selectedElement);
        };
        return false;
    });
};

