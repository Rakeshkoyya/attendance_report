import students
import pandas as pd
import re
from datetime import datetime


def check_today(df, dfw):

    dt = datetime.strptime(df.loc[0, 'Timestamp'], '%m/%d/%Y, %I:%M:%S %p')
    today = dt.strftime('%Y-%m-%d')
    if today in df.columns:
        return False
    return True


def check_match(df, dfw):
    # print(df)
    # print(dfw)
    people = []
    pattern = re.compile(r'\d\dBQ\d\w\d\d.\d')
    for i in df.index:
        name = df.loc[i, 'Full Name']
        matches = pattern.findall(name)
        if matches == []:
            continue
        people.append(matches[0])
    # print(people)
    # print(dfw['REGD NO'].unique())
    for x in people:
        if x not in dfw['REGD NO'].unique():
            return False

    return True


def get_absents(dfw_mod, today):
    absents = []
    # dfw_mod.set_index('REGD NO',inplace=True)    and not pd.isnull(dfw_mod.loc[i, 'REGD NO'])
    for i in dfw_mod.index:
        if dfw_mod.loc[i, today] == 'A' and not pd.isnull(dfw_mod.loc[i, 'REGD NO']):
            absents.append(dfw_mod.loc[i, 'REGD NO'])
    # dfw_mod.reset_index()
    return absents
    # lst=[x for x in range(48)]
    # res=[]
    # for i in range(5,len(absents),5):
    #     temp=absents[i-5:i]
    #     res.append(temp)

    # xtr=absents[i:]

    # return res,xtr


def check_df(df):
    if 'Full Name' not in df or 'User Action' not in df or 'Timestamp' not in df:
        return False
    return True


def check_dfw(dfw):
    # print(dfw)
    if 'REGD NO' not in dfw or 'FullName' not in dfw:
        return False
    return True


def main_fuc(df, dfw, filtr):

    #     dfw.set_index('FullName',inplace=True)

    maxd = mind = datetime.strptime(
        df.loc[0, 'Timestamp'], '%m/%d/%Y, %I:%M:%S %p')
    for i in df['Timestamp']:
        maxd = max(maxd, datetime.strptime(i, '%m/%d/%Y, %I:%M:%S %p'))
        mind = min(mind, datetime.strptime(i, '%m/%d/%Y, %I:%M:%S %p'))
    total_time = (maxd-mind)

    today = maxd.strftime('%Y-%m-%d')
    today_dur = '['+maxd.strftime('%d/%m')+']'+'duration in "mins"'

    dfw[today] = 'A'
    dfw[today_dur] = '0'
    dfw["person"] = 'student'

    import datetime as datetm

# calculating duration
    def cal_duration(periods):
        periods = sorted(periods, key=lambda x: x[1])
        t_time = datetm.timedelta(0)
        pres_time = periods[0][1]
        left = False
        for x in periods:
            if 'Joined' in x[0] and left:
                pres_time = x[1]
                left = False
            elif x[0] == 'Left':
                t_time += x[1]-pres_time
                pres_time = maxd
                left = True
        t_time += maxd-pres_time
        return t_time

    attendees_dict = {}
    for i in df.index:
        name = df.loc[i, 'Full Name']
        time = datetime.strptime(
            df.loc[i, 'Timestamp'], '%m/%d/%Y, %I:%M:%S %p')
        data_tup = (df.loc[i, 'User Action'], time)
        if name in attendees_dict:
            attendees_dict[name].append(data_tup)
        else:
            attendees_dict[name] = [data_tup]

# adding columns of attendance and duration

    import re
    pattern = re.compile(r'\d\dBQ\d\w\d\d.\d')

    for i in attendees_dict:
        t_time = cal_duration(attendees_dict[i])
        temp = ''

        if i in dfw['FullName']:
            temp = i
        for name in dfw['FullName']:
            if str(name).lower() in str(i).lower():
                temp = name
                break

        if temp == '':
            matches = pattern.findall(i)
            if matches != []:
                redg_no = matches[0]
                temp = dfw.loc[dfw[dfw['REGD NO'] ==
                                   redg_no].index, 'FullName'].iat[0]

        if temp == '':
            dfw = dfw.append({'FullName': i, today: '-1', today_dur: (
                t_time.seconds//60), "person": 'teacher/unknown'}, ignore_index=True)
            # print('appended',i)
            continue
        dfw.loc[dfw[dfw['FullName'] == temp].index, today] = 'P'
        dfw.loc[dfw[dfw['FullName'] == temp].index,
                today_dur] = (t_time.seconds//60)
        dfw.loc[dfw[dfw['FullName'] == temp].index, "person"] = 'Student'

        matches = pattern.findall(i)
        if matches == []:
            continue
        redg_no = matches[0]
        # duration=str(t_time.seconds//60)+'mins'
        # dfw.loc[i ,today_dur]=duration
        # dfw.loc[i,today]='Present'

    # filtreing accordily
    filtr_par = filtr*int(total_time.seconds//60)/100
    s = dfw[today_dur]
    dfw.loc[pd.to_numeric(s) < filtr_par, today] = 'A'

    for i in dfw.index:
        if pd.isnull(dfw.loc[i, 'REGD NO']):
            dfw.loc[i, today] = '-1'

    # adding resultant row

    k = dfw[today].value_counts()
    att_data = 'P:{0} A:{1}'.format(k['P'], k['A'])
    total_time_str = 'class dur:'+str(total_time.seconds//60)+'mins'

    if 'results' in dfw['REGD NO'].unique():
        dfw.loc[dfw[dfw['REGD NO'] == 'results'].index, [
            today, today_dur]] = [att_data, total_time_str]
    else:
        dfw = dfw.append({'REGD NO': 'results', today: att_data,
                          today_dur: total_time_str}, ignore_index=True)

# saving the result in new file
    # dfw.to_csv(result_file,index=False)
    # returns dfw, class_duration, today_date, present_count, absent_count

    return dfw, str(total_time.seconds//60), today, str(k['P']), str(k['A'])
