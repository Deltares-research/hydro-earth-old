import time
import datetime
import subprocess

from celery import Celery
from pymongo import MongoClient

TASK_DIR = '../web-site/public/results'
BROKER_URL = 'mongodb://localhost:81/meteor'
app = Celery('tasks', broker=BROKER_URL)

app.config_from_object('celery-config')

basinFusionTableId = {
  3: '13dShZ5yGqCEqk3dsJvYEL3lsa1hEmpMRldxK7aSa',
  4: '1FxGTqGlr_XTSOL8r1zp-PIOCO3S3_6i2gI-KQeQZ',
  5: '1IHRHUiWkgPXOzwNweeM89CzPYSfokjLlz7_0OTQl'
}

models = MongoClient(BROKER_URL).meteor.models

@app.task
def exportModel(resolution, basinLevel, basinId, name):
    cmd = u'./run_wtools.sh {0} {1} {2} {3}'.format(resolution, basinFusionTableId[basinLevel], basinId, name)

    print('Starting: ' + cmd)

    result=subprocess.check_call(cmd, shell=True)

    url = 'http://23.251.128.159:8080/results/' + name + '.zip'
    
    # add model record to the Models collection
    model = {
        'modelType': 'wflow',
        'options': { 'basinLevel': basinLevel, 'basinId': basinId },
        'createdAt': datetime.datetime.utcnow(),
        'name': name
    }
    models.insert(model)

    return url
