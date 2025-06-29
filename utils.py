from PIL import Image, ImageTk
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pandas import Period, period_range, to_datetime


def import_image(path):
    image = Image.open(path)
    resized_image = image.resize((30, 30))
    imagetk = ImageTk.PhotoImage(resized_image)
    return imagetk


def go_to_next_element(event):
    event.widget.tk_focusNext().focus()


def add_month_to_date(date, months_to_add):
    new_date = date + relativedelta(months=months_to_add)
    return new_date


def convert_string_to_date(date_string):
    date_object = datetime.strptime(date_string, '%d/%m/%Y').date()
    return date_object


def convert_date_to_string(date):
    date_object = datetime.strptime(str(date), '%Y-%m-%d')
    string_date = date_object.strftime('%d/%m/%Y')
    return string_date


def prepare_chart_data(df, group_column):
    chart_data = df.groupby(group_column)['Valor'].sum().reset_index()
    chart_data = chart_data[chart_data['Valor'] != 0]
    chart_data = chart_data.sort_values(by='Valor', ascending=False)
    return chart_data


def prepare_line_chart_data(df, start_date, end_date, **kwargs):
    MONTHS_THRESHOLD = kwargs.get('MONTHS_THRESHOLD', 12)
    new_df = df.copy()
    start_period_calc = Period(start_date, freq='M')
    end_period_calc = Period(end_date, freq='M')
    num_months = (end_period_calc - start_period_calc).n + 1
    if num_months > MONTHS_THRESHOLD:
        period_freq = 'Y'
        full_period = period_range(start=start_date.year, end=end_date.year,
                                   freq='Y')
    else:
        period_freq = 'M'
        full_period = period_range(start=start_date.strftime('%Y-%m'),
                                   end=end_date.strftime('%Y-%m'), freq='M')
    new_df['Periodo'] = new_df['Data'].dt.to_period(period_freq)
    line_chart_data = new_df.groupby('Periodo')['Valor'].sum()
    line_chart_data = line_chart_data.reindex(full_period,
                                              fill_value=0).reset_index()
    line_chart_data.rename(columns={'index': 'Periodo'}, inplace=True)
    line_chart_data = line_chart_data.sort_values(by='Periodo')
    return line_chart_data


def prepare_data(df, start_date, end_date):
    df = df.fillna('')
    df['Data'] = to_datetime(df['Data'], errors='coerce')
    df['Valor'] = df['Valor'].replace('', 0).astype(float)
    filtered_df = df[df['Data'].dt.date.between(start_date, end_date)]
    return filtered_df
