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
        '2017-12-30': '2018-01-02',
        '2017-12-31': '2018-01-02',
        '2018-01-01': '2018-01-02',
        '2018-02-15': '2018-02-22',
        '2018-02-16': '2018-02-22',
        '2018-02-17': '2018-02-22',
        '2018-02-18': '2018-02-22',
        '2018-02-19': '2018-02-22',
        '2018-02-20': '2018-02-22',
        '2018-02-21': '2018-02-22',
        '2018-04-05': '2018-04-08',
        '2018-04-06': '2018-04-08',
        '2018-04-07': '2018-04-08',
        '2018-04-29': '2018-05-02',
        '2018-04-30': '2018-05-02',
        '2018-05-01': '2018-05-02',
        '2018-06-16': '2018-06-19',
        '2018-06-17': '2018-06-19',
        '2018-06-18': '2018-06-19',
        '2018-09-22': '2018-09-25',
        '2018-09-23': '2018-09-25',
        '2018-09-24': '2018-09-25',
        '2018-10-01': '2018-10-08',
        '2018-10-02': '2018-10-08',
        '2018-10-03': '2018-10-08',
        '2018-10-04': '2018-10-08',
        '2018-10-05': '2018-10-08',
        '2018-10-06': '2018-10-08',
        '2018-10-07': '2018-10-08',
        '2018-12-30': '2019-01-02',
        '2018-12-31': '2019-01-02',
        '2019-01-01': '2019-01-02',
        '2019-02-04': '2019-02-11',
        '2019-02-05': '2019-02-11',
        '2019-02-06': '2019-02-11',
        '2019-02-07': '2019-02-11',
        '2019-02-08': '2019-02-11',
        '2019-02-09': '2019-02-11',
        '2019-02-10': '2019-02-11',
        '2019-04-05': '2019-04-08',
        '2019-04-06': '2019-04-08',
        '2019-04-07': '2019-04-08',
        '2019-04-27': '2019-04-28',
        '2019-05-01': '2019-05-05',
        '2019-05-02': '2019-05-05',
        '2019-05-03': '2019-05-05',
        '2019-05-04': '2019-05-05',
        '2019-06-07': '2019-06-10',
        '2019-06-08': '2019-06-10',
        '2019-06-09': '2019-06-10',
        '2019-09-13': '2019-09-16',
        '2019-09-14': '2019-09-16',
        '2019-09-15': '2019-09-16',
        '2019-10-01': '2019-10-08',
        '2019-10-02': '2019-10-08',
        '2019-10-03': '2019-10-08',
        '2019-10-04': '2019-10-08',
        '2019-10-05': '2019-10-08',
        '2019-10-06': '2019-10-08',
        '2019-10-07': '2019-10-08',
        '2020-01-01': '2020-01-02',
        '2020-01-24': '2020-01-31',
        '2020-01-25': '2020-01-31',
        '2020-01-26': '2020-01-31',
        '2020-01-27': '2020-01-31',
        '2020-01-28': '2020-01-31',
        '2020-01-29': '2020-01-31',
        '2020-01-30': '2020-01-31',
        '2020-04-04': '2020-04-07',
        '2020-04-05': '2020-04-07',
        '2020-04-06': '2020-04-07',
        '2020-05-01': '2020-05-04',
        '2020-05-02': '2020-05-04',
        '2020-05-03': '2020-05-04',
        '2020-06-25': '2020-06-28',
        '2020-06-26': '2020-06-28',
        '2020-06-27': '2020-06-28',
        '2020-10-01': '2020-10-08',
        '2020-10-02': '2020-10-08',
        '2020-10-03': '2020-10-08',
        '2020-10-04': '2020-10-08',
        '2020-10-05': '2020-10-08',
        '2020-10-06': '2020-10-08',
        '2020-10-07': '2020-10-08'
    };
    var workdays = ['2018-02-11',
        '2018-02-24',
        '2018-04-08',
        '2018-04-28',
        '2018-09-29',
        '2018-09-30',
        '2018-12-29',
        '2019-02-02',
        '2019-02-03',
        '2019-04-28',
        '2019-05-05',
        '2019-09-29',
        '2019-10-12',
        '2020-01-19',
        '2020-02-01',
        '2020-06-28',
        '2020-10-10'
    ];
    var pjenddate = $("input[name='pjenddate']").val();//到期日期
    var outpjdate = $("input[name='outpjdate']").val();//贴现日期
    var dqrReal = new Date((pjenddate.replace(/-/g, '/')));
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
    var dqr = new Date((pjenddate.replace(/-/g, '/')));
    var txr = new Date((outpjdate.replace(/-/g, '/')));
    var readTs = Math.floor(dqrReal.getTime() / (24 * 60 * 60 * 1000)) - Math.floor(txr.getTime() / (24 * 60 * 60 * 1000));
    console.log(readTs);
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
    return [ts,ts-readTs];
}

