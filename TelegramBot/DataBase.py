import psycopg2
import configparser

"""don't forget about safety"""
"""OFU - only for user"""

config = configparser.ConfigParser()
config.read('settings.ini')
password = config['Postgres']['password']


def delete_table():
    """activate the function only when the user uses the program again.
    The first time you try to disable a feature in the context manager(with (psycopg2.connect(database...)"""
    cur.execute("""
        DROP TABLE main_table1;
        DROP TABLE personal_table_OFU;
        DROP TABLE deleted_words_OFU;
        DROP TABLE new_words_OFU;
    """)
    return "Tables deleted"

def do_db():
    """database creation"""
    cur.execute("""
        CREATE TABLE IF NOT EXISTS main_table1 (
            id SERIAL NOT NULL,
	        russian_word VARCHAR(100) NOT NULL,
	        english_word VARCHAR(100) NOT NULL
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS new_words_OFU (
	        id VARCHAR(100) NOT NULL,
	        russian_word VARCHAR(100) NOT NULL,
	        english_word VARCHAR(100) NOT NULL
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS deleted_words_OFU (
            id VARCHAR(100) NOT NULL,
        	russian_word VARCHAR(100) NOT NULL,
        	english_word VARCHAR(100)
        );
    """)
    return "Database created"

def create_tables():
    """filling the main table"""
    cur.execute("""
        INSERT INTO main_table1(russian_word, english_word)
            VALUES('кот', 'cat'),
		          ('солнце', 'sun'),
		          ('дом', 'house'),
		          ('любовь', 'love'),
		          ('собака', 'dog'),
		          ('он', 'he'),
		          ('она', 'she'),
		          ('оно', 'it'),
		          ('дождь', 'rain'),
		          ('красный', 'red'),
		          ('черный', 'black'),
		          ('fly',	'летать'),
                  ('pilot', 'пилот'),
                  ('hospital', 'больница'),
                  ('estate', 'поместье'),
                  ('apartment', 'квартира'),
                  ('bakery', 'пекарня'),
                  ('temple', 'храм'),
                  ('church', 'церковь'),
                  ('doctor', 'доктор'),
                  ('nurse', 'няня'),
                  ('cup', 'чашка'),
                  ('cupboard', 'буфет'),
                  ('glass', 'стакан'),
                  ('plate', 'тарелка'),
                  ('saucepan', 'кастрюля'),
                  ('jug', 'кувшин'),
                  ('kettle', 'чайник'),
                  ('sink', 'тонуть'),
                  ('tap', 'постучать'),
                  ('telephone', 'телефон'),
                  ('knife', 'нож'),
                  ('plane', 'самолет'),
                  ('photographer', 'фотограф'),
                  ('reporter', 'репортер'),
                  ('postman', 'почтальон'),
                  ('cabbage', 'капуста'),
                  ('fork', 'вилка'),
                  ('spoon', 'ложка'),
                  ('waiter', 'официант'),
                  ('waitress', 'официантка'),
                  ('market', 'рынок'),
                  ('actor', 'актер'),
                  ('drugstore', 'аптека'),
                  ('pedestrian', 'пешеход'),
                  ('block', 'блок'),
                  ('bus', 'автобус'),
                  ('car', 'машина'),
                  ('stadium', 'стадион'),
                  ('street', 'улица'),
                  ('taxi', 'такси'),
                  ('tram', 'трамвай'),
                  ('underground', 'метрополитен'),
                  ('van', 'фургон'),
                  ('park', 'парк'),
                  ('boulevard', 'бульвар'),
                  ('truck', 'грузовик'),
                  ('bicycle', 'велосипед'),
                  ('train', 'поезд'),
                  ('coach', 'тренировать');
    """)
    return 'Tables created'

with (psycopg2.connect(database='dict_rus_en', user='postgres', password=password) as conn):
    with conn.cursor() as cur:
        delete_table()
        do_db()
        create_tables()







