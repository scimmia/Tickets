// $(function () {
//     $('.dateinput').datepicker({
//         language: "zh-CN",
//         daysOfWeekHighlighted: "0,6",
//         autoclose: true,
//         todayHighlight: true, //自动关闭
//         clearBtn: true,          //显示清除按钮
//         format: 'yyyy/mm/dd',
//     });
// });

function getDays() {
    var isholiday = false;
    var isworkday = false;
    var holidays = {
        '2017/12/30': '2018/01/02',
        '2017/12/31': '2018/01/02',
        '2018/01/01': '2018/01/02',
        '2018/02/15': '2018/02/22',
        '2018/02/16': '2018/02/22',
        '2018/02/17': '2018/02/22',
        '2018/02/18': '2018/02/22',
        '2018/02/19': '2018/02/22',
        '2018/02/20': '2018/02/22',
        '2018/02/21': '2018/02/22',
        '2018/04/05': '2018/04/08',
        '2018/04/06': '2018/04/08',
        '2018/04/07': '2018/04/08',
        '2018/04/29': '2018/05/02',
        '2018/04/30': '2018/05/02',
        '2018/05/01': '2018/05/02',
        '2018/06/16': '2018/06/19',
        '2018/06/17': '2018/06/19',
        '2018/06/18': '2018/06/19',
        '2018/09/22': '2018/09/25',
        '2018/09/23': '2018/09/25',
        '2018/09/24': '2018/09/25',
        '2018/10/01': '2018/10/08',
        '2018/10/02': '2018/10/08',
        '2018/10/03': '2018/10/08',
        '2018/10/04': '2018/10/08',
        '2018/10/05': '2018/10/08',
        '2018/10/06': '2018/10/08',
        '2018/10/07': '2018/10/08',
        '2018/12/30': '2019/01/02',
        '2018/12/31': '2019/01/02',
        '2019/01/01': '2019/01/02',
        '2019/02/04': '2019/02/11',
        '2019/02/05': '2019/02/11',
        '2019/02/06': '2019/02/11',
        '2019/02/07': '2019/02/11',
        '2019/02/08': '2019/02/11',
        '2019/02/09': '2019/02/11',
        '2019/02/10': '2019/02/11',
        '2019/04/05': '2019/04/08',
        '2019/04/06': '2019/04/08',
        '2019/04/07': '2019/04/08',
        '2019/04/29': '2019/05/02',
        '2019/04/30': '2019/05/02',
        '2019/05/01': '2019/05/02',
        '2019/06/07': '2019/06/20',
        '2019/06/08': '2019/06/20',
        '2019/06/09': '2019/06/20',
        '2019/09/13': '2019/09/16',
        '2019/09/14': '2019/09/16',
        '2019/09/15': '2019/09/16',
        '2019/10/01': '2019/10/08',
        '2019/10/02': '2019/10/08',
        '2019/10/03': '2019/10/08',
        '2019/10/04': '2019/10/08',
        '2019/10/05': '2019/10/08',
        '2019/10/06': '2019/10/08',
        '2019/10/07': '2019/10/08'
    };
    var workdays = ['2018/02/11',
        '2018/02/24',
        '2018/04/08',
        '2018/04/28',
        '2018/09/29',
        '2018/09/30',
        '2018/12/29',
        '2019/02/02',
        '2019/02/03',
        '2019/04/27',
        '2019/04/28',
        '2019/09/28',
        '2019/09/29'
    ];
    var pjenddate = $("input[name='pjenddate']").val();
    var outpjdate = $("input[name='outpjdate']").val();
    for (var key in holidays) {
        if (pjenddate === key) {
            console.log("pjenddate: " + pjenddate + " ,holidays: " + holidays[key]);
            pjenddate = holidays[key];
            isholiday = true;
            break;
        }
    }
    if (!isholiday) {
        for (i = 0; i < workdays.length; i++) {
            if (pjenddate === workdays[i]) {
                console.log("pjenddate: " + pjenddate + " ,workdays: " + workdays[i]);
                isworkday = true;
                break;
            }
        }
    }
    console.log(pjenddate);
    var dqr = new Date((pjenddate.replace(/-/g, '/')));
    var txr = new Date((outpjdate.replace(/-/g, '/')));
    var tzts = parseInt($("input[name='tzts']").val());
    if (isNaN(tzts))
        tzts = 0;
    var ts = Math.floor(dqr.getTime() / (24 * 60 * 60 * 1000)) - Math.floor(txr.getTime() / (24 * 60 * 60 * 1000)) + tzts;
    if (!isworkday && !isholiday) {
        var week = dqr.getDay();
        if (week === 0) {
            ts = ts + 1;
        } else if (week === 6) {
            ts = ts + 2;
        }
    }
    if ($("#piaozhi").is(":checked")) {
        ts = ts + 3;
    }
    if (isNaN(ts))
        ts = 0;
    return ts;
}

