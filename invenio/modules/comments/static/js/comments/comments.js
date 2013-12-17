/**
This file is part of Invenio.
Copyright (C) 2013 CERN.

Invenio is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License as
published by the Free Software Foundation; either version 2 of the
License, or (at your option) any later version.

Invenio is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with Invenio; if not, write to the Free Software Foundation, Inc.,
59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
**/

'use strict';

/* exported COMMENTS */

/**
 * General comment pages utilities modules.
 *
 * @module
 * @param {jQuery} $ usually window's jQuery object.
 */
var COMMENTS = (function($) {

    /**
     * Attaches collapse/ expand actions to comments' chevrons.
     */
    function bindCollapse() {
        $('.collapse').on('show', function(e) {
            $.get($(this).attr('data-action'));
            e.stopPropagation();
        });

        $('.collapse').on('hide', function(e) {
            $.get($(this).attr('data-action')).fail(function() { return; });
            e.stopPropagation();
        });
    }

    function addCommentDialog(e, context) {
        e.preventDefault();
        var $anchor = $(context);
        var href = $anchor.attr('data-href');
        $.ajax({
            url: href,
            success: function(data) {
                $('<div class="modal hide fade" >' + data + '</div>')
                    .modal();
                // focus on textarea
                $('#comment-textarea').focus();
            },
            error: function(jqXHR) {
                if(jqXHR.status === 401) {
                    window.location.href =
                        $anchor.attr('data-href-login');
                }
            }
        });
    }

    $(document).on('hidden.bs.modal', function() {
        // delete any existing modal elements instead of just hiding them
        $('.modal').remove();
        $('.modal-backdrop').remove();
    });

    return {
        bindCollapse: bindCollapse,
        addCommentDialog: addCommentDialog
    };
})(window.jQuery);
