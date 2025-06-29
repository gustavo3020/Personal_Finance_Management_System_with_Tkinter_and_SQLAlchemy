from tkinter import ttk, filedialog, Tk, StringVar, Toplevel, messagebox
from tkcalendar import DateEntry
from utils import go_to_next_element, datetime, convert_date_to_string, \
    add_month_to_date, prepare_line_chart_data, prepare_chart_data, \
    prepare_data
from data import read_sql
from plotter import ChartPlotter
from pandas import read_excel


class Calendar(DateEntry):
    def __init__(self, frame, **kwargs):
        super().__init__(frame)
        self.get_kwargs(**kwargs)
        self.configure(background='darkgray', date_pattern='dd/mm/yyyy',
                       locale='pt_BR')
        self.grid(row=self.row, column=self.column)
        self.set_date(self.date_str)
        self.date_obj = self.get_date()
        self.bind('<<DateEntrySelected>>', lambda event: self.getdate())

    def get_kwargs(self, **kwargs):
        self.row = kwargs.get('row', 0)
        self.column = kwargs.get('column', 0)
        self.external_instance = kwargs.get('external_instance', None)
        self.date_str = kwargs.get('date_str', None)

    def getdate(self):
        self.date_obj = self.get_date()
        if self.external_instance:
            self.external_instance.on_param_changed()


class DashboardManager():
    def __init__(self, **kwargs):
        self.get_kwargs(**kwargs)
        self.create_calendars()
        self.create_summary_display()
        self.create_chart_display()
        self.on_param_changed()

    def get_kwargs(self, **kwargs):
        self.master = kwargs.get('master', None)
        self.upper_frame = kwargs.get('upper_frame', None)
        self.lower_frame = kwargs.get('lower_frame', None)
        self.columns = kwargs.get('columns', None)
        self.columns_to_group = kwargs.get('columns_to_group', None)

    def create_calendars(self):
        create_label(self.upper_frame, text='Data Inicial', geometry='grid',
                     row=0)
        self.calendar1 = Calendar(self.upper_frame, date_str='01/01/2020',
                                  row=0, column=1, external_instance=self)
        create_label(self.upper_frame, text='Data Final', geometry='grid',
                     row=1)
        self.calendar2 = Calendar(self.upper_frame, date_str='31/12/2030',
                                  row=1, column=1, external_instance=self)

    def create_summary_display(self):
        frame = create_frame(self.lower_frame)
        options = list(self.master.entry_trees.keys())
        self.selected_option = StringVar(value=options[0])
        self.options = self.create_combobox('Tabelas', frame, options,
                                            self.selected_option)
        self.tree = SummaryTreeview(frame=frame, columns=self.columns,
                                    master=self.master)

    def create_chart_display(self):
        frame = ttk.Frame(self.lower_frame)
        frame.pack(side='right', fill='both', expand=True, padx=10, pady=10)
        chart_options = ['Pizza', 'Barras', 'Linhas']
        self.selected_chart_type = StringVar(value=chart_options[0])
        self.chart_menu = self.create_combobox('Tipo de gráfico', frame,
                                               chart_options,
                                               self.selected_chart_type)
        self.chart_plotter = ChartPlotter(frame)

    def create_combobox(self, text, frame, options, selected_option):
        create_label(frame, text=text)
        combobox = ttk.Combobox(frame, values=options, state='readonly',
                                textvariable=selected_option)
        combobox.bind("<<ComboboxSelected>>", self.on_param_changed)
        combobox.pack(pady=5)
        return combobox

    def on_param_changed(self, event=None):
        selected_table_name = self.selected_option.get()
        start_date = self.calendar1.date_obj
        end_date = self.calendar2.date_obj
        self.tree.update(selected_table_name, start_date, end_date,
                         self.columns_to_group)
        self.update_chart(selected_table_name, start_date, end_date,
                          self.columns_to_group,
                          self.selected_chart_type.get())

    def update_chart(self, table_name, start_date, end_date, group_by_columns,
                     chart_type):
        df = read_sql(table_name, self.master.dbmanager.engine)
        filtered_df = prepare_data(df, start_date, end_date)
        if filtered_df.empty:
            self.chart_plotter.show_message(
                "Nenhum dado para exibir no gráfico para a seleção atual.")
            return
        if chart_type == "Linhas":
            line_chart_data = prepare_line_chart_data(filtered_df, start_date,
                                                      end_date)
            labels = line_chart_data['Periodo'].astype(str).tolist()
            values = line_chart_data['Valor'].tolist()
            title = 'Tendência de Valores ao Longo do Tempo'
            self.chart_plotter.plot_line_chart(labels, values, title)
        else:
            group_column = group_by_columns[0]
            chart_data = prepare_chart_data(filtered_df, group_column)
            labels = chart_data[group_column].tolist()
            values = chart_data['Valor'].tolist()
            title = f'Distribuição por {group_column}'
        if chart_type == "Pizza":
            self.chart_plotter.plot_pie_chart(labels, values, title)
        elif chart_type == "Barras":
            self.chart_plotter.plot_bar_chart(labels, values, title)


