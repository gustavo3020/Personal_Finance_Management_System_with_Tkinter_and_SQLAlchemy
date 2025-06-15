from tkinter import ttk, filedialog, Frame, Label, Tk, StringVar, OptionMenu, \
    Toplevel, Entry, messagebox
from tkcalendar import DateEntry
from PIL import Image, ImageTk
import data

entry_box_list = []
trees = {}
selected_tab = ['']
date_list = ['01/01/2020', '31/12/2030', '']


class Calendar():
    def __init__(self, frame, date, **kwargs):
        self.number = kwargs.get('number', 0)
        self.row = kwargs.get('row', 0)
        self.column = kwargs.get('column', 0)
        self.calendar = DateEntry(frame, background='darkgray',
                                  date_pattern='dd/mm/yyyy')
        self.calendar.grid(row=self.row, column=self.column)
        self.calendar.bind('<<DateEntrySelected>>', lambda event:
                           self.getdate(self.number-1))
        self.setdate(date)
        self.getdate(self.number-1)

    def getdate(self, n):
        self.date = self.calendar.get()
        date_list[n] = self.date
        update_abstract_tree()

    def setdate(self, date):
        self.calendar.set_date(date)


def create_main_window(title):
    main_window = Tk()
    main_window.title(title)
    main_window.state('zoomed')
    main_window.bind('<Delete>', delete_row)
    main_window.bind('<Double-Button-1>', edit_row)
    return main_window


def create_notebook(frame):
    notebook = ttk.Notebook(frame)
    notebook.pack(padx=10, pady=10, ipadx=200, ipady=100)
    return notebook


def create_tab(**kwargs):
    notebook = kwargs.get('notebook', None)
    tab_name = kwargs.get('tab_name', None)
    new_tab = Frame(notebook, width=200, height=100)
    new_tab.configure(background='#f1f1f1')
    notebook.add(new_tab, text=tab_name)
    return new_tab


def create_frame(parent_frame):
    frame = Frame(parent_frame, highlightthickness=1)
    frame.configure(background='#f1f1f1')
    frame.pack(anchor='w')
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
    background = kwargs.get('background', 'white')
    label = Label(frame, text=text)
    label.configure(background=background)
    label.grid(row=row, column=column)


def get_selected_tab(event):
    selected = event.widget.select()
    tab_text = event.widget.tab(selected, 'text')
    selected_tab[0] = tab_text


def create_dropbox(frame):
    options = ['Opção 1', 'Opção 2', 'Opção 3']
    selected_option = StringVar(value='Selecione uma opção')
    drop = OptionMenu(frame, selected_option, *options, command=dropdown)
    drop.pack()


def dropdown(selection):
    print(f'Selected option: {selection}')


def create_entry_boxes(window, date):
    table_name = selected_tab[0]
    columns = data.get_table_columns(table_name)
    row = 0
    for entry_box_id in range(len(columns)-1):
        create_label(window, text=columns[entry_box_id+1], row=row,
                     background='#f1f1f1')
        if entry_box_id == 0:
            Calendar(window, date, number=3, row=row, column=1)
        else:
            entry_box = Entry(window, width=30)
            entry_box.bind('<Return>', go_to_next_element)
            entry_box.grid(row=row, column=1)
            if len(entry_box_list) < (len(columns)-1):
                entry_box_list.append(entry_box)
        row += 1
    return row


def create_child_window(title):
    window = Toplevel()
    window.title(title)
    window.geometry('400x400')
    window.attributes('-topmost', True)
    window.focus_force()
    window.grab_set()
    entry_box_list.clear()
    return window


def create_window(title, button, command, date):
    global window
    window = create_child_window(title)
    notebook = create_notebook(window)
    tab1 = create_tab(notebook=notebook, tab_name='Entradas')
    tab2 = create_tab(notebook=notebook, tab_name='Avançado')
    window.bind('<Escape>', close_window)
    row = create_entry_boxes(tab1, date)
    create_label(tab2, text='Parcelas', row=row, background='#f1f1f1')
    entry_box = Entry(tab2, width=30)
    entry_box.bind('<Return>', go_to_next_element)
    entry_box.grid(row=row, column=1)
    entry_box_list.append(entry_box)
    row += 1
    confirm_button = ttk.Button(tab1, text=button, command=command, width=45)
    confirm_button.grid(row=row, column=0, columnspan=2, padx=10, pady=10)
    row += 1
    clear_button = ttk.Button(tab1, text='Limpar', command=clear_entrys,
                              width=45)
    clear_button.grid(row=row, column=0, columnspan=2, padx=10, pady=10)


def clear_entrys():
    for e in entry_box_list:
        e.delete(0, 'end')


def close_window(event):
    window.destroy()


def go_to_next_element(event):
    event.widget.tk_focusNext().focus()


def show_msg_box(message):
    messagebox.showwarning(title='Warning', message=message)


