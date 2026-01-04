from .token import set_token
from core.print import print_warning,print_success
#判断是否是有效登录

# 初始化全局变量
WX_LOGIN_ED = True
WX_LOGIN_INFO = None

import asyncio

# 初始化异步锁
login_lock = asyncio.Lock()

async def setStatus(status:bool):
    global WX_LOGIN_ED
    async with login_lock:
        WX_LOGIN_ED=status
async def getStatus():
    global WX_LOGIN_ED
    async with login_lock:
        return WX_LOGIN_ED
async def getLoginInfo():
    global WX_LOGIN_INFO
    async with login_lock:
        return WX_LOGIN_INFO
async def setLoginInfo(info):
    global WX_LOGIN_INFO
    async with login_lock:
        WX_LOGIN_INFO=info
def Success_Msg(data:dict,ext_data:dict={}):
    from jobs.notice import sys_notice
    from core.config import cfg
    text="# 授权成功\n"
    text+=f"- 服务名：{cfg.get('server.name','')}\n"
    text+=f"- 名称：{ext_data['wx_app_name']}\n"
    text+=f"- Token: {data['token']}\n"
    text+=f"- 有效时间: {data['expiry']['expiry_time']}\n"

    sys_notice(text, str(cfg.get("server.code_title","WeRss授权完成")))
async def Success(data:dict,ext_data:dict={}):
    if data != None:
            # print("\n登录结果:")
            await setLoginInfo(data)
            if ext_data is not {}:
                print_success(f"名称：{ext_data['wx_app_name']}")
            if data['expiry'] !=None:
                Success_Msg(data,ext_data)
                print_success(f"有效时间: {data['expiry']['expiry_time']} (剩余秒数: {data['expiry']['remaining_seconds']}) Token: {data['token']}")
                set_token(data,ext_data)
                await setStatus(True)
            else:
                print_warning("登录失败，请检查上述错误信息")
                await setStatus(False)

    else:
            print("\n登录失败，请检查上述错误信息")
            await setStatus(False)