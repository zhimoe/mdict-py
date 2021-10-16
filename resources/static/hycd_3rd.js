// =======设置======= //
/* 
 ______             __  __     _ _      _   
|  ____|           |  \/  |   | (_)    | |  
| |__ _ __ ___  ___| \  / | __| |_  ___| |_ 
|  __| '__/ _ \/ _ \ |\/| |/ _` | |/ __| __|
| |  | | |  __/  __/ |  | | (_| | | (__| |_ 
|_|  |_|  \___|\___|_|  |_|\__,_|_|\___|\__|               
*/
// 仅有一个释义时，隐藏侧边栏的义x，默认开启
var _hycd_hide_pinyin = true; // 如果你不想要这个功能，那就改成 false
// 仅有一个词性时，隐藏侧边栏的词性，默认开启
var _hycd_hide_cixing = true; // 如果你不想要这个功能，那就改成 false
// 点击词头（有拼音的的那一行）隐藏此释义
// 你也可以隐藏全部释义，通过点击词头那一行来开启，emm应该没有人这样吧
// 不过我还是放一个选项在这儿吧
var _hycd_hide_all_parts = false; // 全部隐藏 --> 默认关闭，将这个选项改成 true 打开
// 设置释义按钮渐变深色，默认开启
var _hycd_part_buttons_gradient = true; // 关闭此功能将 true 改成 false 即可
// 只显示第一个释义，通过点击侧边栏的 义2 义3 查看其他释义
// 每次仅显示一个释义，默认关闭
// 当此功能打开时，侧边栏滚动的逻辑会有一些改变
var _hycd_only_display_one_part = false; // 开启此功能将 false 改为 true 即可
// 侧边栏随滑动而滚动，侧边栏就不会显示在其他词典的内容上
// 已知在 goldendict 上如果开了放大页面的话此功能有问题
// 默认打开
var _hycd_sidebar_auto_scroll = true; // 关闭此功能将 true 改成 false 即可

// ====== 结束设置 =========
//
// 代码里为什么不可以写中文？
window.onload = function () {
  var numOfpinyin = document.getElementsByClassName("hycd_3rd_pinyin_part")
    .length;
  if (numOfpinyin <= 1 && _hycd_hide_pinyin) {
    document.getElementsByClassName("hycd_3rd_pinyin")[0].className +=
      " hidden";
  }
  var numOfcixing = document.getElementsByClassName("hycd_3rd_cixing_part")
    .length;
  if (numOfcixing <= 1 && _hycd_hide_cixing) {
    document.getElementsByClassName("hycd_3rd_cixing")[0].className += " hidden";
  }

  var parts = document.getElementsByClassName("hycd_3rd_part");
  for (var i = 0; i < parts.length; i++) {
    if (_hycd_hide_all_parts) {
      parts[i].querySelector("tr[valign=top]").nextSibling.style.display =
        "none";
    }
    var top = parts[i].querySelector("tr[valign=top]");
    top.addEventListener("click", function () {
      if (this.nextSibling.style.display == "none") {
        this.nextSibling.style.display = "block";
      } else {
        this.nextSibling.style.display = "none";
      }
    });
  }

  if (_hycd_part_buttons_gradient) {
    var pinyinButtons = document.getElementsByClassName("hycd_3rd_pinyin_part");
    for (var i = 0; i < pinyinButtons.length; i++) {
      pinyinButton = pinyinButtons[i];
      pinyinButton.style.opacity = 0.2 + 0.031 * i;
    }
  }

  if (_hycd_only_display_one_part) {
    var pinyins = document.getElementsByClassName("hycd_3rd_part");
    for (var i = 1; i < pinyins.length; i++) {
      pinyin = pinyins[i];
      pinyin.style.display = "none";
    }
    for (var i = 0; i < pinyinButtons.length; i++) {
      pinyinButton = pinyinButtons[i];
      pinyinButton.addEventListener("click", function () {
        for (var i = 0; i < pinyins.length; i++) {
          pinyin = pinyins[i];
          pinyin.style.display = "none";
        }
        var id_name = this.querySelector("a").getAttribute("href");
        id_name = id_name.substring(1, id_name.length);
        document.getElementById(id_name).style.display = "block";
      });
    }
  }

  if (_hycd_sidebar_auto_scroll) {
    // 侧边栏随滑动而滚动
    // 已知在 goldendict 上如果开了放大页面的话此功能有问题
    var hycd_3rd_pinyin = this.document.getElementsByClassName(
      "hycd_3rd_pinyin"
    )[0];
    var hycd_3rd_cixing = this.document.getElementsByClassName(
      "hycd_3rd_cixing"
    )[0];
    // 要最后一个元素
    var hycd_3rd_cixing_last = this.document.getElementsByClassName(
      "hycd_3rd_cixing_part"
    );
    hycd_3rd_cixing_last =
      hycd_3rd_cixing_last[hycd_3rd_cixing_last.length - 1];

    var hycd_3rd_dingwei_top = this.document.getElementById(
      "hycd_3rd_dingwei_top"
    );
    var hycd_3rd_dingwei_bottom = this.document.getElementById(
      "hycd_3rd_dingwei_bottom"
    );
    var hycd_3rd_page_height = document.body.clientHeight;
    sidebar_scroll(
      hycd_3rd_pinyin,
      hycd_3rd_cixing,
      hycd_3rd_cixing_last,
      hycd_3rd_dingwei_top,
      hycd_3rd_dingwei_bottom,
      hycd_3rd_page_height
    );
    window.addEventListener("scroll", function () {
      sidebar_scroll(
        hycd_3rd_pinyin,
        hycd_3rd_cixing,
        hycd_3rd_cixing_last,
        hycd_3rd_dingwei_top,
        hycd_3rd_dingwei_bottom,
        hycd_3rd_page_height
      );
    });
  }
};