class SummaryTreeview(ttk.Treeview):
    def __init__(self, frame, **kwargs):
        super().__init__(frame)
        self.get_kwargs(**kwargs)
        self.configure_tree(frame)
        self.configure_columns()

    def get_kwargs(self, **kwargs):
        self.master = kwargs.get('master', None)
        self.columns = kwargs.get('columns', None)
        self.height = kwargs.get('height', 30)

    def configure_tree(self, frame):
        self.y_scroll = self.create_y_scroll(frame)
        self.x_scroll = self.create_x_scroll(frame)
        self.configure(yscrollcommand=self.y_scroll.set, columns=self.columns,
                       xscrollcommand=self.x_scroll.set, height=self.height)
        self.pack(side='left',  fill='both', expand=True)

    def configure_columns(self):
        for column in self.columns:
            self.heading(column, text=column, anchor='w')
        self.column('#0', width=30, stretch='no')
        self.column('#1', width=180, stretch='no')
        self.column('#2', width=120, stretch='no')

    def create_y_scroll(self, frame):
        treescroll = ttk.Scrollbar(frame, orient='vertical')
        treescroll.config(command=self.yview)
        treescroll.pack(side='right', fill='y')
        return treescroll

    def create_x_scroll(self, frame):
        treescroll = ttk.Scrollbar(frame, orient='horizontal')
        treescroll.config(command=self.xview)
        treescroll.pack(side='bottom', fill='x')
        return treescroll

    def update(self, table_name, start_date, end_date, group_by_columns):
        self.delete(*self.get_children())
        if not group_by_columns:
            return
        df = read_sql(table_name, self.master.dbmanager.engine)
        filtered_df = prepare_data(df, start_date, end_date)
        grouped_data = filtered_df.groupby(group_by_columns)['Valor'].sum(
            ).reset_index()
        self.insert_into_treeview(grouped_data, group_by_columns)

    def insert_into_treeview(self, data_frame, columns_to_group,
                             parent_item=''):
        if not columns_to_group:
            return
        current_column = columns_to_group[0]
        remaining_columns = columns_to_group[1:]
        if parent_item == '':
            unique_values = data_frame[current_column].unique()
        else:
            unique_values = data_frame[current_column].unique()

        for value in sorted(unique_values):
            subset_df = data_frame[data_frame[current_column] == value]
            total_for_value = subset_df['Valor'].sum()
            item_id = self.insert(parent_item, 'end', values=(
                value, f'{total_for_value:.2f}'))
            if remaining_columns:
                self.insert_into_treeview(subset_df,
                                          remaining_columns, item_id)


