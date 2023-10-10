import psycopg2

class Db:

    def __init__(self, connection_url) -> None:
        self.connection_url = connection_url

    def __conn(self):
        self.conn = psycopg2.connect(self.connection_url)
        self.cur = self.conn.cursor()

    def __close(self):
        self.conn.close()

    def query(self, text, *args, commit=False):
        self.__conn()
        self.cur.execute(text, args)
        try:
            result = self.cur.fetchone()
        except psycopg2.ProgrammingError:
            result = None
        if commit:  
            self.conn.commit()
        self.__close()
        return result

    def select(self, text, *args):
        self.__conn()
        self.cur.execute(text, args)
        result = self.cur.fetchall()
        self.__close()
        return result
