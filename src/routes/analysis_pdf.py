# Libs
from flask import Blueprint, jsonify, request
from datetime import datetime
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import json, base64, requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from requests.auth import HTTPBasicAuth
from src.helpers.Decorators import require_appkey
from config import s3,brck_u,brck_p


# define the blueprint
blueprint_analysis = Blueprint(name="blueprint_analysis", import_name=__name__)
 

# add view function to the blueprint

@require_appkey
@blueprint_analysis.route('/generate',methods=['POST'])
def serasa():
    start_time=datetime.utcnow()
    input=request.json.get('path')
    url,message,status_code=main_execution(input)
    output_dict={}
    output_dict['elapsed_time']=(datetime.utcnow()-start_time).total_seconds()*1000
    output_dict['message']=message
    if status_code==201:
        output_dict['valid']=True
        output_dict['object_url']=url
    else:
        output_dict['valid']=False
        output_dict['object_url']=None
    return jsonify(output_dict),status_code



def main_execution(path):
    if len(path.split('/'))!=6:
        return None,'INVALID_PATH',400
    basepath='/'.join(path.split('/')[:-1])
    token=login_brick()

    if not token:
        return None,'LOGIN_ERROR',403
    
    driver=get_driver()
    if not driver:
        return None,'DRIVER_ERROR',500
    try:
        driver.get('https://www.app.brickseguros.com.br/kguoiutiyrutdyhgjgkhioyiut')
        driver.delete_all_cookies()
        driver.add_cookie({'name':'brick.token','value': token})
        driver.get(path)
        calculated_print_options = {
        'landscape': False,
        'displayHeaderFooter': False,
        'printBackground': True,
            'preferCSSPageSize': True,
        }
        element=WebDriverWait(driver,10000).until(EC.presence_of_element_located((By.XPATH, '//*[@id="root"]/main/div/div/section')))
        driver.get(f'{basepath}/pdf-completo/')
        element=WebDriverWait(driver,10000).until(EC.presence_of_element_located((By.XPATH, '//*[@id="root"]/main/div/div/div[3]/div[1]')))
        result = send_devtools(driver, "Page.printToPDF", calculated_print_options)
        driver.quit()
    except Exception as e:
        print(e)
        driver.quit()
        return None,'EXTRACTION_ERROR',500
    
    buff=base64.b64decode(result['data'])
    filename=f'AnalysisPdf/{path.split("/")[-1]}.pdf'
    bucket_name = 'pre-booked'
    try:
        url=upload_to_s3(buff,bucket_name,filename)
    except Exception as e:
        print(e)
        return None,'UPLOAD_ERROR',500
    

    return url,'OK',201



def send_devtools(driver, cmd, params={}):
  resource = "/session/%s/chromium/send_command_and_get_result" % driver.session_id
  url = driver.command_executor._url + resource
  body = json.dumps({'cmd': cmd, 'params': params})
  response = driver.command_executor._request('POST', url, body)
  if response.get('status'):
    raise Exception(response.get('value'))
  return response.get('value')

def get_driver():
    try:
        webdriver_options = Options()
        webdriver_options.add_argument("--enable-javascript")
        webdriver_options.add_argument("--headless")
        webdriver_options.add_argument("--no-sandbox")
        webdriver_options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(options=webdriver_options)
        #driver.set_window_size(1920, 1080, driver.window_handles[0])
        return driver
    except:
       return None

def login_brick():
  try:
    response=requests.get('https://api.brickseguros.com.br/auth',auth=HTTPBasicAuth(brck_u, brck_p),timeout=2)
  except:
    return None
  return response.json()['content']['token']

def upload_to_s3(buff,bucket_name,file_name_with_extention):
    obj = s3.Object(bucket_name,file_name_with_extention)
    obj.put(Body=buff)
    #get bucket location
    #get object url
    object_url = f'https://{bucket_name}.s3.us-east-2.amazonaws.com/{file_name_with_extention}'
    return object_url
