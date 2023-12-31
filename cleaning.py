import tkinter as tk
from tkinter import ttk
from _config import col_types, fill_types
from screen import Screen


class Cleaning(Screen):
    def __init__(self, controller):
        super().__init__(controller)
        self.working_data = self.data.get_working_data()
                
        self.buttons()
        self.dataframe()
        self.tools_group()
        
        self.root.mainloop()
    
    def update_views(self):
        for item in self.tree.get_children(): self.tree.delete(item)     
        for index, row in self.working_data.iterrows(): self.tree.insert('', index, values=list(row))
        
        columns = self.working_data.columns
        columns_box.delete(0, tk.END)
        
        for col, text in enumerate(columns): self.tree.heading(col, text=text)
        for column, dytype in self.working_data.dtypes.items(): columns_box.insert(tk.END, f'{column}: {dytype}')

    def on_reset(self):
        self.working_data = self.data.get_working_data()
        self.update_views()
        
    def on_apply_preset(self):
        self.working_data = self.data.preset_clean_data()
        self.update_views()
        
    def on_delete_rows(self):
        selected_rows = self.tree.selection()
        for row in selected_rows: self.tree.delete(row)
        self.data.delete_rows(selected_rows)
        self.working_data = self.data.get_working_data()
        print(self.working_data)
        
    def on_fill(self):
        selection_index = columns_box.curselection()
        if selection_index:
            fill, column = self.selected_fill.get(), self.working_data.columns.values[columns_box.curselection()[0]]
            self.data.fill(fill, column)
            self.working_data = self.data.get_working_data()
        print(self.working_data)
        self.update_views()
        
    def on_replace(self):
        selection_index = columns_box.curselection()
        if selection_index:
            if to_replace.get() and replace_with.get():
                column = self.working_data.columns.values[selection_index[0]]
                self.data.replace(column, to_replace.get(), replace_with.get())
                self.working_data = self.data.get_working_data()
                print(self.working_data[column])
            else: self.popup_dialog('Error','Ensure both replacement fields are filled!')
        else: self.popup_dialog('Error','Select a column!')
        self.update_views()
        
    def on_set_type(self):
        selection_index = columns_box.curselection()
        if selection_index:
            column = self.working_data.columns.values[selection_index[0]]
            try:
                self.data.set_type(column, selected_coltype)
                self.working_data = self.data.get_working_data()   
                print(self.working_data.dtypes)
            except: self.popup_dialog('Error','Column type cannot be converted to target type!')
        else: self.popup_dialog('Error','Select a column!')
        self.update_views()
    
    def on_set_name(self):
        selection_index = columns_box.curselection()
        if selection_index:
            if new_name.get():
                column, name = self.working_data.columns.values[selection_index[0]], new_name.get()
                self.data.set_name(name, column)
                self.working_data = self.data.get_working_data()
                print(self.working_data.columns)
            else: self.popup_dialog('Error','Enter a new name!')
        else: self.popup_dialog('Error','Select a column!')
        self.update_views()
    
    def on_save(self):
        self.data.set_working_data(self.working_data)
        self.on_save_to_database()
        
    def on_continue_to(self):
        self.data.set_working_data(self.working_data)
        self.controller.show_analysis()
        
    def dataframe(self):
        dataframe = tk.Frame(self.root)
        dataframe.pack(expand=True, fill=tk.BOTH)
        self.tree = ttk.Treeview(dataframe, selectmode='extended')
        self.tree.place()
        
        vertical_scrollbar = ttk.Scrollbar(dataframe, orient='vertical', command=self.tree.yview)
        horizontal_scrollbar = ttk.Scrollbar(dataframe, orient='horizontal', command=self.tree.xview)
        
        self.tree.configure(yscrollcommand=vertical_scrollbar.set)
        self.tree.configure(xscrollcommand=horizontal_scrollbar.set)
        
        self.tree['columns'] = list(self.working_data.columns)
        self.tree['show'] = 'headings'

        for column in self.working_data.columns:
            self.tree.heading(column, text=column)
            self.tree.column(column, width=50)

        for index, row in self.working_data.iterrows():
            self.tree.insert('', index, values=list(row))

        self.tree.pack(expand=True, fill=tk.BOTH)
        vertical_scrollbar.pack(side='right', fill='y')
        horizontal_scrollbar.pack(side='bottom', fill='x')
        
        delete_rows = tk.Button(dataframe, text='Delete Selected Rows', command=self.on_delete_rows)
        delete_rows.pack(side=tk.LEFT)
    
    def buttons(self):
        buttons = tk.Frame(self.root)
        buttons.pack(fill=tk.BOTH)
        
        exit = tk.Button(buttons, text='Exit', command=self.controller.exit)
        exit.pack(side=tk.RIGHT, fill=tk.BOTH)    
        
        reset = tk.Button(buttons, text='Reset', command=self.on_reset)
        reset.pack(side=tk.LEFT, fill=tk.BOTH)
        
        apply_preset = tk.Button(buttons, text='Apply Preset Cleaning' ,command=self.on_apply_preset)
        apply_preset.pack(side=tk.LEFT, fill=tk.BOTH)
        
        save = tk.Button(buttons,text='Save to Database', command=self.on_save)
        save.pack(side=tk.LEFT, fill=tk.BOTH)
        
        continue_to = tk.Button(buttons,text='Continue to Visualization', command=self.on_continue_to)
        continue_to.pack(side=tk.LEFT, fill=tk.BOTH)
        
    def tools_group(self):
        global tools
        tools = tk.Frame(self.root)
        tools.pack(expand=True, fill=tk.BOTH)
        
        self.columns_group()
        self.fill_group()
        self.replacement_group()
        self.type_group()
        self.rename_group()
        
    def columns_group(self):
        global columns, columns_box
        columns = tk.Frame(tools, relief='groove', borderwidth=1)
        columns.pack(side=tk.LEFT,fill=tk.BOTH)
        columns_box_frame = tk.Frame(columns)
        columns_box_frame.pack(fill=tk.BOTH)
        colums_label = tk.Label(columns_box_frame,text='Select a Column to Clean')
        colums_label.pack(fill=tk.BOTH)
        columns_box = tk.Listbox(columns)
        for column, dytype in self.working_data.dtypes.items(): columns_box.insert(tk.END, f'{column}: {dytype}')
        columns_box.pack(fill=tk.BOTH)
        
    def fill_group(self):
        global selected_fill
        fill_frame = tk.Frame(tools, relief='groove', borderwidth=1)
        fill_frame.pack(side=tk.LEFT, anchor='n')
        fill_label = tk.Label(fill_frame, text='Select Method to Fill Missing Values in Column')
        fill_label.pack()
        selected_fill = tk.StringVar()
        selected_fill.set(fill_types[0])
        for button_text in fill_types:
            radiobutton = tk.Radiobutton(fill_frame, text=button_text, variable=selected_fill, value=button_text)
            radiobutton.pack(anchor='w')
        fill_blanks = tk.Button(fill_frame,text='Fill Column Blanks', command=self.on_fill)    
        fill_blanks.pack(anchor='w')
    
    def replacement_group(self):
        global to_replace, replace_with
        replacement_frame = tk.Frame(tools, relief='groove', borderwidth=1)
        replacement_frame.pack(side=tk.LEFT, anchor='n')
        replacement_label = tk.Label(replacement_frame, text='Select a Column to Parse Below')
        replacement_label.pack()
        to_replace_label= tk.Label(replacement_frame, text='Enter Value to Mass Replace')
        to_replace_label.pack(anchor='w')
        to_replace = tk.Entry(replacement_frame)
        to_replace.pack(anchor='w')
        replace_with_label = tk.Label(replacement_frame, text='Enter Value to Mass Replace With')
        replace_with_label.pack(anchor='w')
        replace_with = tk.Entry(replacement_frame)
        replace_with.pack(anchor='w')
        replace = tk.Button(replacement_frame, text='Apply Change', command=self.on_replace)
        replace.pack(anchor='w')
    
    def type_group(self):
        global selected_coltype
        coltype_frame = tk.Frame(tools, relief='groove', borderwidth=1)
        coltype_frame.pack(side=tk.LEFT, anchor='n')
        coltype_label = tk.Label(coltype_frame, text='Change Datatype of Column Below')
        coltype_label.pack()
        selected_coltype = tk.StringVar()
        selected_coltype.set(col_types[0])
        for button_text in col_types:
            radiobutton = tk.Radiobutton(coltype_frame, text=button_text, variable=selected_coltype, value=button_text)
            radiobutton.pack(anchor='w')
        set_coltype = tk.Button(coltype_frame,text='Set Column Type', command=self.on_set_type)    
        set_coltype.pack(anchor='w')
    
    def rename_group(self):
        global new_name
        rename_frame = tk.Frame(tools, relief='groove', borderwidth=1)
        rename_frame.pack(side=tk.LEFT, anchor='n')
        rename_label = tk.Label(rename_frame, text='Enter a New Name for the Column')
        rename_label.pack()
        new_name = tk.Entry(rename_frame)
        new_name.pack(anchor='w')
        apply_rename = tk.Button(rename_frame, text='Apply New Name', command=self.on_set_name)
        apply_rename.pack(anchor='w')
        
   
    