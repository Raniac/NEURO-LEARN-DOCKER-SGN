from flask import Flask, request, jsonify
from celery import Celery
import argparse
import json
import time

from dao.db import *
from sgn import core

app = Flask(__name__)
app.config['CELERY_BROKER_URL'] = 'redis://127.0.0.1:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://127.0.0.1:6379/0'
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

global DB

## Loggers
# app.logger.debug('A value for debugging')
# app.logger.info('An info for notice')
# app.logger.warning('A warning occurred (%d apples)', 42)
# app.logger.error('An error occurred')

@app.route('/')
def intro():
    intro_cont = '''
    NEURO-LEARN-DOCKER-SGN(NLD-SGN) is a dockerized application programming
    interface developed with Flask, allowing users to run Schizo_Graph_Net 
    models via the user interface provided by NEURO-LEARN-WEB.
    '''
    return intro_cont

@app.route('/api/v0/new_task', methods=['POST'])
def new_task():
    response_content = {}

    try:
        task_form = json.loads(request.data.decode("utf-8"))
        proj_id = task_form['proj_id']
        task_type = task_form['task_type']

        counter = 0
        task_id = 'TASK' + time.strftime('%y%m%d%H%M%S') + '{:02d}'.format(counter)
        app.logger.info('Creating task: %s' % task_id)

        task_name = task_form['task_name']
        task_config = {}
        task_config['proj_name'] = task_form['proj_name']
        task_config['train_data'] = task_form['train_data']
        task_config['val_data'] = task_form['val_data']
        task_config['enable_test'] = task_form['enable_test']
        task_config['test_data'] = task_form['test_data']
        task_config['model'] = task_form['model']
        task_config['param_set'] = task_form['param_set']

        status = insert_new_task(
            mysql=DB,
            task_id=task_id,
            proj_id=proj_id,
            task_name=task_name,
            task_type=task_type,
            task_config=task_config,
            task_status='Submitted'
            )
        if status == 1:
            raise Exception('Database Error!')
        app.logger.info('Task %s created! Waiting for execution...' % task_id)

        task_executor.delay(
            taskid = task_id,
            tasktype = task_form['task_type'],
            traindata = task_config['train_data'],
            valdata = task_config['val_data'],
            enabletest = task_config['enable_test'],
            testdata = task_config['test_data'],
            model = task_config['model'],
            paramset = task_config['param_set']
        )

        response_content['task_form'] = task_form
        response_content['msg'] = 'success'
        response_content['code'] = 200

    except Exception as e:
        response_content['msg'] = str(e)
        response_content['code'] = 500

    return jsonify(response_content)

@app.route('/api/v0/test_db', methods=['GET'])
def test_db():
    try:
        fetched = get_data_by_data_name(DB, 'A_181210_140_SZ_sfMRI_AAL90')
        app.logger.debug(len(fetched))
        return 'success'
    except Exception as e:
        return str(e)

@celery.task
def task_executor(taskid, tasktype, traindata, valdata, enabletest, testdata, model, paramset):
    DB = init_db(db_host='120.79.49.129', db_name='neurolearn', db_user='neurolearn', db_pwd='nl4444_')
    ## TODO add DAO for data acquisition
    # fetched_train_data = []
    # for train_data_name in traindata:
    #     fetched_train_data.append(get_data_by_data_name(DB, train_data_name))
    
    # fetched_val_data = []
    # for val_data_name in valdata:
    #     fetched_val_data.append(get_data_by_data_name(DB, val_data_name))
    
    # fetched_model = get_model_by_model_name(DB, model)
    
    # fetched_test_data = []
    # if enable_test:
    #     for test_data_name in testdata:
    #         fetched_test_data.append(get_data_by_data_name(DB, test_data_name))
    
    core.run_model(taskid, tasktype, fetched_traind_ata, fetched_val_data, enabletest, fetched_test_data, fetched_model, paramset)
    return

def parse_arg():
    parser = argparse.ArgumentParser(description='nld-sgn-main')
    parser.add_argument('--host', dest='host', default='0.0.0.0')
    parser.add_argument('--port', dest='port', default='80')
    parser.add_argument('--db_host', dest='db_host', default='120.79.49.129')
    parser.add_argument('--db_name', dest='db_name', default='neurolearn')
    parser.add_argument('--db_user', dest='db_user', default='neurolearn')
    parser.add_argument('--db_pwd', dest='db_pwd', default='nl4444_')
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = parse_arg()
    HOST = args.host
    PORT = int(args.port)
    DB_HOST = args.db_host
    DB_NAME = args.db_name
    DB_USER = args.db_user
    DB_PWD = args.db_pwd
    DB = init_db(db_host=DB_HOST, db_name=DB_NAME, db_user=DB_USER, db_pwd=DB_PWD)
    app.run(host=HOST, port=PORT, debug=True)