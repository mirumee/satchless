$(function() {
    $('#content .thumbs a').click(function() {
        //unbind Cloud events
        $("#content .main-photo .mousetrap").unbind();
        $('#content .main-photo').html('<a class="cloud-zoom" href="' + $(this).attr('data-big-picture') + '" title="Click" rel="position: \'inside\' , showTitle: false"><img src="' + $(this).attr('href') + '" /></a>');
        $('#content .main-photo>a').CloudZoom();

        $('#content .main-photo .mousetrap').css('width', '305px');
        return false;
    });
});

