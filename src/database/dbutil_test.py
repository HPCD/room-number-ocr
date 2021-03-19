#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""
@author:abner
@file:dbutil_test.py
@ datetime:2020/7/23 10:53
@software: PyCharm

"""
from src.database.dbutil import DBUtil


def demo():
    table_info = {'addr': '河南省商水县魏乡镇处集村工二组',
                  'birth_date': '19781201',
                  'config_str': '{"side":null}',
                  'end_date': '20240130',
                  'issue_date': '20080130',
                  'name': '孙玉',
                  'nation': '中国',
                  'num': '412723197812016820',
                  'request_id': '20200723112425_e79bae39e127546373d8816a4373b078',
                  'sex': '男',
                  'start_date': '20140130',
                  'success': True,
                  'vehicle_type': 'A2'}
    addr = table_info['addr']
    birth_date = table_info['birth_date']
    config_str = 1
    end_date = table_info['end_date']
    issue_date = table_info['issue_date']
    name = table_info['name']
    num = table_info['num']
    sex = table_info['sex']
    nation = table_info['nation']
    start_date = table_info['start_date']
    success = table_info['success']
    vehicle_type = table_info['vehicle_type']
    import uuid
    img_name = str(uuid.uuid1())
    archive_no = '1233'
    import datetime
    now = datetime.datetime.now()
    create_time = now.strftime("%Y-%m-%d %H:%M:%S")
    # db.insert_detection_status(img_name,config_str,name,num,vehicle_type,start_date,end_date,issue_date,
    #                             birth_date,nation,addr,sex,archive_no,success,create_time)
    image_path = str(uuid.uuid1()) + ".jpg"
    user = "abner"
    device_id = "atp23k000320"
    config_str = 2


if __name__ == '__main__':
    db = DBUtil()
    # db.get_conn()
    sql = '''
        create table image( 
        id int primary key AUTO_INCREMENT,
        image_name varchar(50),
        user varchar(100),
        device_id varchar(12),
        
        create_time timestamp
        )

    '''
    sql_result_tabel = '''
    create table recognition_result(
    image_name varchar(50) not null,
    config_str char(1),
    name varchar(100),
    num char(18),
    vehicle_type char(4),
    start_date char(10),
    end_date char(10),
    issue_date char(10),
    birth_date  char(10),
    nation char(8),
    addr char(20),
    sex char(2),
    archive_no varchar(100),
    success char(4),
    create_time timestamp
    )
    '''
    db.create_tabel(sql)
    db.create_tabel(sql_result_tabel)

    # db.insert_image(image_path,user,device_id,config_str,create_time)