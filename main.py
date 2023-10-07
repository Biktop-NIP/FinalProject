from tkinter import *
from tkinter import ttk
from tkinter.messagebox import askyesno
from db import *
import conf
import re


class Window(Tk):
    def __init__(self):
        super().__init__()
        self.menager = DbManager()
        
        self.title(conf.title)
        self.geometry(conf.geometry)
        
        s = ttk.Style() # стили для текста
        s.configure(".", font=('Helvetica', 12))
        s.configure('my.TLabel', foreground='red')
        
        self.search = StringVar(value="") # текст поиска
        self.error = StringVar() # вывод ошибок
        self.order_by = StringVar(value="") # поле сортировки
        
        self.create_widgets()

    def create_widgets(self):
        """ создание виджетов """
        
        self.create_search()
        self.create_table()
        self.create_form()
    
    def create_search(self):
        """ создание поля поиска """
        search_frame = Frame()
        search_frame.pack(anchor=W, padx=50, pady=[30, 0])
        
        # ввод текста поиска
        ent_search = ttk.Entry(search_frame, textvariable=self.search, font=conf.enter_font)
        ent_search.grid(column=0, row=0, columnspan=2)
        
        # кнопка для поиска
        btn = ttk.Button(search_frame, text='искать', command=lambda: self.change_table_data())
        btn.grid(column=3, row=0)
        
        # label для сортировки
        lb = ttk.Label(search_frame, text="сортировать по ")
        lb.grid(column=4, row=0, padx=5)
        
        # выбор сортировки
        combox = ttk.Combobox(search_frame, textvariable=self.order_by, state="readonly",
                              values=['']+list(conf.fields.values()), font=conf.enter_font)
        combox.bind("<<ComboboxSelected>>", lambda e: self.change_table_data())
        combox.grid(column=5, row=0)
        
    def create_form(self):
        """ создание формы """
        form_frame = ttk.Frame()
        form_frame.pack(anchor=W, padx=50)
        
        # создание полей формы
        fields = conf.fields.copy()
        for i, (key, value) in enumerate(fields.items()):
            label = ttk.Label(form_frame, text=value)
            entry = ttk.Entry(form_frame, font=conf.enter_font)
            label.grid(column=0, row=i, ipady=5, sticky=W)
            entry.grid(column=1, columnspan=2, row=i, ipady=5)
            fields[key] = (label, entry)
        self.form_fields = fields
        
        
        # кнопки под формой
        buttons_frame = Frame(form_frame)
        buttons_frame.grid(column=0, row=6, columnspan=2, pady=5)
        
        btn = ttk.Button(buttons_frame, text='изменить', command=self.update_staffer)
        btn.grid(column=1, row=0)
        btn = ttk.Button(buttons_frame, text='удалить', command=self.delete_staffer)
        btn.grid(column=2, row=0)
        btn = ttk.Button(buttons_frame, text='добавить', command=self.add_staffer)
        btn.grid(column=3, row=0)
        
        # отображение ошибок
        lb_errors = ttk.Label(form_frame, text="", textvariable=self.error, style='my.TLabel')
        lb_errors.grid(columnspan=2)
        
    def create_table(self):
        """ создание таблицы """
        table = ttk.Treeview(columns=['id']+list(conf.fields.keys()), 
                                  displaycolumns=list(range(1,len(conf.fields)+1)),
                                  show="headings", selectmode='browse')
        table.pack(anchor=SW, fill="x", padx=50, pady=[10, 30])
        self.bind("<<TreeviewSelect>>", self.item_selected)
        for i, column in enumerate(conf.fields.values()):
            table.heading(i+1, text=column) # добавление заголовкив столбцов
            table.column(i+1, width=conf.column_width[i+1]) # задание ширины столбцов
        
        self.table = table
        self.change_table_data()
        
    
    def change_table_data(self):
        """ загрузить данные в таблицу из базы данных """
        self.staffer_selected = None
        self.table.delete(*self.table.get_children())
        
        params = {}
        if self.search.get() != "":
            params['search_str'] = self.search.get()
        if self.order_by.get() != "":
            val = self.order_by.get()
            for key, value in conf.fields.items():
                if value == val:
                    val = key
                    break
            params['oreder_by'] = key
            
        data = self.menager.all(**params)
        for staffer in data:
            self.table.insert("", END, values=staffer)
        
    def item_selected(self, event):
        """ выбор элемента из таблицы """
        try:
            staffer_selected_id = self.table.selection()[0]
        except:
            if self.staffer_selected is None: return
            staffer_selected_id = self.staffer_selected
        staffer_selected = self.table.item(staffer_selected_id)
        self.staffer_selected = staffer_selected_id
        self.staffer_id = staffer_selected["values"][0]
        values = staffer_selected["values"][1:]
        for field, value in zip(self.form_fields.values(), values):
            field[1].delete(0, END)
            field[1].insert(0, str(value))
    
    def update_staffer(self):
        """ изменить сотрудника """
        if not "staffer_id" in self.__dict__ or self.staffer_id is None:
            self.error.set("выберети запись")
            return
        values = {}
        for field, key in zip(self.form_fields.values(), conf.fields):
            values[key] = field[1].get()
        self.menager.update(self.staffer_id, **values)
        result = self.validate_data(values=values)
        if isinstance(result, str):
            self.error.set(result)
            return
        self.error.set("")
        self.table.item(self.staffer_selected, values=[self.staffer_id]+list(result.values()))
    
    def delete_staffer(self):
        """ удалить сотрудника """
        if askyesno('Вы уверены?', "удалить сотрудника"):
            self.menager.delete(self.staffer_id)
            self.change_table_data()
    
    def add_staffer(self):
        """ добавить сотрдника """
        values = {}
        for field, key in zip(self.form_fields.values(), conf.fields):
            values[key] = field[1].get()
        
        result = self.validate_data(values=values)
        if isinstance(result, str):
            self.error.set(result)
            return
        self.error.set("")
        
        self.menager.add(**values)
        self.change_table_data()
    
    @staticmethod
    def validate_data(values: dict) -> dict:
        """ проверить данные """
        values = values.copy()
        for key, value in values.items():
            if key in ['salary', 'phone']:
                try:
                    values[key] = int(value)
                except:
                    return key + " должно быть числом"
            elif key == 'email':       
                regex = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
                if re.fullmatch(regex, value) and len(value) <= 120:
                    values[key] = value
                else:
                    return "не верный email"
        return values
        

if __name__ == "__main__":
    root = Window()
    root.mainloop()
    