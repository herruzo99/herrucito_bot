import sqlite3


class DBHelper:
    def __init__(self, dbname="todo.sqlite"):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname)

    def setup(self):
        tblstmt = "CREATE TABLE IF NOT EXISTS items (description text, owner text,ownerid text,grupo text)"
        tblstmt2 = "CREATE TABLE IF NOT EXISTS calendar (recordatorio text, fecha text, nota text)"
        tblstmt2 = "CREATE TABLE IF NOT EXISTS usuarios (grupoid text, esGrupo bit, calendario bit,unique (grupoid))"


        itemidx = "CREATE INDEX IF NOT EXISTS itemIndex ON items (description ASC)"
        ownidx = "CREATE INDEX IF NOT EXISTS ownIndex ON items (owner ASC)"
        numberownidx = "CREATE INDEX IF NOT EXISTS ownIndex ON items (ownerid ASC)"
        gruidx = "CREATE INDEX IF NOT EXISTS gruIndex ON items (grupo ASC)"
        reqidx = "CREATE INDEX IF NOT EXISTS reqIndex ON calendar (recordatorio ASC)"
        fechaidx = "CREATE INDEX IF NOT EXISTS fechaIndex ON calendar (fecha ASC)"
        notaidx = "CREATE INDEX IF NOT EXISTS notaIndex ON calendar (nota ASC)"
        Grupoidx = "CREATE INDEX IF NOT EXISTS GrupoIndex ON usuarios (grupoid ASC)"
        self.conn.execute(tblstmt)
        self.conn.execute(tblstmt2)
        self.conn.execute(itemidx)
        self.conn.execute(ownidx)
        self.conn.execute(numberownidx)
        self.conn.execute(gruidx)
        self.conn.execute(reqidx)
        self.conn.execute(fechaidx)
        self.conn.execute(notaidx)
        self.conn.execute(Grupoidx)
        self.conn.commit()

    def nuevo_chat(self,grupo,esGrupo,calendario):
        stmt = " INSERT INTO usuarios (grupoid,esGrupo,calendario) VALUES (?,?,?)"
        args = (grupo,esGrupo,calendario)
        try:
            self.conn.execute(stmt,args)
            self.conn.commit()
        except:
            pass
    def sacar_chat(self,column,grupo):
        stmt = "SELECT {} FROM usuarios WHERE grupoid = {}".format(column,grupo)

        return self.conn.execute (stmt,).fetchone()

    def chat_calendario(self,calendario,grupo):
        stmt = "UPDATE usuarios SET calendario = (?) WHERE grupoid = (?)"
        args = (calendario,grupo)
        self.conn.execute(stmt,args)
        self.conn.commit()

    def limpiar_eventos(self,):
        stmt = "DELETE FROM calendar"
        self.conn.execute(stmt,)
        self.conn.commit()

    def nuevos_eventos(self,recordatorio,fecha,nota):
        stmt = "INSERT INTO calendar (recordatorio,fecha,nota) VALUES (?, ?,?)"
        args = (recordatorio,fecha,nota)
        self.conn.execute(stmt,args)
        self.conn.commit()

    def get_all_eventos(self,):
        stmt2 = "SELECT nota FROM calendar ORDER BY fecha"
        stmto = "SELECT recordatorio FROM calendar ORDER BY fecha"
        stmt = "SELECT fecha FROM calendar ORDER BY fecha"

        return ([x[0] for x in self.conn.execute (stmto,)],[x[0] for x in self.conn.execute(stmt,)],[x[0] for x in self.conn.execute(stmt2,)])

    def get_eventos(self,nota):
        stmto = "SELECT recordatorio FROM calendar WHERE nota = (?) ORDER BY fecha"
        stmt = "SELECT fecha FROM calendar WHERE nota = (?) ORDER BY fecha"
        args=(nota,)
        return ([x[0] for x in self.conn.execute (stmto,args)],[x[0] for x in self.conn.execute(stmt,args)])

    def add_item(self, item_text, owner,ownerid,grupo):
        stmt = "INSERT INTO items (description, owner,ownerid, grupo) VALUES (?, ?, ?, ?)"
        args = (item_text, owner,ownerid, grupo)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def auto_delete(self,grupo):
        stmt = "DELETE FROM items WHERE grupo = (?) LIMIT 1"
        args=(grupo,)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def number_rows(self,grupo):
        stmt = "SELECT COUNT(grupo)FROM items WHERE grupo = (?)"
        args=(grupo,)
        return [x[0] for x in self.conn.execute(stmt, args)]

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

    def get_grupos(self,):
        stmt = "SELECT grupo FROM items WHERE grupo != ownerid"
        return [x[0] for x in self.conn.execute(stmt,)]
