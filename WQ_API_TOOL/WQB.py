from dotenv import load_dotenv
import os
import requests
from requests.auth import HTTPBasicAuth
import json
import time




class WQB:
    def __init__(self):
        # 加载 .env 文件
        load_dotenv()

        # 获取环境变量
        self.email = os.getenv("EMAIL")
        self.password = os.getenv("PASSWORD")
        self.url = os.getenv("URL")

        # 登录
        self.sess = self.login()

    # 1. 登录
    def login(self):
        sess = requests.Session()
        sess.auth = HTTPBasicAuth(self.email, self.password)
        response = sess.post(self.url+'authentication')
        assert (response.status_code == 201), f"Login failed, status code: {response.status_code}"
        print(response.json())
        return sess
    
    # 2. 模拟
    def simulate(self, data):
        response = self.sess.post(self.url+'simulations', json=data)
        assert (response.status_code == 201), f"Error, status code: {response.status_code}"
        sim_progress_url = response.headers['Location']
        while True:
            response = self.sess.get(sim_progress_url)
            retry_after_sec = float(response.headers.get('Retry-After', 0))
            if retry_after_sec == 0:
                break
            time.sleep(retry_after_sec)
        alpha_id = response.json()['alpha'] if response.json()['status'] == 'COMPLETE' else None
        return alpha_id, response.json()
        
    # 3. 查询alpha信息
    def get_alpha_info(self, alpha_id):
        response = self.sess.get(self.url+'alphas/' + alpha_id + '/recordsets/yearly-stats')
        return response, response.headers, response.json()

