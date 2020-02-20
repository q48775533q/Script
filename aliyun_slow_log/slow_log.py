#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
aliiyun RDS slow API
"""
import datetime
import json
import csv
import os
import sys
import MyMail


reload(sys)
sys.setdefaultencoding('utf8')
from aliyunsdkcore.client import AcsClient
from aliyunsdkrds.request.v20140815.DescribeSlowLogRecordsRequest import DescribeSlowLogRecordsRequest
from aliyunsdkrds.request.v20140815.DescribeDBInstancesRequest import DescribeDBInstancesRequest









class Connection(object):
    """
    aliyun account init
    """
    def __init__(self,aliyun_access_key,aliyun_access_secret,aliyun_region):

        aliyun_access_key = aliyun_access_key
        aliyun_access_secret = aliyun_access_secret
        self.aliyun_region=aliyun_region
        self._connection = AcsClient(aliyun_access_key, aliyun_access_secret,aliyun_region)



    def get_db_instances(self, page_size=30, page_number=1):
        """
        :param aliyun_region:
        :param page_size:
        :param page_number:
        :return: db instances
        """
        request = DescribeDBInstancesRequest()
        request.set_accept_format('json')
        # request.add_query_param('RegionId', aliyun_region)
        request.add_query_param('PageSize', page_size)
        request.add_query_param('PageNumber', page_number)
        try:
            response = self._connection.do_action_with_exception(request)
            instance_dict = json.loads(response)
        except Exception as e:
            print(e)


        instances = list()
        for instance in instance_dict['Items']['DBInstance']:
            instance = (instance['DBInstanceId'], instance['DBInstanceDescription'], instance['RegionId'])
            instances.append(instance)
        return instances

    def get_slow_logs(self, db_instance_id,send_mail=None,endtime=None,day=1,page_number=1):
        db_instance_id=db_instance_id
        request = DescribeSlowLogRecordsRequest()
        request.set_accept_format('json')
        request.set_DBInstanceId(db_instance_id)
        if endtime == None:
            Endtime = datetime.datetime.now()
        else:
            endtime=endtime
            Endtime=datetime.datetime.strptime(endtime,'%Y-%m-%d')

        days = datetime.timedelta(days=int(day))
        starttime = Endtime - days
        Endtime= Endtime.strftime('%Y-%m-%d')
        Starttime = starttime.strftime('%Y-%m-%d')
        request.set_StartTime(Starttime +'T00:00Z')
        request.set_EndTime(Endtime +'T00:00Z')


        # request.set_DBName(page_size)
        request.set_PageSize(100)

        slow_logs = list()
        val=1
        page_number = 1
        while val==1:
            request.set_PageNumber(page_number)
            try:
                response = self._connection.do_action_with_exception(request)
            except Exception as e:
                print(e)
                return e

            slow_log_dict = json.loads(response,encoding='utf-8')


            for slow_log in slow_log_dict['Items']['SQLSlowRecord']:
                slow_log = (
                    slow_log['DBName'],
                    slow_log['ExecutionStartTime'],
                    slow_log['LockTimes'],
                    slow_log['ParseRowCounts'],
                    slow_log['ReturnRowCounts'],
                    slow_log['SQLText'],

                )
                a = str(slow_log[5])

                if "SELECT /*!40001 SQL_NO_CACHE */ * FROM" not in a:
                    slow_logs.append(slow_log)

            if slow_log_dict.get('PageRecordCount', 0) == 0:
                val = 2
            else:
                page_number += 1


        if slow_logs:
            #write slow log to csvfile
            if not os.path.exists('slowfile'):
                os.makedirs('slowfile')
            attachment_file='slowfile/'+ 'slowlog_'+ Endtime +'.csv'
            csvfile = open(attachment_file, 'wb')  # 打开方式还可以使用file对象
            writer = csv.writer(csvfile)
            writer.writerow(['Databases', 'ExecutionStartTime', 'LockTimes','ParseRowCounts', 'ReturnRowCounts', 'SQLText'])
            data=[]
            for val in slow_logs:
                data.append(val)

            writer.writerows(data)
            csvfile.close()

            #send email
            if send_mail == "None":
                pass
            else:
                mail=MyMail.MyMail(to_addr=send_mail)
                mail.Send_slowlog_mail(attachment=attachment_file)
        else:
            print("slow log is null")

        return slow_logs







