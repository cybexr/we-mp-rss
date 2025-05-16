import schedule, time
import core.wx as wx 
import core.db as db
import core.config as cfg
import core.notice as notice
import random
import core.log as log

logger=log.logger

# 初始化数据库
wx_db=db.Db()    
wx_db.init(cfg.get("db"))


# 获取公众号列表
mps=wx_db.get_all_mps()
def do_job():
    print("开始更新")
    all_count=0
    text=f" **时间**：{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}\n"
    for item in mps:

        # 成功更新数量计数
        mps_count=0
        faker_id=item.faker_id
        mp_id=item.id
        print(f'正在更新公众号：{item.mp_name}({item.id})')
        if not cfg.DEBUG:
            # 获取对应公众号列表
            data=wx.get_list(faker_id,mp_id,0)
            for art in data:
                # 添加到数据库
                if  wx_db.add_article(art):
                    mps_count=mps_count+1
        else:
            print("调试模式，不进行更新")

        logger.info(f"{item.mp_name} 更新结束,共更新{mps_count}")
        text+=f"* **{item.mp_name}**({mps_count})\n"
        all_count=all_count+mps_count

        # 随机休眠 防止被封锁
        if not cfg.DEBUG:
            time.sleep(random.randint(2,60))
    logger.info(f"所有公众号更新完成,共更新{all_count}条数据")
    text+=f"\n所有公众号更新完成,共更新{all_count}条数据"
    send_notice(text,cfg.get('app_name',default='we-mp-rss'))
def start():
    schedule.every(10).seconds.do(do_job)  # 每10秒执行
    # schedule.every.day.at("08:00").do(job)  # 每天8点执行
    while True:
        schedule.run_pending()
        time.sleep(1)

def send_notice(text:str="",title:str=""):
    markdown_text = f"""### {title} 通知
    {text}
    """

    webhook=cfg.get('notice')['dingding']
    notice.send_dingtalk_markdown(webhook, title, markdown_text)

if __name__ == '__main__':
    do_job()