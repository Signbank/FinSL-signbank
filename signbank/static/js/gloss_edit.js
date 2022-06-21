/**
 * @author Steve Cassidy
 */
 $(document).ready(function() {
     configure_edit();

     disable_edit();


     if (window.location.search.match('edit')) {
         toggle_edit();

         if (window.location.search.match('editrelforeign')) {
             $('#relationsforeign').addClass('in');
         }
         else if (window.location.search.match('editrel')) {
             $('#relations').addClass('in');
         }
         if (window.location.search.match('editmorphdef')) {
             $('#morphology').addClass('in');
         }

     }

     $('#enable_edit').on('click', toggle_edit);

     glosstypeahead($('.glosstypeahead'));


    // setup requried for Ajax POST
    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    $.ajaxSetup({
        crossDomain: false, // obviates need for sameOrigin test
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type)) {
                xhr.setRequestHeader("X-CSRFToken", csrf_token);
            }
        }
    });

    ajaxifyTagForm();
    delete_glossurl();

 });

function disable_edit() {
    $('.edit').editable('disable');
    $('.edit').css('color', 'black');
    $('.edit_url').css('color', '');
    /*$('#edit_message').text('');*/
    $('#edit_message').hide();
    $('.editform').hide();
    $('#delete_gloss_btn').hide();
    $('#enable_edit').addClass('btn-primary').removeClass('btn-danger');
    $('#add_relation_form').hide();
    $('#add_relationtoforeignsign_form').hide();
    $('#add_morphologydefinition_form').hide();
    $('.relation_delete').hide();
    $('.relationtoforeignsign_delete').hide();
    $('.morphology-definition-delete').hide();
    // Video/poster editing
    $('.video_edit').hide();
    $('#btn-record-video').hide();
    $('.comment_delete_staff').hide();
    $('.update_glossrelation').hide();
    $('.remove_comment_tag').hide();
    $('.glossurlform').hide();
    $('.glossurl-delete').hide();
};

function enable_edit() {
    $('.edit').editable('enable');
    $('.edit').css('color', 'red');
    // we get this message within django now, so that it can be translated.
    /*$('#edit_message').text('Click on red text to edit  ');*/
    $('#edit_message').show();
    $('.editform').show();
    $('#delete_gloss_btn').show().addClass('btn-danger');
    $('#enable_edit').removeClass('btn-primary').addClass('btn-danger');
    $('#add_relation_form').show();
    $('#add_relationtoforeignsign_form').show();
    $('#add_morphologydefinition_form').show();
    $('.relation_delete').show();
    $('.relationtoforeignsign_delete').show();
    $('.morphology-definition-delete').show();
    // Video/poster editing
    $('.video_edit').show();
    $('#btn-record-video').show();
    $('.comment_delete_staff').show();
    $('.update_glossrelation').show();
    $('.remove_comment_tag').show();
    $('.glossurlform').show();
    $('.glossurl-delete').show();
};

function toggle_edit() {
    if ($('#enable_edit').hasClass('edit_enabled')) {
        disable_edit();
        $('#enable_edit').removeClass('edit_enabled');
        // This variable (enable_edit_button_text) should exist in the template
        $('#enable_edit').text(enable_edit_button_text);
    } else {
        enable_edit();
        $('#enable_edit').addClass('edit_enabled');
        // This variable (disable_edit_button_text) should exist in the template
        $('#enable_edit').text(disable_edit_button_text);
    }
}


function delete_gloss() {
    alert("Delete this gloss?");
}

$.editable.addInputType('positiveinteger', {
    element : function(settings, original) {
        var input = $('<input type="number" min="0">');
        $(this).append(input);
        return(input);
    },

});

