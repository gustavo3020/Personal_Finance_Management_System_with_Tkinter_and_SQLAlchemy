from sqlalchemy import create_engine, Column, insert, text, desc, MetaData, \
    Table, update, inspect
from sqlalchemy.orm import sessionmaker, declarative_base
from pandas import read_sql, read_excel, ExcelWriter, to_datetime
from datetime import datetime
from dateutil.relativedelta import relativedelta

column_types = {'VARCHAR': 'string', 'BIGINT': 'int64',
                'DATE': 'datetime64[ns]', 'FLOAT': 'float64',
                'DATETIME': 'datetime64[ns]', 'TEXT': 'string'}


def create_database(path):
    global engine, metadata, Session, session, Base
    engine = create_engine(path)
    metadata = MetaData()
    metadata.reflect(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    Base = declarative_base()
    Base.metadata.create_all(bind=engine)
    return engine


def create_table_if_not_exists(table_name, columns, engine):
    inspector = inspect(engine)
    if not inspector.has_table(table_name):
        Table(table_name, metadata, *[Column(name, column_type) for name,
                                      column_type in columns.items()])
        metadata.create_all(engine)


def get_column_type_list(table_name):
    column_type_list = []
    inspector = inspect(engine)
    columns = inspector.get_columns(table_name)
    for column in columns:
        column_type = str((column['type']))
        column_type_list.append(column_type)
    return column_type_list


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


def get_row_values(Id, table_name):
    df = read_sql(table_name, engine)
    row_values_list = df.loc[df['Id'] == int(Id)].values
    return (*row_values_list,)


def get_last_row_id(table_name):
    table = metadata.tables[table_name]
    try:
        last_row = session.query(table).order_by(desc(table.c.Id)).first()
        last_row_id = last_row[0]
    except TypeError:
        last_row_id = 0
    return last_row_id


def get_table_columns(table_name):
    inspector = inspect(engine)
    columns = inspector.get_columns(table_name)
    columns_list = [column['name'] for column in columns]
    return columns_list


def create_row(**kwargs):
    table_name = kwargs.get('table_name', None)
    values = kwargs.get('values', None)
    table = metadata.tables[table_name]
    stmt = insert(table).values(values)
    execute_stmt(stmt)


def update_row_values(**kwargs):
    table_name = kwargs.get('table_name', None)
    values = kwargs.get('values', None)
    table = metadata.tables[table_name]
    stmt = update(table).where(table.c.Id == values[0]).values(values)
    execute_stmt(stmt)


def delete_row(**kwargs):
    table_name = kwargs.get('table_name', None)
    Id = kwargs.get('Id', None)
    table = metadata.tables[table_name]
    stmt = table.delete().where(table.c.Id == Id)
    execute_stmt(stmt)


def create_column(table_name, column, type):
    stmt = f'ALTER TABLE {table_name} ADD COLUMN {column} {type}'
    execute_text_stmt(stmt)


def delete_column(table_name, column):
    stmt = f'ALTER TABLE {table_name} DROP {column} ;'
    execute_text_stmt(stmt)


def execute_text_stmt(stmt):
    with engine.connect() as connection:
        connection.execute(text(stmt))
        connection.commit()


def execute_stmt(stmt):
    with engine.connect() as connection:
        connection.execute(stmt)
        connection.commit()


def validate_entrys(table_name, entrys):
    new_entrys = []
    column_type_list = get_column_type_list(table_name)[2:]
    count = 0
    for column_type in column_type_list:
        if column_type == 'INTEGER':
            try:
                entry = int(entrys[count])
            except ValueError:
                entry = None
        elif column_type == 'FLOAT':
            try:
                entry = f'{float(entrys[count].replace(",", "."))}'
            except ValueError:
                entry = None
        elif entrys[count] == '':
            entry = None
        else:
            entry = entrys[count]
        new_entrys.append(entry)
        count += 1
    return new_entrys


def change_column_date_format(df):
    try:
        for date_row_id, date in enumerate(df['Data']):
            df.loc[date_row_id, 'Data'] = convert_string_to_date(date)
    except TypeError:
        df = df.astype('object')
        for date_row_id, date in enumerate(df['Data']):
            df.loc[date_row_id, 'Data'] = date.date()
    return df


def get_table_names():
    inspector = inspect(engine)
    table_names = inspector.get_table_names()
    return table_names


def export_to_excel(file_path):
    table_names = get_table_names()
    with ExcelWriter(file_path) as writer:
        for table_name in table_names:
            df = read_sql(table_name, con=engine)
            df.to_excel(writer, sheet_name=table_name, index=False)


def write_df_to_sql(df, table_name, excel_columns):
    new_df = change_column_date_format(df)
    print(new_df)
    sql_column_type = get_column_type_list(table_name)
    for key, column in enumerate(sql_column_type):
        sql_column_type[key] = column_types[column]
    dtype_mapping = dict(zip(excel_columns, sql_column_type))
    new_df = df.astype(dtype_mapping)
    new_df.to_sql(table_name, con=engine, if_exists='replace', index=False)


def export_table(file_path, table_name):
    with ExcelWriter(file_path) as writer:
        df = read_sql(table_name, con=engine)
        df.to_excel(writer, sheet_name=table_name, index=False)
