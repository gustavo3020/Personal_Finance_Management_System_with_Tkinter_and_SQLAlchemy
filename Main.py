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

image_import = GUI.import_image('icons/entrar.jpg')
image_export = GUI.import_image('icons/saida.jpg')
image_new = GUI.import_image('icons/novo.jpg')
image_edit = GUI.import_image('icons/editar.jpg')
image_delete_row = GUI.import_image('icons/lixo.jpg')

notebook = GUI.create_notebook(root)
notebook.bind('<<NotebookTabChanged>>', GUI.get_selected_tab)
tab0 = GUI.create_tab(notebook=notebook, tab_name='Resumo')
tab1 = GUI.create_tab(notebook=notebook, tab_name='Lançamentos')
tab2 = GUI.create_tab(notebook=notebook, tab_name='Cartões')

# frame0 = GUI.create_frame(tab0, side='top')
frame1 = GUI.create_frame(tab0, side='top')
frame2 = GUI.create_frame(tab1, side='top')
frame3 = GUI.create_frame(tab2, side='top')

GUI.create_button(frame=frame2, text='Nova entrada',
                  command=GUI.new_entry, image=image_new)
GUI.create_button(frame=frame2, text='Editar',
                  command=GUI.edit_row, image=image_edit)
GUI.create_button(frame=frame2, text='Excluir',
                  command=lambda: GUI.delete_row(0), image=image_delete_row)
GUI.create_button(frame=frame2, text='Importar',
                  command=GUI.import_table, image=image_import)
GUI.create_button(frame=frame2, text='Exportar',
                  command=GUI.export_table, image=image_export)
GUI.create_button(frame=frame3, text='Nova entrada',
                  command=GUI.new_entry, image=image_new)
GUI.create_button(frame=frame3, text='Editar',
                  command=GUI.edit_row, image=image_edit)
GUI.create_button(frame=frame3, text='Excluir',
                  command=lambda: GUI.delete_row(0), image=image_delete_row)
GUI.create_button(frame=frame3, text='Importar',
                  command=GUI.import_table, image=image_import)
GUI.create_button(frame=frame3, text='Exportar',
                  command=GUI.export_table, image=image_export)


# GUI.create_optionmenu(frame0)

columns = ['Categorias', 'Total']
frame4 = GUI.create_frame(tab0)
frame5 = GUI.create_frame(tab0)

GUI.create_abstract_tree(frame4, columns, 'Lançamentos')
GUI.create_abstract_tree(frame5, columns, 'Cartões')
GUI.create_entry_tree(tab1, 'Lançamentos')
GUI.create_entry_tree(tab2, 'Cartões')

GUI.create_label_grid(frame1, row=0, text='Data Inicial', background='#f1f1f1')
GUI.Calendar(frame1, GUI.date_list[0], number=1, row=0, column=1)

GUI.create_label_grid(frame1, row=1, text='Data Final', background='#f1f1f1')
GUI.Calendar(frame1, GUI.date_list[1], number=2, row=1, column=1)

root.mainloop()