class Window(Toplevel):
    def __init__(self, **kwargs):
        super().__init__()
        self.entry_box_list = []
        self.get_kwargs(**kwargs)
        self.config_window(self.title_name)
        self.create_instances()
        row = self.create_entry_boxes(self.tab1)
        create_button(frame=self.tab1, text=self.button, command=lambda:
                      self.command(self.calendar.date_obj),
                      width=45, geometry='grid', row=row)
        row += 1
        create_button(frame=self.tab1, text='Limpa', command=self.clear_entrys,
                      width=45, geometry='grid', row=row)
        self.create_tab2_widgets()

    def get_kwargs(self, **kwargs):
        self.master = kwargs.get('master', None)
        self.date = kwargs.get('date', datetime.today())
        self.title_name = kwargs.get('title', None)
        self.button = kwargs.get('button', None)
        self.command = kwargs.get('command', None)

    def create_entry_boxes(self, tab):
        self.entry_box_list.clear()
        table_name = self.master.selected_tab
        columns = self.master.dbmanager.get_table_columns(table_name)
        row = 0
        for entry_box_id in range(len(columns)-1):
            create_label(tab, text=columns[entry_box_id+1], row=row,
                         geometry='grid')
            if entry_box_id == 0:
                pass
            else:
                entry_box = ttk.Entry(tab, width=30)
                entry_box.bind('<Return>', go_to_next_element)
                entry_box.grid(row=row, column=1)
                self.entry_box_list.append(entry_box)
            row += 1
        return row

    def create_tab2_widgets(self):
        create_label(self.tab2, text='Parcelas', row=0, geometry='grid')
        entry_box = ttk.Entry(self.tab2, width=30)
        entry_box.grid(row=0, column=1)
        self.entry_box_list.append(entry_box)

    def create_instances(self):
        self.notebook = Notebook(self)
        self.tab1 = create_tab(notebook=self.notebook, tab_name='Entradas')
        self.tab2 = create_tab(notebook=self.notebook, tab_name='Avançado')
        self.calendar = Calendar(self.tab1, date_str=self.date, row=0,
                                 column=1)

    def config_window(self, title):
        self.title(title)
        self.geometry('400x400')
        self.attributes('-topmost', True)
        self.focus_force()
        self.grab_set()
        self.bind('<Escape>', self.on_escape)

    def clear_entrys(self):
        for e in self.entry_box_list:
            e.delete(0, 'end')

    def get_entry_box_values(self):
        self.entrys = []
        for entry_box in self.entry_box_list:
            self.entrys.append(entry_box.get())
        return self.entrys

    def on_escape(self, event):
        self.destroy()


class Notebook(ttk.Notebook):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.pack(padx=10, pady=10, ipadx=200, ipady=100)

    def get_selected_tab(self):
        selected_tab_id = self.select()
        self.master.selected_tab = self.tab(selected_tab_id, 'text')


class EntryTreeview(ttk.Treeview):
    def __init__(self, frame, **kwargs):
        super().__init__(frame)
        self.get_kwargs(**kwargs)
        self.columns = self.master.dbmanager.get_table_columns(self.table_name)
        self.configure_tree(frame)
        self.configure_columns()
        self.master.entry_trees.update({self.table_name: self})
        self.master.update(self.table_name)

    def get_kwargs(self, **kwargs):
        self.master = kwargs.get('master', None)
        self.table_name = kwargs.get('table_name', None)
        self.height = kwargs.get('height', 30)

    def configure_tree(self, frame):
        self.y_scroll = self.create_y_scroll(frame)
        self.x_scroll = self.create_x_scroll(frame)
        self.config(yscrollcommand=self.y_scroll.set, height=self.height,
                    xscrollcommand=self.x_scroll.set, columns=self.columns)
        self.pack(side='left',  fill='both', expand=True)

    def configure_columns(self):
        for column in self.columns:
            self.heading(column, text=column, anchor='w')
        self.column('#0', width=0, stretch='no')
        self.column('#1', width=30, stretch='no')
        for n in range(2, len(self.columns)):
            self.column(f'#{n}', width=150, stretch='no')

    def create_y_scroll(self, frame):
        treescroll = ttk.Scrollbar(frame, orient='vertical')
        treescroll.config(command=self.yview)
        treescroll.pack(side='right', fill='y')
        return treescroll

    def create_x_scroll(self, frame):
        treescroll = ttk.Scrollbar(frame, orient='horizontal')
        treescroll.config(command=self.xview)
        treescroll.pack(side='bottom', fill='x')
        return treescroll


