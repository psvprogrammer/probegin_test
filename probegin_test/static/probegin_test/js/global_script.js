/* this JQuery code snippet allows to add handler on
/* ‘show’/’hide’ events using .on() method
/* source: http://viralpatel.net/blogs/jquery-trigger-custom-event-show-hide-element/ */
(function ($) {
    $.each(['show', 'hide'], function (i, ev) {
        var el = $.fn[ev];
        $.fn[ev] = function () {
            this.trigger(ev);
            return el.apply(this, arguments);
        };
    });
})(jQuery);

$(document).ready(function() {

    //===> tooltip init
    $('[data-toggle="tooltip"]').tooltip();

    //===> ajax load data href click event
    $('[data-load="ajax"]').each(function () {
        $(this).click(function (event) {
            event.preventDefault();
            pathname = $(this).prop('href').replace('http://', '').replace('https://', '').replace(window.location.host, '');
            getAjaxPage(pathname);
        })
    })

    //===> init global budget select
    init_budget_select_change();

    //===> profile page success message fadeOut (should be moved to profile page?)
    // $("div.fadeout-slowly-3").fadeOut(3000);
    $("span.fadeout-slowly-3").css({opacity: 1.0, visibility: "visible"}).animate({opacity: 0.0},3000);

    // var exclude_ajax_urls  = [
    //     '/login', '/logout', '/password_change/', '/password_change/done/',
    // ]
    // load with delay 1 sec
    // $(this).delay(1000).queue(function() {
    //     ajaxGet('/ajax' + window.location.pathname, {}, function (content) {
    //         $("#loader-animation").hide();
    //     });
    //     $(this).dequeue();
    // });

    // direct method load
    // if ($.inArray(window.location.pathname, exclude_ajax_urls) == -1){
    //     getAjaxPage(window.location.pathname);
    // }
    load_page_content();
});

function load_page_content() {
    exclude_ajax_urls  = [
        '/login', '/logout', '/password_change/', '/password_change/done/',
    ]
    // direct method load
    if ($.inArray(window.location.pathname, exclude_ajax_urls) == -1){
        getAjaxPage(window.location.pathname);
    }
    $("#loader-animation").fadeOut(1000);
}

function getAjaxPage(url) {
    $("#loader-animation").show();
    $("#main-container").hide();
    try{
        ajaxGet('/ajax' + url, {'width': $(document).width()}, function (content) {
            $("#main-container").fadeIn(1000);
            $("#loader-animation").fadeOut(1000);
        });
    }
    finally {
        $("#loader-animation").fadeOut(1000);
    }
}

function change_current_budget(value, callback) {
    ajaxPost('/ajax/change_budget', {'budget': value}, function (content) {
        // on success
        if (callback){
            callback();
        }
    });
}

/* This function removes all previous on select changed event handlers
 * and run passed callback function */
function init_budget_select_change(callback) {
    $("#budget-selector").off('changed.bs.select');
    $("#budget-selector").on('changed.bs.select', function (event, clickedIndex, newValue, oldValue) {
        if (newValue){
            change_current_budget(event.currentTarget.value, callback);
            $(document).click();
        }
    });
}

/*
* This function init and show default popover for element
* and freeze elem to prevent DB spam.
* Default delay is 3 sec.
* */
function show_popover(elem, content, freeze_elem) {
    if (!freeze_elem){
        freeze_elem = elem;
    }
    elem.popover({
        delay: { hide: 3000 },
        title: content.title,
        content: content.content,
        template: content.template,
        trigger: 'click|focus',
    });

    elem.popover('show');
    elem.popover('toggle');
    freeze_elem.prop('disabled', true);

    $(this).delay(3000).queue(function() {
        elem.popover('destroy');
        freeze_elem.prop('disabled', false);
        $(this).dequeue();
    });
}