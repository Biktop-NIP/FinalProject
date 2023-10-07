import sqlite3 as sq
import conf
from typing import Optional


class DbManager():
    def __init__(self):
        self.con, self.cur = self.connection()
        self.con.create_function("LOWER", 1, self.sqlite_lower) # переопределение LOWER для работы с кирилицей
    
    @staticmethod
    def sqlite_lower(value_):
        return value_.lower()
    
    def get(self, id:int):
        """ выбрать сотрудника по айди """
        sql = f""" SELECT * FROM staff WHERE id={id}"""
        
        self.cur.execute(sql)
        result = self.cur.fetchall()
        return result[0]
    
    def delete(self, id: int):
        """ удалть сотрудника по айди """
        sql = f""" DELETE FROM staff WHERE id={id}"""
        
        self.cur.execute(sql)
        self.con.commit()

    def all(self, oreder_by: Optional[str]=None, search_str: Optional[str]=None):
        """ выбрать записи """
        sql = f""" SELECT * FROM staff """
        if search_str is not None:
            search_str = search_str.lower()
            sql += f""" WHERE LOWER(last_name) LIKE "%{search_str}%" OR 
                LOWER(first_name) LIKE "%{search_str}%" OR LOWER(patronymic) LIKE "%{search_str}%" """
        if oreder_by is not None:
            sql += " ORDER BY "+oreder_by+" DESC "
        self.cur.execute(sql)
        result = self.cur.fetchall()
        return result
    
    def add(self, last_name: str ,first_name: str, patronymic: str,
            phone: int, email: str , salary: int) -> None:
        """ Добавление записи """
        
        sql = f""" INSERT INTO staff 
                  (last_name, first_name, patronymic, phone, email, salary)
                  VALUES ("{last_name}", "{first_name}", "{patronymic}", 
                           {phone}, "{email}", {salary})"""
        self.cur.execute(sql)
        self.con.commit()
    
    def update(self, id: int, last_name: Optional[str]=None , first_name: Optional[str]=None, 
            patronymic: Optional[str]=None, phone: Optional[int]=None, 
            email: Optional[str]=None , salary: Optional[int]=None):
        """ изменить запись """
        
        params = {}
        if last_name is not None: params['last_name'] = last_name
        if first_name is not None: params['first_name'] = first_name
        if patronymic is not None: params['patronymic'] = patronymic
        if phone is not None: params['phone'] = phone
        if email is not None: params['email'] = email
        if salary is not None: params['salary'] = salary
        if not params:
            raise ValueError("нужно передать хотябы один параметр")
        params_str = ', '.join([key+" = "+ ('"'+value+'"' if type(value)==str else str(value))
                               for key, value in params.items()])
        sql = f'UPDATE staff SET {params_str} WHERE id = {id};'

        self.cur.execute(sql)
        self.con.commit()
    
    @staticmethod
    def connection() -> [sq.Connection, sq.Cursor]:
        """ подключение к базе данных """
        with sq.connect(conf.db_name) as con:
            cur = con.cursor()
        
        return con, cur