class MainApp(Tk):
    def __init__(self, title, dbmanager):
        super().__init__()
        self.dbmanager = dbmanager
        self.config_window(title)
        self.entry_trees = {}
        self.selected_tab = ''
        self.style()

    def config_window(self, title):
        self.title(title)
        self.state('zoomed')
        self.bind('<Delete>', self.delete_row)
        self.bind('<Double-Button-1>', lambda event: self.edit_row())

    def style(self):
        style = ttk.Style()
        style.theme_use('vista')

    def get_images(self, **kwargs):
        self.img_new = kwargs.get('img_new', None)
        self.img_edit = kwargs.get('img_edit', None)
        self.img_delete = kwargs.get('img_delete', None)
        self.img_import = kwargs.get('img_import', None)
        self.img_export = kwargs.get('img_export', None)

    def create_common_buttons(self, frame):
        create_button(frame=frame, text='Nova entrada', command=self.new_entry,
                      image=self.img_new)
        create_button(frame=frame, text='Editar', command=self.edit_row,
                      image=self.img_edit)
        create_button(frame=frame, text='Excluir', command=lambda:
                      self.delete_row(), image=self.img_delete)
        create_button(frame=frame, text='Importar', command=self.import_table,
                      image=self.img_import)
        create_button(frame=frame, text='Exportar', command=self.export_table,
                      image=self.img_export)

    def new_entry(self):
        self.window = Window(master=self, title='Nova entrada',
                             button='Confirmar', command=self.new_row)

    def new_row(self, date_obj):
        tree_name = self.selected_tab
        entrys = self.window.get_entry_box_values()
        try:
            times = int(entrys[-1])
        except ValueError:
            times = entrys[-1] = 1
        Id = self.dbmanager.get_last_row_id(tree_name) + 1
        new_entrys = [Id]
        new_entrys.append(date_obj)
        validated_entry = self.dbmanager.validate_entrys(tree_name, entrys)
        new_entrys += validated_entry
        for n in range(0, times):
            new_entrys[3] = f'{n + 1} de {times}'
            self.dbmanager.create_row(table_name=tree_name, values=new_entrys)
            new_entrys[0] += 1
            new_entrys[1] = add_month_to_date(new_entrys[1], 1)
        self.update(tree_name)

    def edit_row(self):
        tree_name = self.selected_tab
        tree_object = self.entry_trees[tree_name]
        row_values = tree_object.item(tree_object.focus(), 'values')
        Id = row_values[0]
        date = row_values[1]
        self.window = Window(master=self, title=f'Editar entrada {Id}',
                             button='Salvar', command=self.save_row, date=date)
        for entry_box_id, text in enumerate(row_values[2:]):
            self.window.entry_box_list[entry_box_id].insert(0, text)

    def save_row(self, date_obj):
        tree_name = self.selected_tab
        tree_object = self.entry_trees[tree_name]
        row_values = tree_object.item(tree_object.focus(), 'values')
        Id = row_values[0]
        new_entrys = [Id]
        new_entrys.append(date_obj)
        entrys = self.window.get_entry_box_values()
        validated_entry = self.dbmanager.validate_entrys(tree_name, entrys)
        new_entrys += validated_entry
        self.dbmanager.update_row_values(table_name=tree_name,
                                         values=new_entrys)
        self.update(tree_name)

    def delete_row(self, *args):
        tree_name = self.selected_tab
        tree_object = self.entry_trees[tree_name]
        selected_rows_id_tuple = tree_object.selection()
        for tree_row_id in selected_rows_id_tuple:
            database_id = tree_object.item(tree_row_id, 'values')[0]
            self.dbmanager.delete_row(Id=database_id, table_name=tree_name)
        self.update(tree_name)

    def update(self, tree_name):
        df = read_sql(tree_name, self.dbmanager.engine)
        df = df.fillna('')
        for row_id, date_obj in enumerate(df['Data']):
            df = df.astype('object')
            date_string = convert_date_to_string(date_obj.date())
            df.loc[row_id, 'Data'] = date_string
        tree_object = self.entry_trees[tree_name]
        row_to_focus = tree_object.focus()
        tree_object.delete(*tree_object.get_children())
        row_values_list = df.to_numpy().tolist()
        count = 0
        for row_values in row_values_list:
            tree_object.insert('', 'end', iid=count, values=row_values)
            count += 1
        try:
            tree_object.focus(row_to_focus)
            tree_object.selection_set(row_to_focus)
        except Exception:
            pass

    def export_table(self):
        path = filedialog.asksaveasfilename(
            defaultextension='.xlsx', filetypes=[('Excel files', '*.xlsx'),
                                                 ('All files', '*.*')],)
        self.dbmanager.export_table(path, self.selected_tab)

    def import_table(self):
        file_path = filedialog.askopenfilename()
        table_name = self.selected_tab
        df = read_excel(file_path, sheet_name=table_name)
        excel_columns = df.columns.tolist()
        sql_columns = self.dbmanager.get_table_columns(table_name)
        if excel_columns == sql_columns:
            self.dbmanager.write_df_to_sql(df, table_name, excel_columns)
        else:
            count = 0
            difference = {}
            if len(sql_columns) > len(excel_columns):
                show_msg_box(f'Faltam colunas na tabela {table_name}')
            elif len(sql_columns) < len(excel_columns):
                show_msg_box(f'Tabela {table_name} possui colunas a mais')
            else:
                for n in range(len(sql_columns)):
                    if excel_columns[n] != sql_columns[n]:
                        difference.update({excel_columns[n]: sql_columns[n]})
                    count += 1
                show_msg_box(f'Diferença nas colunas: {difference}')
        self.update(table_name)