function sidebar_scroll(
  hycd_3rd_pinyin,
  hycd_3rd_cixing,
  hycd_3rd_cixing_last,
  hycd_3rd_dingwei_top,
  hycd_3rd_dingwei_bottom,
  hycd_3rd_page_height
) {
  var rect_pinyin = hycd_3rd_pinyin.getBoundingClientRect(); // 计算目标元素和视口的距离
  var rect_cixing = hycd_3rd_cixing_last.getBoundingClientRect();
  var rect_top = hycd_3rd_dingwei_top.getBoundingClientRect();
  var rect_bottom = hycd_3rd_dingwei_bottom.getBoundingClientRect();
  //   if (!_hycd_only_display_one_part) {
  // 兼容性问题，不执行这个逻辑，如果你想修改或者尝试，可以试一下，在 goldendict mdictPC 是没有问题的。
  if (false) {
    if (rect_cixing.bottom > rect_bottom.bottom) {
      hycd_3rd_cixing.style.top = "";
      hycd_3rd_pinyin.style.top = "";
      hycd_3rd_cixing.style.bottom =
        hycd_3rd_page_height - rect_bottom.bottom + "px";
      hycd_3rd_pinyin.style.bottom =
        hycd_3rd_page_height -
        rect_bottom.bottom +
        hycd_3rd_page_height * 0.3 +
        "px";
    } else {
      // hycd_3rd_cixing.style.top = ""
      // hycd_3rd_pinyin.style.top = ""
      // if (
      //     rect_bottom.bottom - rect_cixing.bottom >
      //     hycd_3rd_page_height * 0.3
      // ) {
      //     hycd_3rd_cixing.style.bottom = hycd_3rd_page_height * 0.3;
      //     hycd_3rd_pinyin.style.bottom = hycd_3rd_page_height * 0.6;
      // }
    }

    if (rect_pinyin.top < rect_top.top) {
      hycd_3rd_cixing.style.bottom = "";
      hycd_3rd_pinyin.style.bottom = "";
      hycd_3rd_pinyin.style.top = rect_top.top + "px";
      hycd_3rd_cixing.style.top =
        rect_top.top + hycd_3rd_page_height * 0.3 + "px";
    } else {
    }
  } else {
    // 开启了 仅显示一个释义之后逻辑改变
    // 这个逻辑不怎么优雅，trust me, I have done my best
    if (rect_bottom.bottom < 0 || rect_top.top > hycd_3rd_page_height) {
      hycd_3rd_pinyin.style.display = "none";
      hycd_3rd_cixing.style.display = "none";
    } else {
      hycd_3rd_pinyin.style.display = "";
      hycd_3rd_cixing.style.display = "";
    }
  }
}