//计算利率
function getlilv() {
    var inputJinE = $("#tje");
    var je = inputJinE.val();
    if (isNaN(je) || je <=0) {
        console.log("金额："+je);
        je = 100000;
        inputJinE.val(10);
    }else{
        je = je * 10000
    }
    var lixi = $("#everytenprice").val();
    if (isNaN(lixi))
        lixi = 0;
    var realLixi = je * lixi / 100000;
    var days = getDays();
    console.log(days);
    var ts = days[0];
    $("#jxtsd").text(ts);
    $("#tztsd").text(days[1]);
    // $("#txlxd").text(realLixi);
    // $("#jined").text(je - realLixi);
    // $("#real_jine").text(je - realLixi);
    $("#txlxd").text(numeral(realLixi).format('0,0.00'));
    $("#real_jine").text((je - realLixi).toFixed(3));
    $("#jined").text(numeral(je - realLixi).format('0,0.00'));
    var lilv = 0;
    if (ts > 0){
        lilv = (lixi / je / ts * 30 * 1000).toFixed(2);
    }
    $("#txlvi").val(lilv);
    $("#yxlvi").val(lilv * 1.2);
    console.log(lilv);
    // calctxlxone();
}

//按贴现计算
// function calctxlxoneb() {
//     var je = $("input[name='je']").val();
//     var everyten = $("input[name='everyten']").val();
//     var ts = 0;
//     var txlx = (everyten * je / 10).toFixed(2);
//     var jine = (je * 10000 - txlx).toFixed(2);
//     if (isNaN(txlx))
//         txlx = 0;
//     if (isNaN(jine))
//         jine = 0;
//     $("#jxtsd").text(ts);
//     $("#txlxd").text(txlx);
//     $("#jined").text(jine);
//     console.log(jine * 10 / je);
//     $("#everytenprice").val((txlx * 10 / je).toFixed(2));
// }

//按利率计算
function countbylilv(je) {
    var txlv = $("input[name='yxlv']").val();
    var sxf = parseInt($("input[name='sxf']").val());
    var days = getDays();
    console.log(days);
    var ts = days[0];
    // je * 10000 * ts * (txlv/30/1000)
    // je * 10000 * ts * (txlv/360/100)
    var txlx = (je * ts * txlv / 3.6  + je * sxf / 10).toFixed(2);
    var jine = (je * 10000 - je * txlv/3.6 * ts- je/ 10 * sxf ).toFixed(2);//(rililv=txlv/1000/30)
    var everytenprice = (txlx * 10 / je).toFixed(2);
    if (isNaN(ts))
        ts = 0;
    if (isNaN(txlx))
        txlx = 0;
    if (isNaN(jine))
        jine = 0;
    return [ts,days[1],txlx,jine,everytenprice];
}
//按利率计算
function calctxlxone() {
    var je = $("input[name='je']").val();
    var results = countbylilv(je);
    $("#jxtsd").text(results[0]);
    $("#tztsd").text(results[1]);
    $("#txlxd").text(numeral(results[2]).format('0,0.00'));
    $("#jined").text(numeral(results[3]).format('0,0.00'));
    $("#everytenprice").val(results[4]);
    $("#real_jine").text(results[3]);
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
        $("#yxlvi").val(mlv.toFixed(3));
    }
    if (type == 'y' && !isNaN(vals)) {
        var ylv = numDiv(val, 1.2);
        $("#txlvi").val(ylv.toFixed(5));
    }
    return true;
}