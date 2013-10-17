'use strict';

function bindPopover() {
    var content = $('#comment_textarea').attr('popover_content');
    if(content && content.length > 0) {
        $('#comment_textarea').popover({
            title: 'Title',
            content: content,
            trigger: 'focus',
            html: true,
        });
    }
}

$(document).on('shown.bs.modal', function() {
    // bind popover for the modal dialog
    bindPopover();
});

$(document).ready(function() {
    // bind modal in the comments/add stand-alone page
    bindPopover();
});
