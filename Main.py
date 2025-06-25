import GUI
from data import DatabaseManager
from utils import import_image
from sqlalchemy import BIGINT, VARCHAR, Float, Date

table1 = 'Lançamentos'
columns1 = {
    'Id': BIGINT,
    'Data': Date,
    'Valor': Float,
    'Parcela': VARCHAR,
    'Categoria': VARCHAR,
    'Subcategoria': VARCHAR,
    'Responsavel': VARCHAR,
    'Forma de pagamento': VARCHAR,
    'Descrição': VARCHAR}

table2 = 'Cartões'
columns2 = {
    'Id': BIGINT,
    'Data': Date,
    'Valor': Float,
    'Parcela': VARCHAR,
    'Categoria': VARCHAR,
    'Subcategoria': VARCHAR,
    'Responsavel': VARCHAR,
    'Instituição': VARCHAR,
    'Mês fatura': VARCHAR,
    'Descrição': VARCHAR}

dbmanager = DatabaseManager('sqlite:///database.db')
dbmanager.create_table_if_not_exists(table1, columns1)
dbmanager.create_table_if_not_exists(table2, columns2)

root = GUI.MainApp('Finanças', dbmanager)

img_new = import_image('icons/novo.jpg')
img_edit = import_image('icons/editar.jpg')
img_delete = import_image('icons/lixo.jpg')
img_import = import_image('icons/entrar.jpg')
img_export = import_image('icons/saida.jpg')

root.get_images(img_new=img_new, img_edit=img_edit, img_delete=img_delete,
                img_import=img_import, img_export=img_export)

notebook = GUI.Notebook(root)
notebook.bind('<<NotebookTabChanged>>', lambda event:
              notebook.get_selected_tab())

tab0 = GUI.create_tab(notebook=notebook, tab_name='Resumo')
tab1 = GUI.create_tab(notebook=notebook, tab_name='Lançamentos')
tab2 = GUI.create_tab(notebook=notebook, tab_name='Cartões')

frame0 = GUI.create_frame(tab0, side='top')
frame1 = GUI.create_frame(tab0, side='top')
frame2 = GUI.create_frame(tab1, side='top')
frame3 = GUI.create_frame(tab2, side='top')

root.create_common_buttons(frame2)
root.create_common_buttons(frame3)

GUI.EntryTreeview(tab1, 'Lançamentos', master=root)
GUI.EntryTreeview(tab2, 'Cartões', master=root)

columns = ['Categorias', 'Total']
columns_to_group = ['Categoria', 'Subcategoria']
GUI.Options(columns=columns, upper_frame=frame0, lower_frame=frame1,
            master=root, columns_to_group=columns_to_group)

root.mainloop()
