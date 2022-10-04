import psycopg2


class Settings():
    DATABASE = 'data_base_name'
    USER = 'user_name'
    PASSWORD = 'password'


def create_db(conn):
    with conn.cursor() as cur:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS clients (
                client_id SERIAL PRIMARY KEY,
                name VARCHAR(60) NOT NULL,
                email VARCHAR(60)
        );
        CREATE TABLE IF NOT EXISTS phones (
                phone_id SERIAL PRIMARY KEY,
                phone VARCHAR(12) NOT NULL,
                client_id INTEGER REFERENCES clients(client_id)
        );
        """)
        conn.commit()


def add_client(conn, name, email, phones=None):
    with conn.cursor() as cur:
        cur.execute("""
        INSERT INTO clients(name, email)
        VALUES(%s, %s) RETURNING client_id;
        """, (name, email))
        client_id = cur.fetchone()[0]

        if phones: 
            if not isinstance(phones, list):
                phones = [phones]
            for phone in phones:
                add_phone(conn, client_id, phone)


def add_phone(conn, client_id, phone):
    with conn.cursor() as cur:
        cur.execute("""
        INSERT INTO phones(phone, client_id) VALUES(%s, %s);
        """, (phone, client_id))
        conn.commit()


def change_client(conn, client_id, name=None, email=None, phones=None):
    with conn.cursor() as cur:
        if name is None:
            cur.execute("""
            SELECT name FROM clients
            WHERE client_id=%s;
            """, (client_id,))
            name = cur.fetchone()[0]
        
        if email is None:
            cur.execute("""
            SELECT email FROM clients
            WHERE client_id=%s;
            """, (client_id,))
            email = cur.fetchone()[0]

        cur.execute("""
        UPDATE clients SET name=%s, email=%s WHERE client_id=%s;
        """, (name, email, client_id))
        conn.commit()

        if phones: 
            if not isinstance(phones, list):
                phones = [phones]
            for phone in phones:
                cur.execute("""
                DELETE FROM phones WHERE client_id=%s;
                INSERT INTO phones(phone, client_id) VALUES(%s, %s);
                """, (client_id, phone, client_id))
                conn.commit()


def delete_phone(conn, client_id, phone):
    with conn.cursor() as cur:
        cur.execute("""
        DELETE FROM phones WHERE client_id=%s AND phone=%s;
        """, (client_id, phone))
        conn.commit()


def delete_client(conn, client_id):
    with conn.cursor() as cur:
        cur.execute("""
        DELETE FROM phones WHERE client_id=%s;
        DELETE FROM clients WHERE client_id=%s;
        """, (client_id, client_id))
        conn.commit()


def find_client(conn, name=None, email=None, phone=None):
    with conn.cursor() as cur:
        if name:
            cur.execute("""
            SELECT client_id, name, email FROM clients
            WHERE name=%s;
            """, (name,))
            return cur.fetchone()

        elif email:
            cur.execute("""
            SELECT client_id, name, email FROM clients
            WHERE email=%s;
            """, (email,))
            return cur.fetchone()
        
        elif phone:
            cur.execute("""
            SELECT c.client_id, name, email FROM clients AS c
            JOIN phones AS a ON a.client_id = c.client_id
            WHERE phone=%s;
            """, (phone,))
            return cur.fetchone()


if __name__ == '__main__':
    
    settings = Settings()
    conn = psycopg2.connect(database=settings.DATABASE, user=settings.USER, password=settings.PASSWORD)

    create_db(conn)

    print('Добавление нового клиента')
    add_client(conn, 'Василий Пупкин', 'pupok@yandex.ru', ['849651', '864532'])

    print('Добавить телефон для существующего клиента')
    add_phone(conn, 1, '84651321')

    print('Изменить данные о клиенте')
    change_client(conn, 1, name='Василий Дудкин', email='dudok@yandex.ru', phones='666777888')

    print('Найти клиента по его данным')
    client = find_client(conn, name='Василий Дудкин')
    client = find_client(conn, email='dudok@yandex.ru')
    client = find_client(conn, phone='666777888')
    print(client)

    print('Удалить телефон для существующего клиента')
    delete_phone(conn, 8, '666777888')

    print('Удалить существующего клиента')
    delete_client(conn, 1)

    conn.close()