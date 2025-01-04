from dotenv import load_dotenv
import os
import requests
from requests.auth import HTTPBasicAuth
import json
import time

def simulation_data(regular: str,
                    instrumentType: str = 'EQUITY', # ['EQUITY']
                    region: str = 'USA', # ['USA']
                    universe: str = 'TOP3000', # ['TOP3000', 'TOP1000', 'TOP500', 'TOP200', 'TOPSP500']
                    delay: int = 1,
                    decay: int = 0,
                    neutralization: str = 'INDUSTRY', # ['NONE', 'MARKET', 'SECTOR', 'INDUSTRY', 'SUBINDUSTRY']
                    truncation: float = 0.01,
                    pasteurization: str = 'ON', # ['ON', 'OFF']
                    unitHandling: str = 'VERIFY', # ['VERIFY']
                    nanHandling: str = 'OFF', # ['ON', 'OFF']
                    visualization: bool = False,
                    ) -> dict:
    """准备模拟数据的函数。

    Args:
        regular (str): 定期表达式或数据处理规则。
        instrumentType (str, optional): 金融工具类型。Defaults to 'EQUITY'.
        region (str, optional): 地区。Defaults to 'USA'.
        universe (str, optional): 股票范围。Defaults to 'TOP3000'.
        delay (int, optional): 延迟。Defaults to 1.
        decay (int, optional): 衰退。Defaults to 0.
        neutralization (str, optional): 中性化方式。Defaults to 'INDUSTRY'.
        truncation (float, optional): 截断。Defaults to 0.01.
        pasteurization (str, optional): 巴氏杀菌。Defaults to 'ON'.
        unitHandling (str, optional): 单位处理。Defaults to 'VERIFY'.
        nanHandling (str, optional): NaN处理。Defaults to 'OFF'.
        visualization (bool, optional): 可视化。Defaults to False.

    Returns:
        dict: 包含模拟数据设置的字典。
    """
    return{
        'type': 'REGULAR', 
        'settings':{
            'instrumentType': instrumentType,
            'region': region,
            'universe': universe,
            'delay': delay,
            'decay': decay,
            'neutralization': neutralization,
            'truncation': truncation,
            'pasteurization': pasteurization,
            'unitHandling': unitHandling,
            'nanHandling': nanHandling,
            'language': 'FASTEXPR', 
            'visualization': visualization,
        }, 
        'regular': regular
        }


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
        """
        登录方法，用于用户身份验证。
        
        该方法通过POST请求向服务器发送用户邮箱和密码信息，
        以获取登录状态。如果登录成功，将返回一个会话对象，
        用于后续的API调用。
        
        Returns:
            requests.Session: 登录成功的会话对象，用于后续操作。
            
        Raises:
            AssertionError: 如果登录失败，抛出断言错误，包含错误的响应状态码。
        """
        # 创建一个会话对象，用于管理整个会话的cookies、headers等信息
        sess = requests.Session()
        # 设置会话的认证信息，使用HTTP基础认证
        sess.auth = HTTPBasicAuth(self.email, self.password)
        # 发送POST请求到认证URL，尝试登录
        response = sess.post(self.url+'authentication')
        # 断言登录状态码为201，否则抛出异常，提示登录失败
        assert (response.status_code == 201), f"Login failed, status code: {response.status_code}"
        # 打印登录响应的JSON数据，用于调试或日志记录
        print(response.json())
        # 返回登录成功的会话对象
        return sess
    
    # 2. 模拟
    def simulate(self, data: dict) -> dict:
        """启动一个模拟进程。

        Args:
            data (dict): 包含模拟所需数据的字典。

        Returns:
            dict: 模拟结果的JSON响应。
        """
        # 发起模拟请求
        response = self.sess.post(self.url+'simulations', json=data)
        # 检查HTTP响应状态码是否为201（已创建）
        assert (response.status_code == 201), f"Error, status code: {response.status_code}"
        # 获取模拟进程的状态URL
        sim_progress_url = response.headers['Location']
        # 循环检查模拟进程状态直到完成
        while True:
            response = self.sess.get(sim_progress_url)
            retry_after_sec = float(response.headers.get('Retry-After', 0))
            if retry_after_sec == 0:
                break
            time.sleep(retry_after_sec)
        # 返回模拟结果
        return response.json()

    # 3. 查询alpha信息
    def get_alpha_info(self, alpha_id):
        response = self.sess.get(self.url+'alphas/' + alpha_id + '/recordsets/yearly-stats')
        return response, response.headers, response.json()

