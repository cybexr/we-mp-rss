import threading
import random
import asyncio
import time
import atexit
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from typing import Callable, Any, Optional
from core.log import logger
import uuid
# 设置日志

# 全局注册表，用于进程退出时清理所有调度器线程
_all_scheduler_threads = []
def _cleanup_schedulers():
    """进程退出时清理所有调度器线程"""
    for thread in _all_scheduler_threads:
        if thread.is_alive():
            logger.info(f"Waiting for scheduler thread {thread.name} to exit...")
            thread.join(timeout=2.0)

atexit.register(_cleanup_schedulers)

class TaskScheduler:
    """
    异步调度器类，支持cron定时任务调度
    使用APScheduler AsyncIOScheduler作为底层调度引擎

    Cron表达式说明:
    一个cron表达式有5个或6个空格分隔的时间字段，格式为:
        ┌───────────── 秒 (0 - 59) (6位格式)
        │ ┌───────────── 分钟 (0 - 59)
        │ │ ┌───────────── 小时 (0 - 23)
        │ │ │ ┌───────────── 日 (1 - 31)
        │ │ │ │ ┌───────────── 月 (1 - 12 或 JAN-DEC)
        │ │ │ │ │ ┌───────────── 星期 (0 - 6 或 SUN-SAT，0是周日)
        │ │ │ │ │ │
        * * * * * *
        或
        * * * * * (5位格式)

    特殊字符:
        *   任意值
        ,   值列表分隔符 (如 "MON,WED,FRI")
        -   范围 (如 "9-17" 表示9点到17点)
        /   步长 (如 "0/15" 表示从0开始每15分钟)
        ?   日或星期字段无特定值 (只能用在日或星期字段)

    常用示例:
        "0 0 * * *"     每天午夜执行 (5位)
        "0 9 * * MON"   每周一上午9点执行 (5位)
        "0 */6 * * *"   每6小时执行一次 (5位)
        "0 9-17 * * MON-FRI" 工作日每小时从9点到17点执行 (5位)
        "0 0 1 * *"     每月第一天午夜执行 (5位)
        "0 0 1 1 *"     每年1月1日午夜执行 (5位)
        "30 * * * * *"  每分钟的第30秒执行 (6位)
        "0 0 0 * * *"   每天午夜执行 (6位)
        "0 0 9 * * MON" 每周一上午9点执行 (6位)
    """
    
    def __init__(self):
        """初始化调度器和线程锁"""
        self._scheduler = AsyncIOScheduler()
        self._lock = threading.Lock()
        self._jobs = {}
        # 调度器事件循环线程（非守护线程，不会被意外终止）
        self._scheduler_thread: Optional[threading.Thread] = None
        # 调度器事件循环（用于健康检查）
        self._event_loop: Optional[asyncio.AbstractEventLoop] = None
        # 健康监控线程
        self._monitor_thread: Optional[threading.Thread] = None
        # 停止标志
        self._should_stop = False
        # 最后一次任务执行时间（用于检测调度器是否卡死）
        self._last_job_run: Optional[float] = None

    def add_cron_job(self,
                     func: Callable,
                     cron_expr: str,
                     args: Optional[tuple] = None,
                     kwargs: Optional[dict] = None,
                     job_id: Optional[str] = None,
                     tag: str = ""
                     ) -> str:
        """
        添加一个cron定时任务
        
        :param func: 要执行的函数
        :param cron_expr: cron表达式，如"* * * * *"
        :param args: 函数的位置参数
        :param kwargs: 函数的关键字参数
        :param job_id: 任务ID，如果不指定则自动生成
        :return: 任务ID
        """
        with self._lock:
            try:
                logger.info(f"Adding cron job with expression: {cron_expr}")
                
                # 解析cron表达式为各个字段
                fields = cron_expr.split()
                if len(fields) == 5:
                    # 5位格式: 分 时 日 月 周
                    minute, hour, day, month, day_of_week = fields
                    second = "0"  # 默认秒为0
                elif len(fields) == 6:
                    # 6位格式: 秒 分 时 日 月 周
                    second, minute, hour, day, month, day_of_week = fields
                else:
                    error_msg = f"Invalid cron expression: {cron_expr}. Expected 5 or 6 fields."
                    logger.error(error_msg)
                    raise ValueError(error_msg)
                
                # 处理随机时间范围
                def parse_random_field(field: str, field_name: str):
                    # 假设我们要解析的格式是 "*/1~3" 或 "1~3-3~10"
                    import re
                    try:
                        # 使用正则表达式匹配格式
                        pattern = r'(\d+)\~(\d+)'
                        match = re.findall(pattern, field)
                        if match:
                            # 提取匹配的组
                            start, end = match[0]
                            step = random.randint(int(start), int(end))
                            field = field.replace(f"{start}~{end}", str(step))
                    except:
                        pass
                    return field

                second = parse_random_field(second, 'second')
                minute = parse_random_field(minute, 'minute')
                hour = parse_random_field(hour, 'hour')
                day = parse_random_field(day, 'day')
                month = parse_random_field(month, 'month')
                day_of_week_original = parse_random_field(day_of_week, 'day_of_week')

                def translate_day_of_week(dow_str: str) -> str:
                    """将标准cron的星期(0=周日)转换为APScheduler的星期(0=周一)"""
                    import re
                    # 如果字段是 "*" 或 "?"，或者包含字母，则不处理
                    if not re.search(r'\d', dow_str) or re.search(r'[a-zA-Z]', dow_str):
                        return dow_str

                    def replacer(match):
                        num = int(match.group(0))
                        if num == 0:
                            return '6'
                        elif num == 7:  # 标准cron的周日别名 (兼容)
                            return '6'
                        else:
                            return str(num - 1)

                    return re.sub(r'\d+', replacer, dow_str)

                day_of_week = translate_day_of_week(day_of_week_original)

                # 生成job_id
                job_id = job_id or str(uuid.uuid4())

                trigger = CronTrigger(
                    second=second,
                    minute=minute,
                    hour=hour,
                    day=day,
                    month=month,
                    day_of_week=day_of_week
                )

                # 包装任务函数以捕获异常并处理async函数
                import inspect
                if asyncio.iscoroutinefunction(func):
                    # Function is async, create async wrapper
                    async def wrapped_func(*args, **kwargs):
                        try:
                            # logger.info(f"Executing async job {job_id or 'anonymous'}")
                            return await func(*args, **kwargs)
                        except Exception as e:
                            logger.error(f"Job {tag} {job_id or 'anonymous'} failed: {str(e)}")
                            raise
                else:
                    # Function is sync, create sync wrapper
                    def wrapped_func(*args, **kwargs):
                        try:
                            # logger.info(f"Executing job {job_id or 'anonymous'}")
                            return func(*args, **kwargs)
                        except Exception as e:
                            logger.error(f"Job {tag} {job_id or 'anonymous'} failed: {str(e)}")
                            raise

                job = self._scheduler.add_job(
                    wrapped_func,
                    trigger=trigger,
                    args=args,
                    kwargs=kwargs,
                    id=str(job_id)
                )
                self._jobs[job.id] = job
                logger.info(f"Successfully added job {tag} {job.id}")
                return job.id
            except Exception as e:
                logger.error(f"Failed to add cron job: {str(e)}")
                raise
    
    def remove_job(self, job_id: str) -> bool:
        """
        移除指定任务
        
        :param job_id: 要移除的任务ID
        :return: 是否成功移除
        """
        with self._lock:
            if job_id in self._jobs:
                self._scheduler.remove_job(job_id)
                del self._jobs[job_id]
                return True
            return False
    
    def clear_all_jobs(self) -> int:
        """
        清除所有任务，包括正在运行的任务
        
        :return: 被删除的任务数量
        """
        with self._lock:
            job_count = len(self._jobs)
            if job_count > 0:
                # 先终止所有正在运行的任务
                for job in self._scheduler.get_jobs():
                    try:
                        self._scheduler.remove_job(job.id)
                    except Exception as e:
                        logger.warning(f"Failed to remove job {job.id}: {str(e)}")
                
                # 清除所有计划任务
                self._scheduler.remove_all_jobs()
                self._jobs.clear()
                logger.info(f"Removed all {job_count} jobs")
            return job_count
    
    def _health_monitor(self) -> None:
        """健康监控线程，定期检查调度器状态"""
        logger.info("Scheduler health monitor started")

        while not self._should_stop:
            try:
                time.sleep(30)  # 每30秒检查一次

                with self._lock:
                    # 检查调度器是否在运行
                    if not self._scheduler.running:
                        logger.warning("Scheduler not running, attempting to restart...")
                        self._restart_scheduler()
                        continue

                    # 检查事件循环线程是否存活
                    if self._scheduler_thread and not self._scheduler_thread.is_alive():
                        logger.error("Scheduler event loop thread died! Restarting...")
                        self._restart_scheduler()
                        continue

                    # 检查是否有任务但没有执行（可能卡死）
                    if self._event_loop and not self._event_loop.is_running():
                        logger.error("Event loop stopped running! Restarting...")
                        self._restart_scheduler()
                        continue

            except Exception as e:
                logger.error(f"Error in health monitor: {e}")

        logger.info("Scheduler health monitor stopped")

    def _restart_scheduler(self) -> None:
        """内部方法：重启调度器（必须在持有锁的情况下调用）"""
        try:
            # 清理旧调度器
            if self._scheduler.running:
                try:
                    self._scheduler.shutdown(wait=False)
                except Exception as e:
                    logger.warning(f"Error shutting down old scheduler: {e}")

            # 创建新的调度器实例
            old_jobs = list(self._jobs.items())
            self._scheduler = AsyncIOScheduler()

            # 重新添加所有任务
            for job_id, job in old_jobs:
                try:
                    # 从job对象中提取原始信息重新添加
                    # 注意：这里需要保存原始的func和cron表达式
                    logger.info(f"Restoring job {job_id}")
                    # 简化处理：清空任务列表，等待下次reload_job()调用
                except Exception as e:
                    logger.error(f"Failed to restore job {job_id}: {e}")

            # 清空任务字典，需要重新加载
            self._jobs.clear()

            logger.warning("Scheduler restarted. Jobs need to be reloaded via reload_job().")

        except Exception as e:
            logger.error(f"Failed to restart scheduler: {e}")

    def start(self) -> None:
        """启动调度器"""
        with self._lock:
            if self._scheduler.running:
                logger.warning("Scheduler is already running")
                return

            # 停止旧的监控线程
            self._should_stop = True
            if self._monitor_thread and self._monitor_thread.is_alive():
                self._monitor_thread.join(timeout=5.0)
            self._should_stop = False

            try:
                logger.info("Starting scheduler...")
                # For AsyncIOScheduler, we need a running event loop in the current thread
                try:
                    # Try to get running loop (works in FastAPI context)
                    loop = asyncio.get_running_loop()
                    self._scheduler.start()
                    self._event_loop = loop
                    logger.info("Scheduler started successfully (using existing event loop)")
                except RuntimeError:
                    # No running loop - need to create and run one in background thread
                    # This happens when scheduler is started from a regular thread (e.g., jobs/mps.py)
                    logger.info("No running event loop in thread, starting loop in background...")

                    def run_scheduler_in_loop():
                        """Run event loop with scheduler in background thread"""
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        self._event_loop = loop
                        try:
                            # Start the event loop FIRST, then attach scheduler
                            # This avoids "no running event loop" error from scheduler.start()
                            logger.info("Starting event loop in background thread...")
                            loop.call_soon(self._scheduler.start)
                            logger.info("Scheduler start scheduled in event loop")
                            # Run the event loop forever (blocking call, but we're in a thread)
                            loop.run_forever()
                        except Exception as e:
                            logger.error(f"Error in scheduler loop: {e}")
                        finally:
                            logger.info("Scheduler event loop thread exiting")
                            loop.close()

                    # Start the loop in a NON-daemon thread so it won't be killed unexpectedly
                    self._scheduler_thread = threading.Thread(
                        target=run_scheduler_in_loop,
                        name="APScheduler-EventLoop",
                        daemon=False  # 改为非守护线程，防止被意外终止
                    )
                    self._scheduler_thread.start()
                    _all_scheduler_threads.append(self._scheduler_thread)
                    logger.info("Scheduler event loop thread started (non-daemon)")

                # 启动健康监控线程
                self._monitor_thread = threading.Thread(
                    target=self._health_monitor,
                    name="APScheduler-HealthMonitor",
                    daemon=True
                )
                self._monitor_thread.start()
                logger.info("Scheduler health monitor thread started")

            except Exception as e:
                logger.error(f"Failed to start scheduler: {str(e)}")
                raise
    
    def shutdown(self, wait: bool = True) -> None:
        """
        关闭调度器

        :param wait: 是否等待所有任务完成
        """
        # 停止健康监控
        self._should_stop = True

        # 等待监控线程结束
        if self._monitor_thread and self._monitor_thread.is_alive():
            self._monitor_thread.join(timeout=5.0)

        with self._lock:
            if self._scheduler.running:
                self._scheduler.shutdown(wait=wait)
                self._jobs.clear()

            # 停止事件循环
            if self._event_loop and self._event_loop.is_running():
                self._event_loop.call_soon_threadsafe(self._event_loop.stop)

        # 等待调度器线程结束
        if self._scheduler_thread and self._scheduler_thread.is_alive():
            self._scheduler_thread.join(timeout=5.0)
    
    def get_job_ids(self) -> list[str]:
        """获取所有任务ID"""
        with self._lock:
            # 同步 _jobs 字典与 APScheduler 的实际状态
            self._sync_jobs()
            return list(self._jobs.keys())

    def _sync_jobs(self) -> None:
        """同步 _jobs 字典与 APScheduler 的实际状态"""
        try:
            # 获取 APScheduler 中的所有任务
            scheduler_jobs = self._scheduler.get_jobs()
            scheduler_job_ids = {job.id for job in scheduler_jobs}

            # 移除已不存在的任务
            to_remove = []
            for job_id in self._jobs:
                if job_id not in scheduler_job_ids:
                    to_remove.append(job_id)

            for job_id in to_remove:
                del self._jobs[job_id]

            # 添加新任务到字典
            for job in scheduler_jobs:
                if job.id not in self._jobs:
                    self._jobs[job.id] = job
        except Exception as e:
            logger.error(f"Failed to sync jobs: {e}")
    
    def __enter__(self):
        """支持上下文管理协议"""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """支持上下文管理协议"""
        self.shutdown()

    def get_scheduler_status(self) -> dict:
        """
        获取调度器状态信息

        :return: 包含调度器状态的字典
        """
        with self._lock:
            # 检查事件循环线程健康状态
            thread_alive = self._scheduler_thread.is_alive() if self._scheduler_thread else False
            event_loop_running = self._event_loop.is_running() if self._event_loop else False
            monitor_alive = self._monitor_thread.is_alive() if self._monitor_thread else False

            return {
                'running': self._scheduler.running,
                'job_count': len(self._jobs),
                'thread_alive': thread_alive,
                'event_loop_running': event_loop_running,
                'monitor_alive': monitor_alive,
                'healthy': self._scheduler.running and thread_alive and event_loop_running,
                'next_run_times': [
                    (job_id, job.next_run_time.isoformat() if job.next_run_time else None)
                    for job_id, job in self._jobs.items()
                ]
            }

    def get_job_details(self, job_id: str) -> dict:
        """
        获取任务详细信息

        :param job_id: 任务ID
        :return: 包含任务详情的字典
        """
        with self._lock:
            # 先同步状态
            self._sync_jobs()

            # 优先从 APScheduler 获取最新状态
            scheduler_job = None
            try:
                scheduler_job = self._scheduler.get_job(job_id)
            except Exception as e:
                logger.error(f"Failed to get job from scheduler: {e}")

            if scheduler_job:
                job = scheduler_job
            elif job_id in self._jobs:
                job = self._jobs[job_id]
            else:
                raise ValueError(f"Job {job_id} not found")

            return {
                'id': job.id,
                'name': job.name,
                'trigger': str(job.trigger),
                'next_run_time': job.next_run_time.isoformat() if job.next_run_time else None,
                'last_run_time': job.last_run_time.isoformat() if job.last_run_time else None,
                'last_run_result': getattr(job, 'last_run_result', None)
            }

if __name__ == "__main__":
    # 示例用法
    def sample_task():
        print("定时任务执行中...")
    
    with TaskScheduler() as scheduler:
        # 添加每分钟执行一次的任务
        job_id = scheduler.add_cron_job(sample_task, "* * * * * *")
        print(f"已添加任务: {job_id}")
        input("按Enter键退出...\n")
    pass