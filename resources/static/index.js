$(document).ready(function (e) {
        $('#word').focus();
    }
);

//监听回车键
$(document).keydown(function (e) {
    if (e.keyCode === 13) {
        postQuery();
    }
});

//监听牛津8解释页面的外部单词链接
$(document).on('click', 'a', function (e) {
    console.log($(this).attr('href'));
    let href = $(this).attr('href');// '/cool'
    if (href.startsWith('/') && !href.startsWith('/#')) {
        $('#word').val(href.slice(1)) // 'cool'
        postQuery();
        e.preventDefault()
    }
});

function postQuery() {
    let word = $('#word').val().trim();
    if (!validInput(word)) {
        return;
    }
    queryMdx(word);

}

/**
 * 特殊字符不查询
 * @param word
 * @return boolean
 */
function validInput(word) {
    return word
        && word !== '.'
        && word !== '#'
        && word !== '?'
        && word !== '/';
}

/*查询mdx*/
function queryMdx(word) {
    $('#mdx-resp').html('查询中...');
    $.ajax({
        url: './query',
        type: 'POST',
        data: {'word': word},
        dataType: 'html',
        success: function (data) {
            if (data !== '') {
                $('#mdx-resp').html(data).show();
            } else {
                $('#mdx-resp').hide();
            }
        }
    });
}


// 捕获ctrl+L快捷键
$(window).bind('keyup keydown', function (e) {
    if ((e.ctrlKey || e.metaKey)
        && String.fromCharCode(e.which).toLowerCase() === 'l') {
        e.preventDefault();
        $('#word').val('').focus();//清空
    }
});