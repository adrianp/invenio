'use strict';

/* global PDF_VIEWER */
/* global _ */
/* exported PDF_NOTES_HELPER */

/**
 * Utilities for combining the PDF preview and Notes features.
 *
 * @module
 * @param {jQuery} $ usually window's jQuery object.
 */
var PDF_NOTES_HELPER = (function($) {

    /**
     * Retrives the notes from the server via an AJAX request.
     *
     * @param  {*} callerData unused, AJAX callback source.
     * @param  {*} ajaxStatus unused, AJAX callback source.
     * @param  {*} ajaxObject unused, AJAX callback source.
     * @param  {Boolean} all true if all the notes should be retrieved, false if
     *                   only those on the currently previewed page.
     */
    function getNotes(callerData, ajaxStatus, ajaxObject, all) {
        if(all === undefined && ALL_TOGGLED) {
            // AJAX callback on page change while `all-notes-toggle` is toggled
            return;
        }
        var page = all ? -1 : PDF_VIEWER.getCurrentPage();
        $.ajax({
            url: 'notes_page',
            data: { page: page },
            success: function(data) {
                $('#notes-wrapper').html(data);
                $(window).trigger('notesdisplayed');
            }
        });
    }

    /**
     * true if all the notes are currently displayed, false if only those on
     * currently previewd page.
     *
     * @type Boolean
     */
    var ALL_TOGGLED = false;

    /**
     * Text that should fill the add comment textarea when modal opens (usually
     * the current page note marker).
     *
     * @type String
     */
    var TEXTAREA_FILL;

    /**
     * Uses the currently previewed page number to construct an note marker that
     * will fill the add comment textarea.
     */
    function fillCommentsTextArea() {
        TEXTAREA_FILL = 'P.' + PDF_VIEWER.getCurrentPage() + ': ';
    }

    /**
     * Changes the view notes button text, depending on what is previewed
     * currently (all notes/ notes on page).
     */
    function changeAllNotesButtonText() {
        if(!ALL_TOGGLED) {
            $('#all-notes-toggle').
                html('<i class="icon-eye-open"></i> ' +
                     _('Show all annotations'));
        } else {
            $('#all-notes-toggle').
                html('<i class="icon-eye-open"></i> ' +
                     _('Show page annotations'));
        }
    }

    /**
     * Returns the text that should fill the add comment textarea.
     *
     * @return {String}
     */
    function getTextAreaFill() {
        return TEXTAREA_FILL;
    }

    /**
     * Sets the text that should fill the add comment textarea.
     *
     * @param {String} fill
     */
    function setTextAreaFill(fill) {
        TEXTAREA_FILL = fill;
    }

    /**
     * Bootstrapping actions.
     */
    function init() {
        // get notes on previewed page change
        PDF_VIEWER.bindPageChangeAction(getNotes);

        // when clicking the on PDF viewer. a new comment with the current page
        // note marker should be initialized
        $('#pdf-preview').on('click', fillCommentsTextArea);

        $('#all-notes-toggle').on('click', function() {
            // this event is called before the button has the 'active' class set
            ALL_TOGGLED = !ALL_TOGGLED;
            getNotes(undefined, undefined, undefined, ALL_TOGGLED);
            changeAllNotesButtonText();
        });
    }

    $(document).ready(function() {
        init();
    });

    $(window).on('tabreloaded', function() {
        init();
    });

    return {
        getTextAreaFill: getTextAreaFill,
        setTextAreaFill: setTextAreaFill
    };
})(window.jQuery);
