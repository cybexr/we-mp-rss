import queue
import threading
import time
import gc
import asyncio
import inspect
from typing import Callable, Any, Optional, Dict
from datetime import datetime
from enum import Enum
from core.print import print_error, print_info, print_warning, print_success

class JobStatus(str, Enum):
    """Job status enumeration"""
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class TaskQueueManager:
    """任务队列管理器，用于管理和执行排队任务，支持任务状态追踪"""

    def __init__(self,maxsize=0,tag:str=""):
        """初始化任务队列"""
        self._queue = queue.Queue(maxsize=maxsize)
        self._lock = threading.Lock()
        self._is_running = False
        self.tag = tag
        self._jobs: Dict[str, Dict[str, Any]] = {}  # Job storage with status tracking
        
    def add_task(self, task: Callable[..., Any], *args: Any, job_id: Optional[str] = None, **kwargs: Any) -> str:
        """添加任务到队列并返回任务ID

        Args:
            task: 要执行的任务函数
            *args: 任务函数的参数
            job_id: 可选的任务ID，如不提供则自动生成
            **kwargs: 任务函数的关键字参数

        Returns:
            str: 任务ID，用于后续查询任务状态
        """
        # Generate job_id if not provided
        if job_id is None:
            job_id = f"job_{int(time.time() * 1000)}_{id(task)}"

        # Initialize job record
        with self._lock:
            self._jobs[job_id] = {
                'status': JobStatus.QUEUED,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'task_name': task.__name__ if hasattr(task, '__name__') else str(task),
                'error': None,
                'progress': 0
            }
            self._queue.put((job_id, task, args, kwargs))
        print_success(f"{self.tag}队列任务添加成功 - Job ID: {job_id}\n")
        return job_id
    def run_task_background(self)->None:
        threading.Thread(target=self.run_tasks, daemon=True).start()  
        print_warning("队列任务后台运行")
    def run_tasks(self, timeout: float = 1.0) -> None:
        """执行队列中的所有任务，并持续运行以接收新任务

        Args:
            timeout: 等待新任务的超时时间(秒)
        """
        with self._lock:
            if self._is_running:
                return
            self._is_running = True

        try:
            while self._is_running:
                time.sleep(0.1)  # 避免过于频繁的任务获取
                try:
                    # 阻塞获取任务，避免CPU空转
                    job_id, task, args, kwargs = self._queue.get(timeout=timeout)

                    # Update job status to RUNNING
                    with self._lock:
                        if job_id in self._jobs:
                            self._jobs[job_id]['status'] = JobStatus.RUNNING
                            self._jobs[job_id]['updated_at'] = datetime.now().isoformat()

                    try:
                        # 记录任务开始时间
                        start_time = time.time()

                        # Check if the task is an async function
                        if inspect.iscoroutinefunction(task):
                            # Run async function in a new event loop
                            try:
                                loop = asyncio.get_event_loop()
                                if loop.is_closed():
                                    raise RuntimeError("Event loop is closed")
                            except RuntimeError:
                                # Create new event loop if none exists or it's closed
                                loop = asyncio.new_event_loop()
                                asyncio.set_event_loop(loop)

                            # Run the async function
                            loop.run_until_complete(task(*args, **kwargs))
                        else:
                            # Run synchronous function normally
                            task(*args, **kwargs)

                        # 记录任务执行时间
                        duration = time.time() - start_time
                        print_info(f"\n任务执行完成，耗时: {duration:.2f}秒")

                        # Update job status to COMPLETED
                        with self._lock:
                            if job_id in self._jobs:
                                self._jobs[job_id]['status'] = JobStatus.COMPLETED
                                self._jobs[job_id]['updated_at'] = datetime.now().isoformat()
                                self._jobs[job_id]['progress'] = 100

                    except Exception as e:
                        print_error(f"队列任务执行失败: {e}")
                        # Update job status to FAILED
                        with self._lock:
                            if job_id in self._jobs:
                                self._jobs[job_id]['status'] = JobStatus.FAILED
                                self._jobs[job_id]['updated_at'] = datetime.now().isoformat()
                                self._jobs[job_id]['error'] = str(e)
                        # raise
                    finally:
                        # 确保任务完成标记和资源释放
                        self._queue.task_done()
                        # 强制垃圾回收
                        gc.collect()

                except queue.Empty:
                    # 超时无任务，继续检查运行状态
                    continue

        finally:
            # 确保停止状态设置和资源清理
            with self._lock:
                self._is_running = False
            # 清理可能残留的资源
            gc.collect()
    
    def stop(self) -> None:
        """停止任务执行"""
        with self._lock:
            self._is_running = False
    
    def get_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        获取指定任务的状态信息

        Args:
            job_id: 任务ID

        Returns:
            dict: 包含任务状态的字典，如果任务不存在则返回None
                - job_id: 任务ID
                - status: 任务状态 (queued/running/completed/failed)
                - created_at: 任务创建时间
                - updated_at: 任务更新时间
                - task_name: 任务名称
                - error: 错误信息（仅失败时有值）
                - progress: 进度百分比 (0-100)
        """
        with self._lock:
            return self._jobs.get(job_id)

    def get_queue_info(self) -> dict:
        """
        获取队列的当前状态信息

        返回:
            dict: 包含队列信息的字典，包括:
                - is_running: 队列是否正在运行
                - pending_tasks: 等待执行的任务数量
        """
        with self._lock:
            return {
                'is_running': self._is_running,
                'pending_tasks': self._queue.qsize()
            }
            
    def clear_queue(self) -> None:
        """清空队列中的所有任务"""
        with self._lock:
            while not self._queue.empty():
                try:
                    self._queue.get_nowait()
                    self._queue.task_done()
                except queue.Empty:
                    break
            print_success("队列已清空")
            
    def delete_queue(self) -> None:
        """删除队列(停止并清空所有任务)"""
        with self._lock:
            self._is_running = False
            while not self._queue.empty():
                try:
                    self._queue.get_nowait()
                    self._queue.task_done()
                except queue.Empty:
                    break
            print_success("队列已删除")
TaskQueue = TaskQueueManager(tag="默认队列")
TaskQueue.run_task_background()
if __name__ == "__main__":
    def task1():
        print("执行任务1")

    def task2(name):
        print(f"执行任务2，参数: {name}")

    manager = TaskQueueManager()
    manager.add_task(task1)
    manager.add_task(task2, "测试任务")
    manager.run_tasks()  # 按顺序执行任务1和任务2