def create_tab(**kwargs):
    notebook = kwargs.get('notebook', None)
    tab_name = kwargs.get('tab_name', None)
    new_tab = ttk.Frame(notebook, width=200, height=100)
    notebook.add(new_tab, text=tab_name)
    return new_tab


def create_frame(parent_frame, **kwargs):
    anchor = kwargs.get('anchor', 'w')
    side = kwargs.get('side', 'left')
    frame = ttk.Frame(parent_frame)
    frame.pack(side=side, anchor=anchor)
    return frame


def create_button(**kwargs):
    frame = kwargs.get('frame', None)
    text = kwargs.get('text', None)
    com = kwargs.get('command', None)
    img = kwargs.get('image', None)
    geometry = kwargs.get('geometry', 'pack')
    row = kwargs.get('row', 0)
    column = kwargs.get('column', 0)
    width = kwargs.get('width', 10)
    button = ttk.Button(frame, text=text, width=width, command=com, image=img)
    if geometry == 'pack':
        button.pack(side='left', anchor='nw', padx=2, pady=2)
    if geometry == 'grid':
        button.grid(row=row, column=column, columnspan=2, padx=10, pady=10)


def create_label(frame, **kwargs):
    text = kwargs.get('text', 'Label')
    row = kwargs.get('row', 0)
    column = kwargs.get('column', 0)
    geometry = kwargs.get('geometry', 'pack')
    label = ttk.Label(frame, text=text)
    if geometry == 'pack':
        label.pack()
    if geometry == 'grid':
        label.grid(row=row, column=column)


def show_msg_box(message):
    messagebox.showwarning(title='Warning', message=message)
