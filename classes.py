import psycopg2
import re
from functools import singledispatchmethod


class Clients_db:

    def __init__(self, db_name: str, user_name: str, passw: str):
        '''Функция для присоединения к существующей базе данных PostgreSQL
           Параметры: db_name - имя базы данных
                      user_name - имя пользователя
                      passw - пароль
        '''
        try:
            self.conn = psycopg2.connect(
                database=db_name, user=user_name, password=passw)
            self.cur = self.conn.cursor()
        except:
            print('Подключение не удалось')
            self.conn = None

    def create_table(self):
        '''Функция для создания таблиц Clients, Phone'''

        self.cur.execute('''
        CREATE TABLE IF NOT EXISTS Clients(
        id SERIAL PRIMARY KEY,
        name VARCHAR(40) NOT NULL,
        surname VARCHAR(40) NOT NULL,
        email VARCHAR(40) UNIQUE NOT NULL                                         
        );
        ''')

        self.cur.execute('''
        CREATE TABLE IF NOT EXISTS Phone(
        id SERIAL PRIMARY KEY,
        client_id INTEGER NOT NULL REFERENCES Clients(id),
        number VARCHAR(20) UNIQUE NOT NULL                                      
        );
        ''')

        self.conn.commit()

    def add_client(self, name: str, surname: str, email: str, phones: str | list[str] = None):
        '''Функция для добавления клиента в таблицу Clients
           Параметры: name - имя клиента
                      surname - фамилия клиента
                      email - адрес эл. почты клиента. Должен быть уникальным для каждого клиента.
           '''

        try:
            self.cur.execute('''
            INSERT INTO Clients(name, surname, email)
            VALUES (%s, %s, %s);
            ''', (name, surname, email))
            self.conn.commit()
            cur_id = self.search_id(name, surname, email)[0][0]
            if phones:
                if isinstance(phones, list):
                    for phone in phones:
                        self.add_phone(cur_id, phone)
                elif isinstance(phones, str):
                    self.add_phone(cur_id, phones)

        except psycopg2.errors.UniqueViolation:
            self.conn.rollback()
        except:
            print('Не удалось добавить нового клиента')
            self.conn.rollback()

    @singledispatchmethod
    def add_phone(self, id: int, phone: str, *args):
        '''Функция для добавления телефонного номера в таблицу Phone
           Параметры: id - уникальный идентификатор клиента (поле id таблицы Clients)
                      phone - телефонный номер клиента. Должен состоять только из цифр.
                      args - прочие необязательные аргументы
        '''

        if isinstance(id, int) and isinstance(phone, str) and re.fullmatch('\d*', phone):
            try:
                self.cur.execute('''
                INSERT INTO Phone(client_id, number)
                VALUES (%s, %s);
                ''', (id, phone))
                self.conn.commit()
            except psycopg2.errors.UniqueViolation:
                self.conn.rollback()
            except psycopg2.errors.ForeignKeyViolation:
                print('Пользователя с таким id не найдено в базе данных')
                self.conn.rollback()
            except Exception as err:
                print(type(err))
                self.conn.rollback()
        else:
            print(
                f'Тип данных {id} не является целым числом, либо тип данных {phone} не является строкой, либо в записи номера есть символы, не являющиеся цифрами')

    @add_phone.register(str)
    def _from_str(self, name: str = None, surname: str = '%', email: str = '%', phone: str = None):
        '''Функция для добавления телефонного номера в таблицу Phone по данным клиента (имя фамилия, эл. почта)
           Обязательно должно быть указано имя и телефон.
           В случае если указанным данным (имя, фамилия, эл. почта) соответствуют несколько записей, выводится
           соответствующее сообщение, добавление телефона не происходит)
        '''

        x = self.search_id(name, surname, email)
        if x:
            if len(x) > 1:
                print(
                    'В базе данных существует больше одного пользователя с такими данными')
            else:
                self.add_phone(x[0][0], phone)

    def search_id(self, name: str = '%', surname: str = '%', email: str = '%', phone: str = '%'):
        '''Функиця для поиска id клиента (поле id таблицы Clients) по указанным данным.'''

        try:
            if phone == '%':
                self.cur.execute('''
                SELECT id FROM Clients
                WHERE name LIKE %s AND surname LIKE %s AND email LIKE %s;''', (name, surname, email))
            else:
                self.cur.execute('''
                SELECT id FROM Clients
                WHERE name LIKE %s AND surname LIKE %s AND email LIKE %s AND 
                      id IN (SELECT client_id FROM Phone WHERE number = %s);
                ''', (name, surname, email, phone))
            x = self.cur.fetchall()
            if not x:
                print('Пользователя с такими данными нет в базе данных')
            else:
                return x
        except Exception as err:
            self.conn.rollback()
            return f'Ошибка: {type(err)}'

    def search_client(self, name: str = '%', surname: str = '%', email: str = '%', phone: str = '%'):
        '''Функция для поиска всех клиентов, которые соответствуют указанным данным(
           имя, фамилия, эл. почта, телефон).
        '''

        clients = self.search_id(
            name=name, surname=surname, email=email, phone=phone)
        counter, strings = -1, []
        if isinstance(clients, list) and clients:
            for el in clients:
                self.cur.execute('''
                        SELECT name, surname, email
                        FROM Clients
                        WHERE id = %s;
                        ''', (el))
                x = self.cur.fetchone()
                counter += 1
                strings.append(f'Имя: {x[0]} Фамилия: {x[1]} e-mail: {x[2]}')

                self.cur.execute('''
                        SELECT number
                        FROM Phone
                        WHERE client_id = %s;
                        ''', (el))
                y = [a[0] for a in self.cur.fetchall()]
                strings[counter] += (bool(y) == True) * \
                    f' Номера телефонов: {", ".join(y)}'
            return strings
        else:
            return clients

    def del_phone(self, phone: str):
        '''Функция для удаления одного конкретного номера телефона'''

        if isinstance(phone, str) and re.fullmatch('\d*', phone):
            try:
                self.cur.execute(
                    '''DELETE FROM Phone WHERE number = %s;''', (phone,))
                self.conn.commit()
            except Exception as err:
                print(type(err))
                self.conn.rollback()
        else:
            print(
                f'Тип данных {phone} не является строкой, либо в записи номера есть символы, не являющиеся цифрами')

    @singledispatchmethod
    def del_all_phone(self, id: int):
        '''Функция для удаления всех номеров телефона клиента по его id (поле id таблицы Clients)'''

        if isinstance(id, int):
            try:
                self.cur.execute(
                    'DELETE FROM Phone WHERE client_id = %s;', (id,))
                self.conn.commit()
            except Exception as err:
                print(type(err))
                self.conn.rollback()
        else:
            print(
                f'Тип данных {id} не является целым числом')

    @del_all_phone.register(str)
    def del_from_str(self, name: str, surname: str = '%', email: str = '%'):
        '''Функция для удаления всех номеров телефонов для клиента по его данным(имя, фамилия, эл. почта)'''

        x = self.search_id(
            name=name, surname=surname, email=email)
        if x:
            if len(x) > 1:
                print('В базе данных больше одного пользователя с такими данными')
            else:
                self.del_all_phone(x[0][0])

    def del_client(self, id: int):
        '''Функция для удаления клиента по его id (поле id таблицы Clients)'''

        if isinstance(id, int):
            try:
                self.del_all_phone(id)
                self.cur.execute('DELETE FROM Clients WHERE id = %s;', (id,))
                self.conn.commit()
            except Exception as err:
                print(type(err))
                self.conn.rollback()
        else:
            print(
                f'Тип данных {id} не является целым числом')

    def change_client(self, id, name: str = None, surname: str = None, email: str = None):
        '''Функция для изменения данных клиена по его id (поле id таблицы Clients)'''

        if isinstance(id, int):
            try:
                self.cur.execute(
                    'SELECT name, surname, email FROM Clients WHERE id = %s;', (id,))
                x = self.cur.fetchone()
                name = name if name else x[0]
                surname = surname if surname else x[1]
                email = email if email else x[2]
                self.cur.execute('''
                    UPDATE Clients 
                    SET name = %s, surname = %s, email = %s WHERE id = %s;
                    ''', (name, surname, email, id))
            except Exception as err:
                print(type(err))
                self.conn.rollback()

    def select_clients(self, string: str):
        '''Функция для вывода всех записей таблицы Clients'''

        self.cur.execute('SELECT * FROM Clients;')
        print(string, ('id', 'name', 'surname', 'email'),
              *self.cur.fetchall(), sep='\n', end='\n\n')

    def select_phone(self, string: str):
        '''Функция для вывода всех записей таблицы Phone'''

        self.cur.execute('SELECT * FROM Phone;')
        print(string, ('id', 'client_id', 'number'),
              *self.cur.fetchall(), sep='\n', end='\n\n')

    def close_func(self):
        '''Функция для удаления таблиц Phone, Clients и закрытия курсора, объекта соединения'''

        self.cur.execute("""
        DROP TABLE Phone;
        DROP TABLE Clients;
        """)
        self.conn.commit()

        self.cur.close()
        self.conn.close()
