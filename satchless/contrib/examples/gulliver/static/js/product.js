$(function() {
    $('.photos a').click(function() {
        $('#sidebar .section img').removeClass('active');
        $(this).find('img').addClass('active');

        //unbind Cloud events
        $("#main-photo .mousetrap").unbind();
        $('#main-photo').html('<a class="cloud-zoom" href="' + $(this).attr('data-big-picture') + '" title="Click" rel="position: \'inside\' , showTitle: false"><img src="' + $(this).attr('href') + '" /></a><div class="zoom-hint">Click the image to zoom in.<br />To pan, move your mouse around the image.</div>');
        $('#main-photo>a').CloudZoom();

        return false;
    });
});