function getlilv() {
    var lixi = $("#everytenprice").val();
    var je = 100000;
    if (isNaN(lixi))
        lixi = 0;
    var ts = getDays();
    $("#tje").val(10);
    $("#jxtsd").text(ts);
    $("#txlxd").text(lixi);
    $("#jined").text(je - lixi);
    var lilv = lixi / je / ts * 30 * 1000;
    if (isNaN(lilv))
        lilv = 0;
    $("#txlvi").val(lilv);
    $("#yxlvi").val(lilv * 1.2);
    console.log(lilv);
}

//按贴现计算
function calctxlxoneb() {
    var je = $("input[name='je']").val();
    var everyten = $("input[name='everyten']").val();
    var ts = 0;
    var txlx = Math.round(everyten * je) / 10;
    var jine = Math.round(je * 10000 - txlx);
    if (isNaN(txlx))
        txlx = 0;
    if (isNaN(jine))
        jine = 0;
    $("#jxtsd").text(ts);
    $("#txlxd").text(txlx);
    $("#jined").text(jine);
    console.log(jine * 10 / je);
    $("#everytenprice").val(Math.round(txlx * 10 / je));
}

//按利率计算
function calctxlxone() {
    var je = $("input[name='je']").val();
    var txlv = $("input[name='txlv']").val();
    var sxf = parseInt($("input[name='sxf']").val());
    //alert(tzts);
    var ts = getDays();
    var txlx = Math.round(je * txlv * ts / 3 * 100) / 100 + je * sxf / 10;
    var jine = Math.round(je * 1000000 - je * txlv * ts / 3 * 100) / 100 - je * sxf / 10;
    if (isNaN(ts))
        ts = 0;
    if (isNaN(txlx))
        txlx = 0;
    if (isNaN(jine))
        jine = 0;
    $("#jxtsd").text(ts);
    $("#txlxd").text(txlx);
    $("#jined").text(jine);
    $("#everytenprice").val(txlx * 10 / je);
    console.log(jine * 10 / je);
}

function numDiv(num1, num2) {
    var baseNum1 = 0, baseNum2 = 0;
    var baseNum3, baseNum4;
    try {
        baseNum1 = num1.toString().split(".")[1].length;
    } catch (e) {
        baseNum1 = 0;
    }
    try {
        baseNum2 = num2.toString().split(".")[1].length;
    } catch (e) {
        baseNum2 = 0;
    }
    with (Math) {
        baseNum3 = Number(num1.toString().replace(".", ""));
        baseNum4 = Number(num2.toString().replace(".", ""));
        return (baseNum3 / baseNum4) * pow(10, baseNum2 - baseNum1);
    }
}

function numMulti(num1, num2) {
    var baseNum = 0;
    try {
        baseNum += num1.toString().split(".")[1].length;
    } catch (e) {
    }
    try {
        baseNum += num2.toString().split(".")[1].length;
    } catch (e) {
    }
    return Number(num1.toString().replace(".", "")) * Number(num2.toString().replace(".", "")) / Math.pow(10, baseNum);
}

function getVal(val, type) {
    var vals = parseFloat(val);
    if (type == 'm' && !isNaN(vals)) {
        var mlv = numMulti(val, 1.2);
        $("#yxlvi").val(mlv.toFixed(5));
    }
    if (type == 'y' && !isNaN(vals)) {
        var ylv = numDiv(val, 1.2);
        $("#txlvi").val(ylv.toFixed(4));
    }
    return true;
}