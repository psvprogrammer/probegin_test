$(document).ready(function(){
    handle_table_td_clicks();
    init_budget_select_change(budget_select);

    $("#table-new-in_cat").on('show', function(){
        $("#new-in_cat-name").focus();
    });
});

$("#btn-show-new-in-cat-row").click(function(event){
    event.preventDefault();
    $(this).hide();
    $("#table-new-in_cat").show();
    $("#btn-cancel-new-in-cat").show();
});

$("#btn-cancel-new-in-cat").click(function(event){
    event.preventDefault();
    $("#table-new-in_cat").hide();
    $(this).hide();
    $("#btn-show-new-in-cat-row").show();
});

// add new category ajaxPost
$("#btn-add-new-in_cat").click(function(event){
    event.preventDefault();
    add_in_cat();
});

//cancel delete income source click
$(".cancel-del").each(function () {
    $(this).on('click', function (event) {
        row_elem = $(this).parent().parent();
        row_elem.hide();
    });
});

//force delete income source click
$(".force-del").each(function () {
    $(this).on('click', function (event) {
        id = $(this).prop('id').replace('force-del-in_cat-id_', '');
        force_delete_in_cat(id);
    });
});

/* table td click events: Save | Cancel | Delete buttons
/* and "Enter" key pres event equals to 'Save' button click */
function handle_table_td_clicks() {
    $("#table-in_cat>tbody>tr>td").each(function () {

        $(this).on('click', function (event) {
            row_elem = $(this).parent();

            // xs row template (action buttons in separate row)
            if (!row_elem.prop('id')){
                row_elem = $(this).parent().prev();
            }

            id = row_elem.prop('id').replace('in_cat-id_', '');
            if (event.target.tagName == 'BUTTON'){
                if (event.target.innerText == 'Save'){
                    save_in_cat(id);
                }
                else if(event.target.innerText == 'Delete') {
                    delete_in_cat(id);
                }
                else if(event.target.innerText == 'Cancel') {
                    restore_init_values(id);
                }
                focusout_row(id, row_elem, event);
            }
            else{
                focusin_row(id, row_elem, event);
            }
        });

        $(this).on('focusout', function (event) {
            event.preventDefault();
            active_table = $(':active').closest('table');
            if (active_table.prop('id') != 'table-in_cat'){
                event.target.focus();
            }
        });
    });

    // bind "Enter" key press with 'Save' button click
    $("#table-in_cat>tbody>tr>td.field").each(function () {
        $(this).on('keypress', function (e) {
            if(e.which === 13){
                id = $(this).parent().prop('id').replace('in_cat-id_', '');
                $("#btn-edit-in_cat-id_" + id).click();
            }
        });
    });
}

function restore_init_values(id) {
    $("#new_name-id_" + id).prop('value', $("#name-id_" + id).html());
}

function focusin_row(id, row_elem, event) {
    if (!row_elem){
        row_elem = $('#in_cat-id_'+id);
    }

    row_elem.find('td.field').each(function () {
        p = $(this).find('p');
        input = $(this).find('input');

        // input.prop('value', p.html());
        p.hide();
        input.show();
    });

    $("#btn-edit-in_cat-id_"+id).show();
    $("#btn-cancel-in_cat-id_"+id).show();
    $("#btn-del-in_cat-id_"+id).show();
    if (event){
        test = event.target;

        // event.target.focus();
        $("input#new_" + event.target.id).focus();
        event.stopPropagation();
    }

    // focusout all other rows
    $("#table-in_cat>tbody>tr").each(function () {
        current_id = $(this).prop('id').replace('in_cat-id_', '');
        if (current_id != id){
            focusout_row(current_id, $(this));
        }
    });
}

function focusout_row(id, row_elem, event) {
    if (!row_elem){
        row_elem = $('#in_cat-id_'+id);
    }

    row_elem.find('td.field').each(function () {
        p = $(this).find('p');
        input = $(this).find('input');

        // p.html(input.prop('value'));
        p.show();
        input.hide();
    });

    $("#btn-edit-in_cat-id_"+id).hide();
    $("#btn-cancel-in_cat-id_"+id).hide();
    $("#btn-del-in_cat-id_"+id).hide();
    row_elem.focusout();
    if (event){
        event.stopPropagation();
    }
}

function save_in_cat(id) {
    name_elem = $('input#new_name-id_' + id);
    descr_elem = $('input#new_description-id_' + id);

    name = name_elem.parent().find('p').html();
    descr = descr_elem.parent().find('p').html();
    new_name = name_elem.prop('value');
    new_descr = descr_elem.prop('value');
    if (name != new_name || descr != new_descr){
        // if any changes - save them!
        data = {
            id: id,
            name: new_name,
            description: new_descr,
        };
        ajaxPost('ajax/edit-in-cat', data, function (content) {
            row = $("#in_cat-id_" + id);
            if (content.success){
                name_elem.parent().find('p').html(name_elem.prop('value'));
                descr_elem.parent().find('p').html(descr_elem.prop('value'));
            }
            else{
                focusin_row(id);
            }
            show_popover(row, content.popover, $("#btn-edit-in_cat-id_" + id));
        });
    }
}

function add_in_cat() {
    //post to ajax and on success
    name = $("input#new-in_cat-name").prop('value');
    description = $("input#new-in_cat-description").prop('value');
    data = {
        id: '0', // just for correct query
        name: name,
        description: description,
    };
    ajaxPost('ajax/add-in-cat', data, function (content) {
        //on success
        if (content.success){
            row = $("#in_cat-id_" + content.id);

            $("#table-new-in_cat").hide();
            $("#btn-cancel-new-in-cat").hide();
            $("#btn-show-new-in-cat-row").show();
        }
        else{
            row = $("#table-new-in_cat");
        }
        show_popover(row, content.popover, $("#btn-add-new-in_cat"));
        handle_table_td_clicks();
    });
}

function delete_in_cat(id) {
    data = {
        id: id,
    };
    ajaxPost('ajax/del-in-cat', data, function (content) {
        //on success
        if (content.success){
            $('#in_cat-id_' + id).remove();
        }
        else{
            warning_row = $('#in_cat_warnings-id_' + id);
            $('#delete-warning-id_' + id).html(content.popover.content);
            warning_row.show();
        }
    });
}

function force_delete_in_cat(id) {
    data = {
        id: id,
    };
    ajaxPost('ajax/force-del-in-cat', data, function (content) {
        //on success
        if (content.success){
            $('#in_cat-id_' + id).remove();
            $('#in_cat_warnings-id_' + id).remove();
        }
        elem = $("tr[id^='in_cat-id_']").last();
        show_popover(elem, content.popover);
    });
}

function budget_select() {
    getAjaxPage('/income-categories');
}