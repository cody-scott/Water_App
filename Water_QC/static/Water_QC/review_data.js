
function get_id(e) {
    return $(e).closest(".parent_id").attr("id")
}

function accept_click(e) {
    var id = get_id(e);
    console.log(id);
    if (e.checked === true) {
        $("#reject_" + id)[0].checked = false;
    }
    push_change_to_api(id);
}

function reject_click(e) {
    var id = get_id(e);
    console.log(id);

    var comments_area = "#commentstextarea_" + id;
    if (e.checked === true) {
        // $(comments_area).removeAttr("hidden");
        $("#accept_" + id)[0].checked = false;
    }
    // else {
    //     $(comments_area).attr("hidden","hidden");
    // }
    push_change_to_api(id);
}

// var last_feature = null;
function copy_query_click(e) {
    // var tmp = $("#1").closest(".type_data").attr("id");
    // if (last_feature === tmp) {
    //
    // }

    var text_area = $(".copy_query_" + e);
    $(text_area).removeAttr("hidden");
    $(text_area).select();
    document.execCommand("copy");
    $(text_area).attr("hidden","hidden");
    console.log("copied");
}

function push_change_to_api(feature_id) {
    var ac_status = $("#accept_" + feature_id)[0].checked;
    var rj_status = $("#reject_" + feature_id)[0].checked;
    var comments = $("#commentstextarea_" + feature_id)[0].value;

    var comments_area = "#commentstextarea_" + feature_id;
    if (rj_status === true) {
        $(comments_area).removeAttr("hidden");
    }
    else {
        $(comments_area).attr("hidden","hidden");
    }

    var qc_status;
    if (rj_status === true) {
        qc_status = false;
    }
    else if (ac_status === true) {
        qc_status = true;
    }
    else {
        qc_status = null;
    }

    console.log(qc_status);
    console.log(comments);

    $.ajax({
        url: '/api/feature/' + feature_id + '/',
        method: 'PUT',
        data: {
            qc_comments: comments,
            qc_approved: qc_status
        },
        success: function() {
            console.log("Success")
        },
        error: function(e) {
            console.log(e);
        },
    });
}


function copy_mxd(e) {
    var js_tmp = $("#copy_ta");
    $(js_tmp).removeAttr("hidden");
    $(js_tmp).select();
    document.execCommand("copy");
    $(js_tmp).attr("hidden","hidden");
}


function toggle_vis(e) {
    if ($(e).attr("hidden") === undefined) {
        $(e).attr("hidden", "hidden");
    }
    else{
        $(e).removeAttr("hidden");
    }
}


$(document).ready(function() {
    $.ajaxSetup({
        headers:
            { 'X-CSRFToken': $('meta[name="csrf-token"]').attr('content') }
    });
});
