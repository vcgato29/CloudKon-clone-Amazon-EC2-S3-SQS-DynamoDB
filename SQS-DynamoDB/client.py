
# coding: utf-8

# In[1]:

import Queue
import json
import sys
import threading
import time
import getopt
import boto.sqs
import boto.dynamodb
from boto.sqs.message import Message

def readtask(filename):
    task_queue=Queue.Queue()

    with open(filename) as f:
        task_list=f.readlines()

    for i in task_list:
        task_queue.put(i)
    return task_queue;

def readtaskSQS(filename, queue_name, process_queue):
    aws_conn=boto.sqs.connect_to_region("us-east-1", aws_access_key_id='{aws_access_key_id}', aws_secret_access_key = '{aws_secret_access_key}')
    dynamo_conn = boto.dynamodb.connect_to_region("us-east-1", aws_access_key_id='{aws_access_key_id}', aws_secret_access_key = '{aws_secret_access_key}')
    SQS_queue=aws_conn.get_queue(queue_name)
    SQS_process_queue=aws_conn.get_queue(process_queue)
    task_id = 0;

    try:
        task_table_schema = conn_dynamo.create_schema(hash_key_name='task_id',hash_key_proto_value=str)
        table = conn_dynamo.create_table(name = 'Dynamo_Table', schema = task_table_schema,read_units = 10,write_units = 10)
        print 'Table Dynamo_Table has been created'
    except Exception as e:
        print 'Dynamo_Table already exists.'

    with open(filename) as f:
        task_list=f.readlines()

    for i in task_list:
        msg = Message()
        json_msg = {}
        json_msg["task_id"] = task_id
        json_msg["task"] = i
        msg.set_body(json.dumps(json_msg))
        SQS_queue.write(msg);
        task_id=task_id+1

    return SQS_queue, SQS_process_queue, task_id;


class initializethread(threading.Thread):
    def __init__(self,data):
        threading.Thread.__init__(self);
        self.data=data
        #self.thread = threading.Thread(target=self.run)

    def run(self):
	for i in self.data:
	    task1=i.split(' ')
            task2=task1[0]
            task3=float(task1[1])
        #for i in self.data:
            try:
                ex1 = 'time.'+(task2)+'('+str(float(task3/1000))+')'
                exec ex1
            #exec self.data
            except Exception as e:
                print e;

def processlocalthread(task_queue, no_of_threads):
    threads=[]
    c=0;
    queue_list=[]
    while not task_queue.empty():
	queue_list.append(task_queue.get());

    for a in range(no_of_threads):
        thread=initializethread(queue_list)
        threads.append(thread)
    for xx in threads:
        xx.start();
    for xx in threads:
        xx.join();
    return('Finished successfully')


def main(argv):
    no_of_threads = ''
    is_local = ''
    opts, args = getopt.getopt(argv,"s:t:w:",["is_local=","no_of_threads=","filename="])
    for opt, arg in opts:
        if opt == '-w':
            filename= arg
        elif opt == '-t':
            no_of_threads= int(arg)
        elif opt == '-s':
            is_local= arg

    if(is_local=='LOCAL'):
        print "Start time: ", time.strftime("%H:%M:%S")
	start_time = time.time()
        task_queue=readtask(filename);
        ret_msg=processlocalthread(task_queue, int(no_of_threads))
        print ret_msg
	end_time= time.time()
        print "End time: ", time.strftime("%H:%M:%S")
	print "Total Time Taken : ", end_time-start_time;
    elif(is_local=='MY_QUEUE'):
	print "Start time: ", time.strftime("%H:%M:%S")
        start_time = time.time()
        SQS_queue, SQS_process_queue, no_of_tasks=readtaskSQS(filename, is_local, 'PROCESS_QUEUE');
        while True:
            if(SQS_queue.count()==0):
                process_list = SQS_process_queue.count()
                if(process_list == no_of_tasks):
		    print "End time: ", time.strftime("%H:%M:%S")
                    end_time= time.time()
                    break;
        print "Total Time Taken : ", end_time-start_time;


if __name__ == "__main__":
    main(sys.argv[1:])



# In[ ]:
