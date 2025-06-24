import GUI
from data import create_table_if_not_exists, create_database
from sqlalchemy import BIGINT, VARCHAR, Float, Date

engine = create_database('sqlite:///database.db')

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
    'Descrição': VARCHAR
}

create_table_if_not_exists(table1, columns1, engine)

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
    'Descrição': VARCHAR
}

create_table_if_not_exists(table2, columns2, engine)

root = GUI.create_main_window('Finanças')

image_new = GUI.import_image('icons/novo.jpg')
image_edit = GUI.import_image('icons/editar.jpg')
image_delete = GUI.import_image('icons/lixo.jpg')
image_import = GUI.import_image('icons/entrar.jpg')
image_export = GUI.import_image('icons/saida.jpg')

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

GUI.create_common_buttons(frame=frame2, master=root, image_new=image_new,
                          image_edit=image_edit, image_delete=image_delete,
                          image_import=image_import, image_export=image_export)
GUI.create_common_buttons(frame=frame3, master=root, image_new=image_new,
                          image_edit=image_edit, image_delete=image_delete,
                          image_import=image_import, image_export=image_export)

GUI.EntryTreeview(tab1, 'Lançamentos')
GUI.EntryTreeview(tab2, 'Cartões')

columns = ['Categorias', 'Total']
GUI.Options(columns=columns, upper_frame=frame0, lower_frame=frame1)

root.mainloop()
