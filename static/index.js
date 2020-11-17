$(document).ready(function (e) {
        $("#word").focus();
    }
)
$(document).keydown(function (e) {
    if (e.keyCode === 13) {
        postQuery();
    }
});

//监听牛津8解释页面的外部单词链接
$(document).on('click', 'a', function (e) {
    console.log($(this).attr('href'));
    let href = $(this).attr('href');// "/cool"
    if (href.startsWith("/") && !href.startsWith("/#")) {
        $("#word").val(href.slice(1)) // "cool"
        postQuery();
        e.preventDefault()
    }
});

// ctrl + L trigger input focus
$(window).bind('keyup keydown', function (e) {
    if ((e.ctrlKey || e.metaKey)
        && String.fromCharCode(e.which).toUpperCase() === "L") {
        e.preventDefault();
        $("#word").val("");
        $("#word").focus();
    }
});

function postQuery() {
    let word = $("#word").val().trim();
    let dict = $("#dict-options").val(); //词典
    if (!word || word === "." || word === "#" || word === "?" || word === "/") {
        return;
    }
    $.ajax({
        url: "./",
        type: "POST",
        data: {"word": word, "dict": dict},
        dataType: "html",
        success: function (data) {
            $("#response").html(data);
        }
    });
}