$.editable.addInputType('multicheckbox', {
    element: function(settings) {
        var $el = $(this);

        settings.submitdata = function(_revert, settings, submitdata) {
            submitdata[settings.name] = $.map($el.find(":checked"), function(input) { return input.value });

            return submitdata;
        };

        $.each(settings.data || [], function(value, label) {
            if (value === "selected") {
                return;
            }

            $el.append($("<label><input type='checkbox' value='" + value + "' /></label><br />"));
        });

        return $el.find("input[type='checkbox']");
    },
    content : function(_string, settings, original) {
        var selected = settings.data.selected || [];
        var $el = $(this);
        $.each(settings.data || [], function(value, label) {
            if (value === "selected") {
                return;
            }

            var $radio = $el.find("[value='" + value + "']");
            selected.indexOf(value) >= 0 && $radio.attr("checked", "checked");

            $radio.after("&nbsp;" + label);
        });
    },
})


function configure_edit() {

    $.fn.editable.defaults['indicator'] = 'Saving...';
    $.fn.editable.defaults['tooltip'] = 'Click to edit...';
    $.fn.editable.defaults['placeholder'] = '-';
    // save_button_text and cancel_button_text variables should exist in template (inside blocktrans tags)!
    $.fn.editable.defaults['submit'] = '<button class="btn btn-primary" type="submit">'+save_button_text+'</button>';
    $.fn.editable.defaults['cancel'] = '<button class="btn btn-default" type="cancel">'+cancel_button_text+'</button>';
    $.fn.editable.defaults['width'] = 'none';
    $.fn.editable.defaults['height'] = 'none';
    $.fn.editable.defaults['submitdata'] = {'csrfmiddlewaretoken': csrf_token};
    $.fn.editable.defaults['onerror']  = function(settings, original, xhr){
                          alert("There was an error processing this change: " + xhr.responseText );
                          original.reset();
                        };
    $.fn.editable.defaults['onreset']  = function(settings, original, xhr){
                          original.reset();
                        };


     $('.edit_text').editable(edit_post_url);
     $('.edit_int').editable(edit_post_url, {
         type      : 'positiveinteger',
         onerror : function(settings, original, xhr){
                          alert(xhr.responseText);
                          original.reset();
                    },
     });
     $('.edit_area').editable(edit_post_url, {
         type      : 'textarea'
     });
     $('.edit_area_translations').editable(edit_post_url, {
         type      : 'textarea',
         width     : 400,
         rows      : 3,
         onblur    : 'ignore',
     });
     $('.edit_area_notes').editable(edit_post_url, {
         type      : 'textarea',
         width     : 400,
         rows      : 3,
         onblur    : 'ignore',
     });
     $('.edit_url').editable(edit_post_url, {
         type      : 'text',
     });
     $('.edit_check').editable(edit_post_url, {
         type      : 'checkbox',
         checkbox: { trueValue: 'Yes', falseValue: 'No' }
     });
     $('.edit_list_multiple').on('click', function() {
        $(this).editable(edit_post_url, {
            type      : 'select',
            multiple: true,
            data    : choice_lists[$(this).attr('id')]
        });
     });
     $('.edit_list_check').on('click', function() {
        var choices = choice_lists[$(this).attr('id')];
        var selected = [];
	// In the template, edit_list_check contents are split on HTML entity New Lines - ie. "&#10;"
	// The New Lines may appear in the template with other code such as breaks - eg. "&#10;<br>" - since
	// only the New Line itself makes it through to this point here in the JavaScript.
	// The New Line appears in its normal JavaScript escaped form - '\n'
        for (var key in choices ) {
	     this.textContent.split(/\n\s*/).indexOf(choices[key]) >= 0 && (selected.push(key));
        }

         $(this).editable(edit_post_url, {
             type: 'multicheckbox',
             onblur: 'ignore',
		     data: $.extend(choice_lists[$(this).attr('id')], { selected: selected })
         })
     });

     $('.edit_list').on('click', function() {
         var choices = choice_lists[$(this).attr('id')];
         var selected;
         for (var key in choices ) {
             choices[key] == this.textContent && (selected = key);
         }

		 $(this).editable(edit_post_url, {
		     type      : 'select',
		     data    : $.extend(choice_lists[$(this).attr('id')], { selected: selected })
		 });
     });

}


