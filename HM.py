from classes import Clients_db

db = Clients_db('clients_db', 'postgres', 'Cfvjktn')

if db.conn:
    # 1. создание таблиц Clients, Phone
    db.create_table()

    # 2. Добавление новых клиентов в таблицу Clients
    db.add_client('John', 'Travolta', 'big_john@google.com',
                  ['89112223344', '89029019009'])
    db.add_client('John', 'Malkovich', 'old_john@google.com', '89010102030')
    db.add_client('Katty', 'Parry', 'sweet_cat@google.com')
    db.select_clients('2. Записи в таблице Clients после этапа 2')
    db.select_phone('2. Записи в таблице Phone после этапа 2')

    # 3. Добавление телефонов для текущих клиентов
    db.add_phone(1, '89045667570')
    db.add_phone('John', 'Travolta', phone='89123456789')
    db.add_phone('John', email='old_john@google.com', phone='89630000000')
    db.add_phone('Katty', phone='89876543210')
    db.add_phone(3, '89049049040')
    db.select_phone('3. Записи в таблице Phone после этапа 3')

    # 4. Попытка добавить некорректные данные в таблицу Phone
    print('4. Попытка добавить некорректные данные в таблицу Phone')
    db.add_phone(5, '89999999999')
    db.add_phone('John', 'Smith', phone='89899899898')
    db.add_phone('John', phone='89633690000')
    db.add_phone('Kat', phone='89876543210')
    db.add_phone('Katty', phone='89049898904a')
    print('')

    # 5. Поиск клиента по данным
    print('5.1.', *db.search_client(name='John'), sep='\n')
    print('5.2.', *db.search_client(email='big_john@google.com'), sep='\n')
    print('5.3.', *db.search_client(phone='89049049040'), sep='\n')
    print('5.4.', *db.search_client(surname='Travolta'), sep='\n')
    print('5.5.', *db.search_client(name='John', phone='89630000000'), sep='\n')
    print('')

    # 6. Изменение данных о клиенте
    db.change_client(3, 'Katheryn', 'Hudson')
    db.change_client(1, 'Joseph', email='travolta_john@google.com')
    db.change_client(2, 'Joseph', surname='Malkov')
    db.select_clients('6. Записи в таблице Clients после этапа 6')

    # 7. Удаление телефонов
    db.del_phone('89049049040')  # удаление телефона по номеру
    db.del_all_phone('Joseph')  # попытка удаления по неуникальному имени
    # удаление всех телефонов по уникальному имени
    db.del_all_phone('Katheryn')
    db.del_all_phone(1)  # Удаление всех телефонов пользователя по id
    db.select_phone('7. Записи в таблице Phone после этапа 7')

    # 8. Удаление существующего клиента
    db.del_client(2)
    db.select_clients('8. Записи в таблице Clients после этапа 8')
    db.select_phone('8. Записи в таблице Phone после этапа 8')

    # 9. Удаление таблиц и закрытие курсора, объекта соединения
    db.close_func()
