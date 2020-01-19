import pymysql

class MYSQLDB:
    def __init__(self, host, user, pwd, db):
        self.host = host
        self.user = user
        self.pwd = pwd
        self.db = db

    def __GetConnect(self):
        try:
            self.conn = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.pwd,
                database=self.db,
                charset="utf8"
                )
            cur = self.conn.cursor()
            return cur
        except Exception as e:
            print('Fail connection: ', e)

    def ExecQuery(self, sql):
        """
        执行查询语句
        返回的是一个包含tuple的list，list的元素是记录行，tuple的元素是每行记录的字段

        调用示例：
                ms = MYSQL(host="localhost",user="sa",pwd="123456",db="PythonWeiboStatistics")
                resList = ms.ExecQuery("SELECT id,NickName FROM WeiBoUser")
                for (id,NickName) in resList:
                    print str(id),NickName
        """
        cur = self.__GetConnect()
        cur.execute(sql)
        resList = cur.fetchall()

        #查询完毕后必须关闭连接
        self.conn.close()
        return resList

    def ExecNonQuery(self, sql):
        """
        执行非查询语句

        调用示例：
            cur = self.__GetConnect()
            cur.execute(sql)
            self.conn.commit()
            self.conn.close()
        """
        cur = self.__GetConnect()
        cur.execute(sql)
        self.conn.commit()
        self.conn.close()

def init_db(db_host, db_name, db_user, db_pwd):
    mysql = MYSQLDB(host=db_host, db=db_name, user=db_user, pwd=db_pwd)
    return mysql

def insert_new_task(mysql):
    try:
        sql = """
        SELECT username
        FROM backend_users
        WHERE username = '%s'
        """ % ('Raniac')
        resList = mysql.ExecQuery(sql)
        for inst in resList:
            print(inst)
        status = 0
    except Exception as e:
        print(e)
        status = 1
    return status

def update_task_result_by_task_id(mysql):
    return ''

def get_data_by_data_name(mysql, data_name):
    try:
        sql = """
        SELECT data_cont
        FROM backend_datasets as datasets
        WHERE datasets.data_name = '%s'
        """ % (data_name)
        fetList = mysql.ExecQuery(sql)
        for inst in fetList:
            print(inst)
            print(type(inst))
    except Exception as e:
        print(e)
    return ''

def get_model_by_model_name(mysql):
    return ''

if __name__ == '__main__':
    mysql = MYSQLDB(host="116.56.138.220", user="root", pwd="root", db="neurolearn")
    resList = mysql.ExecQuery("SELECT username FROM backend_users")
    for inst in resList:
        print(inst)