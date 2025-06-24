from tkinter import ttk, filedialog, Frame, Label, Tk, StringVar, OptionMenu, \
    Toplevel, Entry, messagebox
from tkcalendar import DateEntry
from PIL import Image, ImageTk
import data

entry_box_list = []
trees = {}
selected_tab = ['']


class Calendar():
    def __init__(self, frame, date_str, **kwargs):
        self.row = kwargs.get('row', 0)
        self.column = kwargs.get('column', 0)
        self.external_instance = kwargs.get('external_instance', None)
        self.date_str = kwargs.get('date_str', data.datetime.today())
        self.calendar = DateEntry(frame, background='darkgray',
                                  date_pattern='dd/mm/yyyy', locale='pt_BR')
        self.calendar.grid(row=self.row, column=self.column)
        self.calendar.set_date(date_str)
        self.date_obj = self.calendar.get_date()
        self.calendar.bind('<<DateEntrySelected>>', lambda event:
                           self.getdate())

    def getdate(self):
        self.date_obj = self.calendar.get_date()
        if self.external_instance:
            self.external_instance.on_calendar_date_changed()


class Options():
    def __init__(self, **kwargs):
        upper_frame = kwargs.get('upper_frame', None)
        lower_frame = kwargs.get('lower_frame', None)
        columns = kwargs.get('columns', None)
        options = list(trees.keys())
        self.selected_option = StringVar(value=options[0])
        self.options = OptionMenu(lower_frame, self.selected_option, *options,
                                  command=self.on_menu_selected)
        self.options.pack()
        self.tree = Treeview(lower_frame, columns)

        create_label(upper_frame, text='Data Inicial', background='#f1f1f1',
                     geometry='grid', row=0)
        self.calendar1 = Calendar(upper_frame, '01/01/2020', row=0, column=1,
                                  external_instance=self)

        create_label(upper_frame, text='Data Final', background='#f1f1f1',
                     geometry='grid', row=1)
        self.calendar2 = Calendar(upper_frame, '31/12/2030', row=1, column=1,
                                  external_instance=self)

        self.on_menu_selected(selection=options[0])

    def on_calendar_date_changed(self):
        self.on_menu_selected(self.selected_option.get())

    def on_menu_selected(self, selection):
        start_date = self.calendar1.date_obj
        end_date = self.calendar2.date_obj
        self.tree.update(selection, start_date, end_date)


class Treeview():
    def __init__(self, frame, columns):
        self.tree = ttk.Treeview(frame, height=30, columns=columns)
        self.y_scroll = self.create_y_scroll(frame)
        self.x_scroll = self.create_x_scroll(frame)
        self.tree.config(yscrollcommand=self.y_scroll.set,
                         xscrollcommand=self.x_scroll.set)
        self.tree_heading(columns)
        self.tree.pack(side='left',  fill='both', expand=True)
        self.configure_columns()

    def tree_heading(self, columns):
        for column in columns:
            self.tree.heading(column, text=column, anchor='w')

    def configure_columns(self):
        self.tree.column('#0', width=50, stretch='no')
        self.tree.column('#1', width=180, stretch='no')
        self.tree.column('#2', width=120, stretch='no')

    def create_y_scroll(self, frame):
        self.treescroll = ttk.Scrollbar(frame, orient='vertical')
        self.treescroll.config(command=self.tree.yview)
        self.treescroll.pack(side='right', fill='y')
        return self.treescroll

    def create_x_scroll(self, frame):
        self.treescroll = ttk.Scrollbar(frame, orient='horizontal')
        self.treescroll.config(command=self.tree.xview)
        self.treescroll.pack(side='bottom', fill='x')
        return self.treescroll

    def update(self, table_name, start_date, end_date):
        column = 'Categoria'
        column2 = 'Subcategoria'
        tree_object = self.tree
        tree_object.delete(*tree_object.get_children())
        df = data.read_sql(table_name, data.engine)
        df = df.fillna('')
        df['Valor'] = df['Valor'].replace('', 0)
        unique_values = df[column].unique()
        unique_values.sort()
        for value in unique_values:
            df1 = df[(df[column] == value) &
                     (df['Data'].dt.date >= start_date) &
                     (df['Data'].dt.date <= end_date)]
            unique_values2 = df1[column2].unique()
            unique_values2.sort()
            parent = tree_object.insert('', 'end',
                                        values=(value,
                                                f'{df1["Valor"].sum():.2f}'))
            for val in unique_values2:
                df2 = df1[(df1[column2] == val) &
                          (df1['Data'].dt.date >= start_date) &
                          (df1['Data'].dt.date <= end_date)]
                tree_object.insert(parent, 'end',
                                   values=(val, f'{df2["Valor"].sum():.2f}'))


