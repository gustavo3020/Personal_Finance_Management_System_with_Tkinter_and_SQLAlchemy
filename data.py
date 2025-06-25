from sqlalchemy import create_engine, Column, insert, text, MetaData, Table, \
    update, inspect
from pandas import read_sql, read_excel, ExcelWriter, to_datetime
from datetime import datetime
from dateutil.relativedelta import relativedelta

column_types = {'VARCHAR': 'string', 'BIGINT': 'int64',
                'DATE': 'datetime64[ns]', 'FLOAT': 'float64',
                'DATETIME': 'datetime64[ns]', 'TEXT': 'string'}


class DatabaseManager():
    def __init__(self, db_path):
        self.engine = create_engine(db_path)
        self.metadata = MetaData()
        self.metadata.bind = self.engine
        self.inspector = inspect(self.engine)
        self.table_names = self.inspector.get_table_names()

    def create_table_if_not_exists(self, table_name, columns):
        cols = []
        for column_name, column_type in columns.items():
            if column_name == 'Id':
                cols.append(Column(column_name, column_type, primary_key=True,
                                   autoincrement=True))
            else:
                cols.append(Column(column_name, column_type))
        Table(table_name, self.metadata, *cols)
        self.metadata.create_all(self.engine, checkfirst=True)

    def get_table_columns(self, table_name):
        columns = self.inspector.get_columns(table_name)
        columns_list = [column['name'] for column in columns]
        return columns_list

    def get_column_type_list(self, table_name):
        column_type_list = []
        columns = self.inspector.get_columns(table_name)
        for column in columns:
            if 'VARCHAR' in column:
                column_type_list.append('VARCHAR')
            elif 'INT' in column:
                column_type_list.append('BIGINT')
            else:
                column_type = str((column['type']))
                column_type_list.append(column_type)
        return column_type_list

    def create_row(self, **kwargs):
        table_name = kwargs.get('table_name', None)
        values = kwargs.get('values', None)
        table = self.metadata.tables[table_name]
        stmt = insert(table).values(values)
        self.execute_stmt(stmt)

    def update_row_values(self, **kwargs):
        table_name = kwargs.get('table_name', None)
        values = kwargs.get('values', None)
        table = self.metadata.tables[table_name]
        stmt = update(table).where(table.c.Id == values[0]).values(values)
        self.execute_stmt(stmt)

    def delete_row(self, **kwargs):
        table_name = kwargs.get('table_name', None)
        Id = kwargs.get('Id', None)
        table = self.metadata.tables[table_name]
        stmt = table.delete().where(table.c.Id == Id)
        self.execute_stmt(stmt)

    def execute_text_stmt(self, stmt):
        with self.engine.connect() as connection:
            result = connection.execute(text(stmt))
            connection.commit()
            return result

    def execute_stmt(self, stmt):
        with self.engine.connect() as connection:
            result = connection.execute(stmt)
            connection.commit()
            return result

    def get_last_row_id(self, table_name):
        stmt = f'SELECT Id FROM \"{table_name}\" ORDER BY Id DESC LIMIT 1'
        last_row_id = self.execute_text_stmt(stmt).scalar_one_or_none()
        return last_row_id if last_row_id is not None else 0

    def validate_entrys(self, table_name, entrys):
        new_entrys = []
        column_type_list = self.get_column_type_list(table_name)[2:]
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

    def write_df_to_sql(self, df, table_name, excel_columns):
        new_df = change_column_date_format(df)
        sql_column_type = self.get_column_type_list(table_name)
        for key, column in enumerate(sql_column_type):
            sql_column_type[key] = column_types[column]
        dtype_mapping = dict(zip(excel_columns, sql_column_type))
        new_df = df.astype(dtype_mapping)
        new_df.to_sql(table_name, con=self.engine, if_exists='replace',
                      index=False)

    def export_table(self, file_path, table_name):
        with ExcelWriter(file_path) as writer:
            df = read_sql(table_name, con=self.engine)
            df.to_excel(writer, sheet_name=table_name, index=False)


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


def change_column_date_format(df):
    try:
        df['Data'] = to_datetime(df['Data'], format='%d/%m/%Y',
                                 errors='coerce')
    except TypeError:
        df = df.astype('object')
        for date_row_id, date in enumerate(df['Data']):
            df.loc[date_row_id, 'Data'] = date.date()
    return df


# def export_to_excel(file_path):
#     table_names = get_table_names()
#     with ExcelWriter(file_path) as writer:
#         for table_name in table_names:
#             df = read_sql(table_name, con=engine)
#             df.to_excel(writer, sheet_name=table_name, index=False)


# def create_column(table_name, column, type):
#     stmt = f'ALTER TABLE {table_name} ADD COLUMN {column} {type}'
#     execute_text_stmt(stmt)


# def delete_column(table_name, column):
#     stmt = f'ALTER TABLE {table_name} DROP {column} ;'
#     execute_text_stmt(stmt)
