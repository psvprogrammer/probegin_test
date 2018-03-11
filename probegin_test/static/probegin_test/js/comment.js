$(document).ready(function(){
});

// add new category ajaxPost
$("#btn-add-new-comment").click(function(event){
    event.preventDefault();
    add_comment();
});

function add_comment() {
    elem = $("#new-comment");
    // content = elem.prop('value');
    // post_id = elem.prop('post_id');
    data = {
        post_id: elem.attr('post_id'),
        content: elem.prop('value'),
    };
    ajaxPost('/add-comment/', data, function (content) {
        //on success
        if (content.success){
            elem.prop('value', '')
        }
        else{
            // row = $("#table-new-in_cat");
        }
    });
}