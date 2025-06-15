import GUI
import data

engine = data.create_database('sqlite:///database.db')

table1 = 'Lançamentos'
columns1 = {
    'Id': data.BIGINT,
    'Data': data.Date,
    'Valor': data.Float,
    'Parcela': data.VARCHAR,
    'Categoria': data.VARCHAR,
    'Subcategoria': data.VARCHAR,
    'Responsavel': data.VARCHAR,
    'Forma de pagamento': data.VARCHAR,
    'Descrição': data.VARCHAR
}

data.create_table_if_not_exists(table1, columns1, engine)

table2 = 'Cartões'
columns2 = {
    'Id': data.BIGINT,
    'Data': data.Date,
    'Valor': data.Float,
    'Parcela': data.VARCHAR,
    'Categoria': data.VARCHAR,
    'Subcategoria': data.VARCHAR,
    'Responsavel': data.VARCHAR,
    'Instituição': data.VARCHAR,
    'Mês fatura': data.VARCHAR,
    'Descrição': data.VARCHAR
}

data.create_table_if_not_exists(table2, columns2, engine)

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

frame0 = GUI.create_frame(tab0)
frame1 = GUI.create_frame(tab0)
frame2 = GUI.create_frame(tab1)
frame3 = GUI.create_frame(tab2)

GUI.create_button(frame=frame0, text='Importar',
                  command=data.import_from_excel, image=image_import)
GUI.create_button(frame=frame0, text='Exportar',
                  command=data.export_to_excel, image=image_export)
GUI.create_button(frame=frame2, text='Nova entrada',
                  command=GUI.new_entry, image=image_new)
GUI.create_button(frame=frame2, text='Editar',
                  command=GUI.edit_row, image=image_edit)
GUI.create_button(frame=frame2, text='Excluir',
                  command=lambda: GUI.delete_row(0), image=image_delete_row)
GUI.create_button(frame=frame3, text='Nova entrada',
                  command=GUI.new_entry, image=image_new)
GUI.create_button(frame=frame3, text='Editar',
                  command=GUI.edit_row, image=image_edit)
GUI.create_button(frame=frame3, text='Excluir',
                  command=lambda: GUI.delete_row(0), image=image_delete_row)


# GUI.create_dropbox(frame0)

columns = ['Categorias', 'Total']

GUI.create_abstract_tree(tab0, columns)
GUI.create_entry_tree(tab1, 'Lançamentos')
GUI.create_entry_tree(tab2, 'Cartões')

GUI.create_label(frame1, row=0, text='Data Inicial', background='#f1f1f1')
GUI.Calendar(frame1, GUI.date_list[0], number=1, row=0, column=1)

GUI.create_label(frame1, row=1, text='Data Final', background='#f1f1f1')
GUI.Calendar(frame1, GUI.date_list[1], number=2, row=1, column=1)

root.mainloop()
