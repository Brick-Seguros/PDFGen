import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import json, base64, requests
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from requests.auth import HTTPBasicAuth


def send_devtools(driver, cmd, params={}):
  resource = "/session/%s/chromium/send_command_and_get_result" % driver.session_id
  url = driver.command_executor._url + resource
  body = json.dumps({'cmd': cmd, 'params': params})
  response = driver.command_executor._request('POST', url, body)
  if response.get('status'):
    raise Exception(response.get('value'))
  return response.get('value')

def get_driver():
  webdriver_options = Options()
  webdriver_options.add_argument("--enable-javascript")
  webdriver_options.add_argument("--headless")
  webdriver_options.add_argument("--no-sandbox")
  webdriver_options.add_argument("--disable-dev-shm-usage")
  driver = webdriver.Chrome(options=webdriver_options)
  #driver.set_window_size(1920, 1080, driver.window_handles[0])
  return driver

def login_brick():
  try:
    response=requests.get('https://api.brickseguros.com.br/auth',auth=HTTPBasicAuth('carlos@brickseguros.com.br', 'senhadonada'),timeout=2)
  except:
    raise Exception('Could not login')
  print('Logged in')
  return response.json()['content']['token']

def get_pdf_from_html(path):
  basepath='/'.join(path.split('/')[:-1])
  token=login_brick()
  driver=get_driver()
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
  print('foundelement')
  driver.get(f'{basepath}/pdf-completo/')
  element=WebDriverWait(driver,10000).until(EC.presence_of_element_located((By.XPATH, '//*[@id="root"]/main/div/div/div[3]/div[1]')))
  print('foundelement2')
  result = send_devtools(driver, "Page.printToPDF", calculated_print_options)
  driver.quit()

  return base64.b64decode(result['data'])

if __name__=='__main__':
     print(len('https://www.app.brickseguros.com.br/analise-cadastral/pj/f2951e49-6edd-4b0c-84d9-2820ca6c4f1e'.split('/')))
     with open('test.pdf', 'wb') as f:
          f.write(get_pdf_from_html('https://www.app.brickseguros.com.br/analise-cadastral/pj/f2951e49-6edd-4b0c-84d9-2820ca6c4f1e'))


import os

if __name__=='__main__':
  print(os.environ['TSTVAR'])