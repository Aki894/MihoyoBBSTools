import config
import tools
import time
import os
from loghelper import log
from request import http

token = '' # 设置环境变量“ttocr_token”
points = -1


def game_captcha(gt: str, challenge: str):
    response = geetest(gt, challenge, 'https://passport-api.mihoyo.com/account/ma-cn-passport/app/loginByPassword')
    # 失败返回None 成功返回validate
    if response is None:
        # return response
        time.sleep(5)
        response = geetest(gt, challenge, 'https://passport-api.mihoyo.com/account/ma-cn-passport/app/loginByPassword')
        if response is None:
            return response
    return response['validate']


def bbs_captcha(gt: str, challenge: str):
    response = geetest(gt, challenge, "https://webstatic.mihoyo.com/bbs/event/signin-ys/index.html?bbs_auth_required=true&act_id=e202009291139501&utm_source=bbs&utm_medium=mys&utm_campaign=icon")
    # 失败返回None 成功返回validate
    if response is None:
        # return response
        time.sleep(5)
        response = geetest(gt, challenge, "https://webstatic.mihoyo.com/bbs/event/signin-ys/index.html?bbs_auth_required=true&act_id=e202009291139501&utm_source=bbs&utm_medium=mys&utm_campaign=icon")
        if response is None:
            return response
    return response['validate']

# 提交识别
def geetest(gt: str, challenge: str, referer: str):
    global points
    if points == -1:
        points = get_points()
    points = int(points)  # 确保points是整数类型
    if points < 10:
        log.warning("点数不足，无法识别")
        return None
    # 构建请求数据，确保所有必要参数都被包括
    data = {
        'appkey': token,
        'gt': gt,
        'challenge': challenge,
        'itemid': 388,
        # 'referer': referer  # 可选
    }
    response = http.post('http://api.ttocr.com/api/recognize', data=data, timeout=60000)
    r = response.json()
    if r['status'] != 1:
        log.warning(f"提交错误：[{r['status']}]{r['msg']}")  # 打码失败输出错误信息
        return None
    else:
        log.info("提交成功，正在查询结果...")
        time.sleep(5)
        result_data = get_result(r['resultid'])  # 查询结果
        attempts = 0  # 初始化尝试次数
        while result_data['status'] == 2 and attempts < 20:
            log.info("识别中，请稍等...")
            time.sleep(5)
            result_data = get_result(r['resultid'])
            attempts += 1  # 增加尝试次数
        if result_data['status'] == 1:
            log.info("查询结果成功，识别成功")  # 成功输出识别结果
        else:
            log.warning(f"识别失败：[{result_data['status']}]{result_data['msg']}")  # 失败输出错误信息
            return None
        return result_data['data']  # 失败返回None 成功返回data，包含validate

# 查询结果
def get_result(resultid: str):
    # 构建请求数据，确保所有必要参数都被包括
    data = {
        'appkey': token,
        'resultid': resultid,
    }
    response = http.post('http://api.ttocr.com/api/results', data=data, timeout=10000)
    data = response.json()
    # if data['status'] != 1:
    #     log.warning(f"查询结果错误：[{data['status']}]{data['msg']}")  # 打码失败输出错误信息
    # if data['status'] == 1:
    #     log.info("查询结果成功，识别成功")  # 成功输出识别结果
    return data


# 查询用户点数
def get_points():
    global token
    if os.getenv("ttocr_token") is not None:
        token = os.getenv("ttocr_token")
    response = http.get('http://api.ttocr.com/api/points', params={
        'appkey': token,
    }, timeout=10000)
    data = response.json()
    if data['status'] != 1:
        log.warning(f"点数查询错误：{data['status']}{data['msg']}")  # 打码失败输出错误信息
        return None
    else:
        log.info(f"当前ttocr点数: {data['points']}")  # 成功输出点数信息
        global points
        points = int(data['points'])
        return data['points']
