import pymysql
import calendar
from pyecharts.charts import Line, Pie
import pyecharts.options as opts


def get_line():
    datelist = ["1月", "2月", "3月", "4月", "5月", "6月", "7月",
                "8月", "9月", "10月", "11月", "12月"]
    date_count = [0] * 12
    conn = pymysql.connect(host='127.0.0.1',
                           port=3306,
                           user='root',
                           password='1232123',
                           db='xinfang',
                           charset='utf8')
    cursor = conn.cursor()
    sql_date = " SELECT date,COUNT(letter_id) FROM letter GROUP BY date "
    cursor.execute(sql_date)
    dates = cursor.fetchall()
    for date in dates:
        s = date[0].strftime("%Y-%m-%d %H-%M-%S")
        moon = int(s[5:7]) - 1
        date_count[moon] += date[1]
    conn.close()
    line = (
        Line()
            .add_xaxis(datelist)
            .add_yaxis("", date_count)
            .set_global_opts(title_opts=opts.TitleOpts(title="信访数量趋势图"))
    )
    return line


def get_month_line(moon):
    days = calendar.monthrange(2016, moon)[1]
    date_list = range(1, (days + 1))
    date_count = [0] * days
    conn = pymysql.connect(host='127.0.0.1',
                           port=3306,
                           user='root',
                           password='1232123',
                           db='xinfang',
                           charset='utf8')
    cursor = conn.cursor()
    sql_date = " SELECT date,COUNT(letter_id) FROM letter GROUP BY date"
    cursor.execute(sql_date)
    dates = cursor.fetchall()
    for date in dates:
        s = date[0].strftime("%Y-%m-%d %H-%M-%S")
        day = int(s[8:10]) - 1
        date_count[day] += date[1]
    conn.close()
    line = (
        Line()
            .add_xaxis(date_list)
            .add_yaxis("", date_count)
            .set_global_opts(title_opts=opts.TitleOpts(title=str(moon) + "信访数量趋势图"))
    )
    return line


def get_place_pie():

    sql = "SELECT area,COUNT(letter_id) " \
          "FROM (SELECT LEFT(accuseArea,6) as area,letter_id FROM letter) b GROUP BY area"
    conn = pymysql.connect(host='127.0.0.1',
                           port=3306,
                           user='root',
                           password='1232123',
                           db='xinfang',
                           charset='utf8')
    cursor = conn.cursor()
    cursor.execute(sql)
    results = cursor.fetchall()
    area_count = []
    for r in results:
        area = r[0]
        count = r[1]
        area_count.append([area, count])
    conn.close()
    pie = Pie()
    pie.add("", area_count, center=["60%", "50%"], radius=["0%", "75%"])
    pie.set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
    pie.set_global_opts(
        title_opts=opts.TitleOpts(title="地区类别占比"),
        legend_opts=opts.LegendOpts(orient="vertical", pos_top="7%", pos_left="2%"),
    )
    return pie