class Window(Toplevel):
    def __init__(self, master, title, text, command, **kwargs):
        super().__init__(master)
        date = kwargs.get('date', data.datetime.today())
        self.title(title)
        self.geometry('400x400')
        self.attributes('-topmost', True)
        self.focus_force()
        self.grab_set()
        entry_box_list.clear()
        notebook = Notebook(self)
        tab1 = create_tab(notebook=notebook, tab_name='Entradas')
        tab2 = create_tab(notebook=notebook, tab_name='Avançado')
        self.calendar = Calendar(tab1, date, row=0, column=1)
        self.bind('<Escape>', self.teste)
        row = create_entry_boxes(tab1)
        create_label(tab2, text='Parcelas', row=row, background='#f1f1f1',
                     geometry='grid')
        entry_box = Entry(tab2, width=30)
        entry_box.bind('<Return>', go_to_next_element)
        entry_box.grid(row=row, column=1)
        entry_box_list.append(entry_box)
        row += 1
        command_button = ttk.Button(tab1, text=text, command=lambda:
                                    command(self.calendar.date_obj), width=45)
        command_button.grid(row=row, column=0, columnspan=2, padx=10, pady=10)
        row += 1
        clear_button = ttk.Button(tab1, text='Limpar', command=clear_entrys,
                                  width=45)
        clear_button.grid(row=row, column=0, columnspan=2, padx=10, pady=10)

    def teste(self, event):
        self.destroy()


class Notebook(ttk.Notebook):
    def __init__(self, master):
        super().__init__(master)
        self.pack(padx=10, pady=10, ipadx=200, ipady=100)

    def get_selected_tab(self):
        selected_tab_id = self.select()
        self.selected_tab = self.tab(selected_tab_id, 'text')
        selected_tab[0] = self.selected_tab


class EntryTreeview():
    def __init__(self, frame, table_name):
        self.style()
        self.table_name = table_name
        self.columns = data.get_table_columns(table_name)
        self.tree = ttk.Treeview(frame, height=30, columns=self.columns)
        self.configure_tree(frame)
        self.configure_columns()
        trees.update({table_name: self.tree})
        update_entry_tree(table_name)

    def style(self):
        style = ttk.Style()
        style.theme_use('default')
        style.configure('Treeview', background='#f1f1f1',
                        fieldbackground='#f1f1f1')

    def configure_tree(self, frame):
        self.y_scroll = self.create_y_scroll(frame)
        self.x_scroll = self.create_x_scroll(frame)
        self.tree.config(yscrollcommand=self.y_scroll.set,
                         xscrollcommand=self.x_scroll.set)
        self.tree_heading(self.columns)
        self.tree.pack(side='left',  fill='both', expand=True)

    def configure_columns(self):
        self.tree.column('#0', width=0, stretch='no')
        self.tree.column('#1', width=30, stretch='no')
        self.tree.column('#2', width=70, stretch='no')
        self.tree.column('#3', width=70, stretch='no')
        self.tree.column('#4', width=70, stretch='no')

    def create_y_scroll(self, frame):
        self.treescroll = ttk.Scrollbar(frame, orient='vertical')
        self.treescroll.config(command=self.tree.yview)
        self.treescroll.pack(side='right', fill='y')
        return self.treescroll

    def create_x_scroll(self, frame):
        self.treescroll = ttk.Scrollbar(frame, orient='horizontal')
        self.treescroll.config(command=self.tree.xview)
        self.treescroll.pack(side='bottom', fill='x')
        return self.treescroll

    def tree_heading(self, columns):
        for column in columns:
            self.tree.heading(column, text=column, anchor='w')


def create_common_buttons(**kwargs):
    frame = kwargs.get('frame', None)
    master = kwargs.get('master', None)
    image_new = kwargs.get('image_new', None)
    image_edit = kwargs.get('image_edit', None)
    image_delete = kwargs.get('image_delete', None)
    image_import = kwargs.get('image_import', None)
    image_export = kwargs.get('image_export', None)
    create_button(frame=frame, text='Nova entrada', command=lambda:
                  new_entry(master), image=image_new)
    create_button(frame=frame, text='Editar', command=lambda:
                  edit_row(master=master), image=image_edit)
    create_button(frame=frame, text='Excluir', command=lambda: delete_row(0),
                  image=image_delete)
    create_button(frame=frame, text='Importar', command=import_table,
                  image=image_import)
    create_button(frame=frame, text='Exportar', command=export_table,
                  image=image_export)


def create_main_window(title):
    main_window = Tk()
    main_window.title(title)
    main_window.state('zoomed')
    main_window.bind('<Delete>', delete_row)
    main_window.bind('<Double-Button-1>', edit_row)
    return main_window


def create_tab(**kwargs):
    notebook = kwargs.get('notebook', None)
    tab_name = kwargs.get('tab_name', None)
    new_tab = Frame(notebook, width=200, height=100)
    new_tab.configure(background='#f1f1f1')
    notebook.add(new_tab, text=tab_name)
    return new_tab


def create_frame(parent_frame, **kwargs):
    anchor = kwargs.get('anchor', 'w')
    side = kwargs.get('side', 'left')
    frame = Frame(parent_frame, highlightthickness=1)
    frame.configure(background='#f1f1f1')
    frame.pack(side=side, anchor=anchor)
    return frame


def create_button(**kwargs):
    frame = kwargs.get('frame', None)
    text = kwargs.get('text', None)
    com = kwargs.get('command', None)
    image = kwargs.get('image', None)
    button = ttk.Button(frame, text=text, width=10, command=com, image=image)
    button.pack(side='left', anchor='nw', padx=2, pady=2)


