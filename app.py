from flask import Flask, render_template, request, url_for, make_response
import backend
import students
import pandas as pd
from backend import check_df, check_dfw, check_match, get_absents, check_today
# from flask_sqlalchemy import SQLAlchemy


mod_df = pd.DataFrame
filename = ''
opt = ''

app = Flask(__name__)
@app.route('/', methods=['GET', 'POST'])
def fuc():
    global opt
    if request.method == 'POST':
        opt = request.form.get('opt')
        if opt == 'null':
            return render_template('index.html', err_m='select an option...!')
        if opt == 'vvit':
            return render_template('vvit.html')
        return render_template('others.html')
    return render_template("index.html")


@app.route('/vvit', methods=['GET', 'POST'])
def result():
    global mod_df, filename
    if request.method == 'POST':
        branch = request.form.get('branch')
        year = request.form.get('year')
        filtr = int(request.form.get('filter'))
        subject = request.form['subject']
        subject = subject.upper()
        # print(type(year),year)
        # x = document.getElementById("file").value

        if branch == 'select_b' or year == 'select_y' or subject == '':
            return render_template('vvit.html', err_m='ERROR',
                                   error='please select year, branch and enter subject')

        # detecting the unicode for the given file
        # import chardet
        # x = request.files[r'file']
        # print(x.filename)

        # with open(x.filename, 'rb') as rawdata:
        #     result = chardet.detect(rawdata.read(10000))
        # encode = result['encoding']
        # df = pd.read_csv(x.filename, encoding=encode,
        #                  sep='[\t,]', engine='python')#sep='\s+'

        try:
            df = pd.read_csv(request.files.get(r'file'),
                             encoding='utf-16', delimiter='\t')
            # dfw = pd.read_csv(request.files.get(r'file2'))

        except:
            return render_template('vvit.html', err_m='ERROR',
                                   error='select proper csv input file')

        if check_df(df) != True:
            # mesg=check_df(df)
            return render_template('vvit.html', err_m='ERROR',
                                   error='"Full Name" or "User Action" or "Timestamp" column(s) is missing in MS teams file.')

        masterfl = branch+year
        dfw = students.getlist(masterfl)

        if check_dfw(dfw) != True:
            # mesg=check_dfw(dfw)
            return render_template('vvit.html', err_m='ERROR',
                                   error='"REGD NO"  or "FullName" column(s) is missing in students file.')

        if check_match(df, dfw) != True:
            # mesg=check_match(df,dfw)
            return render_template('vvit.html', err_m='ERROR',
                                   error='This two files doesnt match, please check and try again.')

        if check_today(df, dfw) != True:
            return render_template('vvit.html', err_m='ERROR',
                                   error='The student file already contain data from attendance file')
        try:
            mod_df, class_duration, today_date, pr_cnt, ab_cnt = backend.main_fuc(
                df, dfw, filtr)
        except:
            return render_template('vvit.html', err_m='ERROR',
                                   error='something went wrong, please check your file')

        absents_list = get_absents(mod_df, today_date)
        ab_cnt = str(len(absents_list))
        tday_date = today_date.replace('/', '')
        filename = year+'_'+branch+'_'+subject+'_'+tday_date+'.csv'

        return render_template('results.html',
                               shape='Completed successfully',
                               year_ht='year: '+year,
                               branch_ht='Branch: '+branch,
                               subject_ht='Subject: '+subject,
                               class_dur='class duration: '+class_duration+'mins',
                               today='Date: '+today_date,
                               present='Present: '+pr_cnt,
                               absent='Absent: '+ab_cnt,
                               list_absent=absents_list,
                               filtr=filtr)

    return render_template('vvit.html')


@app.route("/others", methods=["GET", "POST"])
def home():
    global mod_df, filename, opt
    if request.method == 'POST':
        branch = request.form.get('branch')
        year = request.form.get('year')
        filtr = int(request.form.get('filter'))
        subject = request.form['subject']
        subject = subject.upper()
        # print(type(year),year)

        if branch == 'select_b' or year == 'select_y' or subject == '':
            return render_template('others.html', err_m='ERROR',
                                   error='please select year, branch and enter subject')
        try:
            df = pd.read_csv(request.files.get(r'file'),
                             encoding='utf-16', delimiter='\t')
            dfw = pd.read_csv(request.files.get(r'file2'))
        except:
            return render_template('others.html', err_m='ERROR',
                                   error='select proper csv input file')
        if check_df(df) != True:
            # mesg=check_df(df)
            return render_template('others.html', err_m='ERROR',
                                   error='"Full Name" or "User Action" or "Timestamp" column(s) is missing in MS teams file.')
        if check_dfw(dfw) != True:
            # mesg=check_dfw(dfw)
            return render_template('others.html', err_m='ERROR',
                                   error='"REGD NO"  or "FullName" column(s) is missing in students file.')

        if check_match(df, dfw) != True:
            # mesg=check_match(df,dfw)
            return render_template('others.html', err_m='ERROR',
                                   error='This two files doesnt match, please check and try again.')

        if check_today(df, dfw) != True:
            return render_template('others.html', err_m='ERROR',
                                   error='The student file already contain data from attendance file')

        # mod_df, class_duration, today_date, pr_cnt, ab_cnt = backend.func(
        #     df, dfw)

        try:
            mod_df, class_duration, today_date, pr_cnt, ab_cnt = backend.main_fuc(
                df, dfw, filtr)
        except:
            return render_template('others.html', err_m='ERROR',
                                   error='Something went wrong, please check your files and try again')

        absents_list = get_absents(mod_df, today_date)
        ab_cnt = str(len(absents_list))

        # mod_df = mod_df[["REGD NO", "FullName", today_date, today_dur]].style.hide_index().set_properties(
        #     subset=[today_date, today_dur], **{'text-align': 'center'})

        # option=request.form.get('option')

        # return render_template('others.html',error=option)
        tday_date = today_date.replace('/', '')
        filename = year+'_'+branch+'_'+subject+'_'+tday_date+'.csv'
        return render_template('results.html',
                               shape='Completed successfully',
                               year_ht='year: '+year,
                               branch_ht='Branch: '+branch,
                               subject_ht='Subject: '+subject,
                               class_dur='class duration: '+class_duration+'mins',
                               today='Date: '+today_date,
                               present='Present: '+pr_cnt,
                               absent='Absent: '+ab_cnt,
                               list_absent=absents_list)

    return render_template('others.html')


@app.route("/results", methods=['GET', 'POST'])
def results():
    global mod_df, filename
    if request.method == 'POST':
        resp = make_response(mod_df.to_csv())
        resp.headers["Content-Disposition"] = "attachment; filename="+filename
        resp.headers["Content-Type"] = "text/csv"
        return resp

        # file_name = filename+'.xltx'
        # wb = load_workbook(mod_df)
        # wb.save(file_name, as_template=True)
        # return send_from_directory(file_name, as_attachment=True)


@app.route('/clear', methods=['GET', 'POST'])
def res():
    global opt
    if request.method == 'POST':
        if opt == 'vvit':
            return render_template('vvit.html')
        return render_template('others.html')


if __name__ == "__main__":
    app.run(debug=True)
