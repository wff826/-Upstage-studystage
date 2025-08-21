import sqlite3

class HistoryDB:
    def __init__(self, path="./study.db"):
        self.conn = sqlite3.connect(path)
        self.cur = self.conn.cursor()
        self._init_tables()

    def _init_tables(self):
        self.cur.execute("CREATE TABLE IF NOT EXISTS qa (q TEXT, a TEXT)")
        self.cur.execute("CREATE TABLE IF NOT EXISTS quiz (topic TEXT, level TEXT, content TEXT)")
        self.cur.execute("CREATE TABLE IF NOT EXISTS plan (goal TEXT, days INT, hours INT, content TEXT)")
        self.conn.commit()

    def save_qa(self, q, a):
        self.cur.execute("INSERT INTO qa VALUES (?,?)", (q, a))
        self.conn.commit()

    def save_quiz(self, topic, level, quiz):
        self.cur.execute("INSERT INTO quiz VALUES (?,?,?)", (topic, level, quiz))
        self.conn.commit()

    def save_plan(self, goal, days, hours, plan):
        self.cur.execute("INSERT INTO plan VALUES (?,?,?,?)", (goal, days, hours, plan))
        self.conn.commit()
