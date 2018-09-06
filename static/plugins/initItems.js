function initDatePicker(val) {
    val.datepicker({
        language: "zh-CN",
        autoclose: true,
        todayHighlight: true, //自动关闭
        clearBtn: true,          //显示清除按钮
        format: 'yyyy-mm-dd',
    });
    val.attr("autocomplete","off")
    val.find("input").attr("autocomplete","off")
}
function initSortTable(val) {
    return val.DataTable({
                'paging': false,
                'lengthChange': false,
                'searching': false,
                'ordering': true,
                'info': true,
                'autoWidth': false,
                'scrollY': 410,
                "language": {
                    "processing": "处理中...",
                    "lengthMenu": "显示 _MENU_ 项结果",
                    "zeroRecords": "没有匹配结果",
                    "info": "",
                    "infoEmpty": "显示第 0 至 0 项结果，共 0 项",
                    "infoFiltered": "(由 _MAX_ 项结果过滤)",
                    "infoPostFix": "",
                    "search": "搜索:",
                    "searchPlaceholder": "搜索...",
                    "url": "",
                    "emptyTable": "表中数据为空",
                    "loadingRecords": "载入中...",
                    "infoThousands": ",",
                    "paginate": {
                        "first": "首页",
                        "previous": "上页",
                        "next": "下页",
                        "last": "末页"
                    },
                    "aria": {
                        "paginate": {
                            'first': '首页',
                            'previous': '上页',
                            'next': '下页',
                            'last': '末页'
                        },
                        "sortAscending": ": 以升序排列此列",
                        "sortDescending": ": 以降序排列此列"
                    },
                }
            });
}