def create_tree_scroll(frame, orient, tree):
    treescroll = ttk.Scrollbar(frame, orient=orient)
    if orient == 'vertical':
        treescroll.config(command=tree.yview)
        treescroll.pack(side='right', fill='y')
    if orient == 'horizontal':
        treescroll.config(command=tree.xview)
        treescroll.pack(side='bottom', fill='x')
    return treescroll


def create_tree(frame, columns):
    style = ttk.Style()
    style.theme_use('default')
    style.configure('Treeview', background='#f1f1f1',
                    fieldbackground='#f1f1f1')
    tree = ttk.Treeview(frame, height=30, columns=columns)
    y_scroll = create_tree_scroll(frame, 'vertical', tree)
    x_scroll = create_tree_scroll(frame, 'horizontal', tree)
    tree.config(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
    tree.pack(side='left',  fill='both', expand=True)
    for column in columns:
        tree.heading(column, text=column, anchor='w')
    return tree


def create_entry_tree(frame, table_name):
    columns = data.get_table_columns(table_name)
    tree = create_tree(frame, columns)
    tree.column('#0', width=0, stretch='no')
    tree.column('#1', width=30, stretch='no')
    tree.column('#2', width=70, stretch='no')
    tree.column('#3', width=70, stretch='no')
    tree.column('#4', width=70, stretch='no')
    trees.update({table_name: tree})
    update_entry_tree(table_name)


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


def create_abstract_tree(frame, columns):
    tree = create_tree(frame, columns)
    tree.column('#0', width=30, stretch='no')
    tree.column('#1', width=120, stretch='no')
    tree.column('#2', width=90, stretch='no')
    trees.update({'Resumo': tree})
    update_abstract_tree()


def update_abstract_tree():
    table_name = 'Lançamentos'
    column = 'Categoria'
    column2 = 'Subcategoria'
    start_date = date_list[0]
    end_date = date_list[1]
    tree_object = trees['Resumo']
    tree_object.delete(*tree_object.get_children())
    df = data.read_sql(table_name, data.engine)
    df['Data'] = data.to_datetime(df['Data'])
    df = df.fillna('')
    df['Valor'] = df['Valor'].replace('', 0)
    unique_values = df[column].unique()
    unique_values.sort()
    for value in unique_values:
        df1 = df[(df[column] == value) & (df['Data'] >= start_date) &
                 (df['Data'] <= end_date)]
        unique_values2 = df1[column2].unique()
        unique_values2.sort()
        parent = tree_object.insert('', 'end',
                                    values=(value,
                                            f'{df1["Valor"].sum():.2f}'))
        for val in unique_values2:
            df2 = df1[(df1[column2] == val) & (df1['Data'] >= start_date) &
                      (df1['Data'] <= end_date)]
            tree_object.insert(parent, 'end',
                               values=(val, f'{df2["Valor"].sum():.2f}'))


def new_entry():
    create_window('Nova entrada', 'Confirmar', new_row, data.datetime.today())


def new_row():
    tree_name = selected_tab[0]
    entrys = get_entry_box_values()
    try:
        times = int(entrys[-1])
    except ValueError:
        times = entrys[-1] = 1
    Id = data.get_last_row_id(tree_name) + 1
    new_entrys = [Id]
    new_entrys.append(data.convert_string_to_date(date_list[2]))
    validated_entry = data.validate_entrys(tree_name, entrys)
    new_entrys += validated_entry
    for n in range(0, times):
        new_entrys[3] = f'{n + 1} de {times}'
        data.create_row(table_name=tree_name, values=new_entrys)
        new_entrys[0] += 1
        new_entrys[1] = data.add_month_to_date(new_entrys[1], 1)
    update_abstract_tree()
    update_entry_tree(tree_name)


def edit_row(*args):
    tree_name = selected_tab[0]
    tree_object = trees[tree_name]
    row_values = tree_object.item(tree_object.focus(), 'values')
    Id = row_values[0]
    date = row_values[1]
    create_window(f'Editar entrada {Id}', 'Salvar', lambda: save_row
                  (tree_name, tree_object, row_values, Id, date), date)
    for entry_box_id, text in enumerate(row_values[2:]):
        entry_box_list[entry_box_id].insert(0, text)


def save_row(tree_name, tree_object, row_values, Id, date):
    new_entrys = [Id]
    new_entrys.append(data.convert_string_to_date(date_list[2]))
    entrys = get_entry_box_values()
    validated_entry = data.validate_entrys(tree_name, entrys)
    new_entrys += validated_entry
    data.update_row_values(table_name=tree_name, values=new_entrys)
    update_abstract_tree()
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
    update_abstract_tree()
    update_entry_tree(tree_name)


def import_image(path):
    image = Image.open(path)
    resized_image = image.resize((30, 30))
    imagetk = ImageTk.PhotoImage(resized_image)
    return imagetk