def create_label(frame, **kwargs):
    text = kwargs.get('text', 'Label')
    row = kwargs.get('row', 0)
    column = kwargs.get('column', 0)
    geometry = kwargs.get('geometry', 'pack')
    background = kwargs.get('background', 'white')
    label = Label(frame, text=text)
    label.configure(background=background)
    if geometry == 'pack':
        label.pack()
    if geometry == 'grid':
        label.grid(row=row, column=column)


def create_entry_boxes(window):
    table_name = selected_tab[0]
    columns = data.get_table_columns(table_name)
    row = 0
    for entry_box_id in range(len(columns)-1):
        create_label(window, text=columns[entry_box_id+1], row=row,
                     background='#f1f1f1', geometry='grid')
        if entry_box_id == 0:
            pass
        else:
            entry_box = Entry(window, width=30)
            entry_box.bind('<Return>', go_to_next_element)
            entry_box.grid(row=row, column=1)
            if len(entry_box_list) < (len(columns)-1):
                entry_box_list.append(entry_box)
        row += 1
    return row


def clear_entrys():
    for e in entry_box_list:
        e.delete(0, 'end')


def go_to_next_element(event):
    event.widget.tk_focusNext().focus()


def show_msg_box(message):
    messagebox.showwarning(title='Warning', message=message)


def update_entry_tree(tree_name):
    df = data.read_sql(tree_name, data.engine)
    df = df.fillna('')
    for row_id, date_obj in enumerate(df['Data']):
        df = df.astype('object')
        date_string = data.convert_date_to_string(date_obj.date())
        df.loc[row_id, 'Data'] = date_string
    tree_object = trees[tree_name]
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


def new_entry(master):
    Window(master, 'Nova entrada', 'Confirmar', new_row)


def new_row(date_obj):
    tree_name = selected_tab[0]
    entrys = get_entry_box_values()
    try:
        times = int(entrys[-1])
    except ValueError:
        times = entrys[-1] = 1
    Id = data.get_last_row_id(tree_name) + 1
    new_entrys = [Id]
    new_entrys.append(date_obj)
    validated_entry = data.validate_entrys(tree_name, entrys)
    new_entrys += validated_entry
    for n in range(0, times):
        new_entrys[3] = f'{n + 1} de {times}'
        data.create_row(table_name=tree_name, values=new_entrys)
        new_entrys[0] += 1
        new_entrys[1] = data.add_month_to_date(new_entrys[1], 1)
    update_entry_tree(tree_name)


def edit_row(*args, **kwargs):
    master = kwargs.get('master', None)
    tree_name = selected_tab[0]
    tree_object = trees[tree_name]
    row_values = tree_object.item(tree_object.focus(), 'values')
    Id = row_values[0]
    date = row_values[1]
    Window(master, f'Editar entrada {Id}', 'Salvar', save_row, date=date)
    for entry_box_id, text in enumerate(row_values[2:]):
        entry_box_list[entry_box_id].insert(0, text)


def save_row(date_obj):
    tree_name = selected_tab[0]
    tree_object = trees[tree_name]
    row_values = tree_object.item(tree_object.focus(), 'values')
    Id = row_values[0]
    new_entrys = [Id]
    new_entrys.append(date_obj)
    entrys = get_entry_box_values()
    validated_entry = data.validate_entrys(tree_name, entrys)
    new_entrys += validated_entry
    data.update_row_values(table_name=tree_name, values=new_entrys)
    update_entry_tree(tree_name)


def get_entry_box_values():
    entrys = []
    for entry_box in entry_box_list:
        entrys.append(entry_box.get())
    return entrys


def delete_row(*args):
    tree_name = selected_tab[0]
    tree_object = trees[tree_name]
    selected_rows_id_tuple = tree_object.selection()
    for tree_row_id in selected_rows_id_tuple:
        database_id = tree_object.item(tree_row_id, 'values')[0]
        data.delete_row(Id=database_id, table_name=tree_name)
    update_entry_tree(tree_name)


def import_image(path):
    image = Image.open(path)
    resized_image = image.resize((30, 30))
    imagetk = ImageTk.PhotoImage(resized_image)
    return imagetk


def export_to_excel():
    path = filedialog.asksaveasfilename(defaultextension='.xlsx',
                                        filetypes=[('Excel files', '*.xlsx'),
                                                   ('All files', '*.*')],)
    data.export_to_excel(path)


def export_table():
    path = filedialog.asksaveasfilename(defaultextension='.xlsx',
                                        filetypes=[('Excel files', '*.xlsx'),
                                                   ('All files', '*.*')],)
    data.export_table(path, *selected_tab)


def import_table():
    file_path = filedialog.askopenfilename()
    table_name = selected_tab[0]
    df = data.read_excel(file_path, sheet_name=table_name)
    excel_columns = df.columns.tolist()
    sql_columns = data.get_table_columns(table_name)
    if excel_columns == sql_columns:
        data.write_df_to_sql(df, table_name, excel_columns)
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
    update_entry_tree(table_name)