var gloss_bloodhound = new Bloodhound({
      datumTokenizer: function(d) { return d.tokens; },
      queryTokenizer: Bloodhound.tokenizers.whitespace,
      remote: {
        url: '/dictionary/ajax/gloss/%QUERY',
        wildcard: '%QUERY'
      },
    });

gloss_bloodhound.initialize();

function glosstypeahead(target) {

     $(target).typeahead(null, {
          name: 'glosstarget',
          display: 'pk',
          source: gloss_bloodhound.ttAdapter(),
          templates: {
              suggestion: function(gloss) {
                  return("<div><strong>" + gloss.idgloss + "</strong></div>");
              }
          }
      });
};


$.editable.addInputType('glosstypeahead', {

   element: function(settings, original) {
      var input = $('<input type="text" class="glosstypeahead">');
      $(this).append(input);

      glosstypeahead(input);

      return (input);
   },
});

/*
 * http://stackoverflow.com/questions/1597756/is-there-a-jquery-jeditable-multi-select-plugin
 */

$.editable.addInputType("multiselect", {
    element: function (settings, original) {
        var select = $('<select multiple="multiple" />');

        if (settings.width != 'none') { select.width(settings.width); }
        if (settings.size) { select.attr('size', settings.size); }

        $(this).append(select);
        return (select);
    },
    content: function (data, settings, original) {
        /* If it is string assume it is json. */
        if (String == data.constructor) {
            eval('var json = ' + data);
        } else {
            /* Otherwise assume it is a hash already. */
            var json = data;
        }
        for (var key in json) {
            if (!json.hasOwnProperty(key)) {
                continue;
            }
            if ('selected' == key) {
                continue;
            }
            var option = $('<option />').val(key).append(json[key]);
            $('select', this).append(option);
        }

        if ($(this).val() == json['selected'] ||
                            $(this).html() == $.trim(original.revert)) {
            $(this).attr('selected', 'selected');
        }

        /* Loop option again to set selected. IE needed this... */
        $('select', this).children().each(function () {
            if (json.selected) {
                var option = $(this);
                $.each(json.selected, function (index, value) {
                    if (option.val() == value) {
                        option.attr('selected', 'selected');
                    }
                });
            } else {
                if (original.revert.indexOf($(this).html()) != -1)
                    $(this).attr('selected', 'selected');
            }
        });
    }
});



function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) { // >
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


function ajaxifyTagForm() {
    // ajax form submission for tag addition and deletion
    $('.tagdelete').on('click', function() {
        var action = $(this).attr('href');
        var tagid = $(this).attr('id');
        var tagelement = $(this).parents('.tagli');

        // This determines the post action: jQuery.post( url [, data ] [, success ] [, dataType ] )
        $.post(action,
              {'tag': tagid, 'delete': "True" },
               function(data) {
                    if (data == 'deleted') {
                        // remove the tag from the page
                       tagelement.remove();
                    }
               });

        return false;
    });

    $('#tagaddform').on('submit', function(){

        var newtag = $('#tagaddform select').val();

        if (newtag != "") {
            $.post($(this).attr('action'), $(this).serialize(),
                    function(data) {
                       // response is a new tag list
                       $('#tags').replaceWith(data);
                       ajaxifyTagForm();
                       $('.editform').show();
                   });
        } else {
            alert("Please select a tag value.");
        }

        return false;
    });
}

function delete_glossurl() {
    $('.glossurl-delete').on('click', function() {
        var action = $(this).attr('href');
        var glossurl_id = $(this).attr('data-glossurl-id');
        var element = $(this).parent();

        // This determines the post action: jQuery.post( url [, data ] [, success ] [, dataType ] )
        $.post(action,
              {'glossurl': glossurl_id})
              .success(function () {
                element.remove();
              });

        return false;
    });

}



