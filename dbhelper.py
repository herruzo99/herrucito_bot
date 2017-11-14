import sqlite3


class DBHelper:
    def __init__(self, dbname="todo.sqlite"):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname)

    def setup(self):
        tblstmt = "CREATE TABLE IF NOT EXISTS items (description text, owner text,grupo text)"
        itemidx = "CREATE INDEX IF NOT EXISTS itemIndex ON items (description ASC)"
        ownidx = "CREATE INDEX IF NOT EXISTS ownIndex ON items (owner ASC)"
        gruidx = "CREATE INDEX IF NOT EXISTS gruIndex ON items (grupo ASC)"
        self.conn.execute(tblstmt)
        self.conn.execute(itemidx)
        self.conn.execute(ownidx)
        self.conn.commit()

    def add_item(self, item_text, owner,grupo):
        stmt = "INSERT INTO items (description, owner, grupo) VALUES (?, ?, ?)"
        args = (item_text, owner, grupo)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def delete_item(self, item_text, grupo):
        stmt = "DELETE FROM items WHERE description = (?) AND grupo = (?)"
        args = (item_text, grupo )
        self.conn.execute(stmt, args)
        self.conn.commit()

    def delete_group(self, grupo):
        stmt = "DELETE FROM items WHERE grupo = (?)"
        args = (grupo, )
        self.conn.execute(stmt, args)
        self.conn.commit()

    def get_items(self, grupo):
        stmto = "SELECT  owner FROM items WHERE grupo = (?)"
        stmt = "SELECT description  FROM items WHERE grupo = (?)"

        args = (grupo, )
        return ([x[0] for x in self.conn.execute(stmto, args)],[x[0] for x in self.conn.execute(stmt, args)])
