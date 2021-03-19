import pymysql
import logging

from src.database.dbconfig import dbconf


class DBUtil:

    # def __init__(self):
    #     # 创建连接
    #     self.conn = pymysql.connect(host=dbconf.host, port=dbconf.port, user=dbconf.user,
    #                            passwd=dbconf.password, db=dbconf.db, charset='utf8')

    def get_conn(self):
        '''连接mysql数据库'''
        try:
            self.conn = pymysql.connect(host=dbconf.host, port=dbconf.port, user=dbconf.user,
                                        passwd=dbconf.password, db=dbconf.db, charset='utf8')
            logging.info("success connect myqsl !")
            print("success")

        except pymysql.Error as e:
            logging.info("connect mysql %s", e)
            logging.info('连接数据库失败')
    def close_conn(self):
        try:
            if self.conn:
                self.conn.close()
        except pymysql.Error as e:
            logging.info("close mysql %s", e)
            logging.info("关闭数据库失败")

    def create_tabel(self,sql):
        self.get_conn()
        cursor = self.conn.cursor()
        try:

            cursor.execute(sql)
        except pymysql.Error as e:
            print(e)
            logging.info("create tabel failed ！")
        finally:
            cursor.close()
            self.conn.close()
    def insert_detection_status(self,img_name,config_str,name,num,vehicle_type,start_date,end_date,issue_date,
                                birth_date,nation,addr,sex,archive_no,success,create_time):

        try:
            logging.info("insert_detection_status !!!")
            self.get_conn()
            cur = self.conn.cursor()
            sql_insert = "insert into recognition_result(image_name,config_str,name,num,vehicle_type,start_date,end_date,issue_date,birth_date,nation,addr,sex,archive_no,success,create_time) values" \
                         "('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}','{10}','{11}','{12}','{13}','{14}')".format(
                img_name, config_str, name, num, vehicle_type, start_date, end_date, issue_date,
                birth_date, nation, addr, sex, archive_no, success, create_time)
            cur.execute(sql_insert)

            # 提交
            self.conn.commit()
            self.close_conn()
        except Exception as e:
            print(e)
            logging.info(" insert mysql err %s", e)
            # 错误回滚
            self.conn.rollback()
            return None

    def insert_image(self,image_name,user,device_id,config_str,create_time):

        try:
            logging.info("insert_image !!!")
            self.get_conn()
            cur = self.conn.cursor()
            sql_insert = "insert into image(image_name,user,device_id,config_str,create_time) values" \
                         "('{0}','{1}','{2}','{3}','{4}')".format(
                image_name,user,device_id,config_str,create_time)
            cur.execute(sql_insert)

            # 提交
            self.conn.commit()
            self.close_conn()
        except Exception as e:
            print(e)
            logging.info(" insert mysql err %s", e)
            # 错误回滚
            self.conn.rollback()
            return None

    def query_children_not_age(self,status):


        try:
            logging.info("Start query children not age ")
            self.get_conn()
            cur = self.conn.cursor()
            sql = "select * from bl_children_detection where status = '{0}'".format(status)
            cur.execute(sql)
            res = cur.fetchall()
            self.close_conn()
            return res
        except Exception as e:
            logging.info(" query mysql err %s", e)
            # 错误回滚
            self.conn.rollback()
            return None


    def update_detection_result(self,age,gender,status,img_name):

        try:
            logging.info("update_detection_result !!!")
            self.get_conn()
            cur = self.conn.cursor()
            sql = "update bl_children_detection set age= '{0}' ,gender = '{1}',status = {2} where img_name = '{3}'".format(
                age, gender, status, img_name)
            cur.execute(sql)
            self.conn.commit()
            self.close_conn()
        except  Exception as e:
            logging.info("update  mysql err %s", e)
            # 错误回滚
            self.conn.rollback()
            return None



if __name__ == '__main__':
    db = dbutil()
    db.update_detection_result("20","99","89bc26ac-ebce-11e9-9b88-001cbff69c70.jpg")
    # print(text)
    # db.insert_detection_status("1234g6d35","15706973759","children","0.99999998","sh001","A1010",'1',"1570699179991")
    # print(db.selectGoodsPrice(1000))
