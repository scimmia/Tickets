function initDatePicker(val) {
    val.datepicker({
        language: "zh-CN",
        autoclose: true,
        todayHighlight: true, //自动关闭
        clearBtn: true,          //显示清除按钮
        format: 'yyyy/mm/dd',
    });
}