"""
Queue Management API - Dual-Queue Monitoring and Control

This module provides REST API endpoints for monitoring and controlling the dual-queue system.
Supports real-time status queries, pause/resume operations, and job tracking.

Endpoints:
    GET  /queues/health          - Health check endpoint for load balancers
    GET  /queues/status          - Get status of both queues
    POST /queues/list/pause      - Pause article list collection queue
    POST /queues/list/resume     - Resume article list collection queue
    POST /queues/content/pause   - Pause article content extraction queue
    POST /queues/content/resume  - Resume article content extraction queue
    GET  /queues/jobs            - List all jobs from both queues
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel, Field
from core.queue import GlobalQueueManager
from core.print import print_error, print_info


# Pydantic Response Schemas
class HealthCheckResponse(BaseModel):
    """Health check response model"""
    status: str = Field(..., description="Overall health status (healthy/degraded/unhealthy)")
    timestamp: str = Field(..., description="Health check timestamp (ISO 8601)")
    queues: Dict[str, Dict[str, Any]] = Field(..., description="Queue health status")

    class Config:
        schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": "2026-01-13T15:30:00Z",
                "queues": {
                    "list_queue": {
                        "running": True,
                        "paused": False,
                        "pending_tasks": 15
                    },
                    "content_queue": {
                        "running": True,
                        "paused": False,
                        "pending_tasks": 8
                    }
                }
            }
        }


class QueueStatusResponse(BaseModel):
    """Queue status response model"""
    name: str = Field(..., description="Queue name (list_queue or content_queue)")
    is_paused: bool = Field(..., description="Whether queue is paused")
    is_running: bool = Field(..., description="Whether queue is running")
    pending_tasks: int = Field(..., description="Number of pending tasks in queue")
    tag: str = Field(..., description="Queue tag/label")

    class Config:
        schema_extra = {
            "example": {
                "name": "list_queue",
                "is_paused": False,
                "is_running": True,
                "pending_tasks": 15,
                "tag": "Article List Queue"
            }
        }


class JobStatusResponse(BaseModel):
    """Job status response model"""
    job_id: str = Field(..., description="Unique job identifier")
    status: str = Field(..., description="Job status (queued/running/completed/failed)")
    queue_name: str = Field(..., description="Queue name this job belongs to")
    task_name: str = Field(..., description="Task function name")
    created_at: str = Field(..., description="Job creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")
    progress: int = Field(..., description="Progress percentage (0-100)")
    error: Optional[str] = Field(None, description="Error message if failed")

    class Config:
        schema_extra = {
            "example": {
                "job_id": "job_1705123456789_123456",
                "status": "completed",
                "queue_name": "list_queue",
                "task_name": "do_job",
                "created_at": "2026-01-13T12:00:00",
                "updated_at": "2026-01-13T12:00:05",
                "progress": 100,
                "error": None
            }
        }


# FastAPI Router
router = APIRouter(prefix="/queues", tags=["队列管理"])


@router.get("/health", response_model=HealthCheckResponse, summary="健康检查")
async def health_check():
    """
    队列系统健康检查端点

    用于负载均衡器和监控系统检查服务健康状态

    Returns:
        HealthCheckResponse: 健康状态报告

    Health Status Rules:
        - healthy: 所有队列正常运行
        - degraded: 至少一个队列暂停但系统仍可用
        - unhealthy: 系统故障或无法获取队列状态
    """
    try:
        list_status = GlobalQueueManager.get_list_queue_status()
        content_status = GlobalQueueManager.get_content_queue_status()

        # Determine overall health status
        list_paused = list_status['is_paused']
        content_paused = content_status['is_paused']

        if list_paused and content_paused:
            overall_status = "degraded"  # Both paused but system functional
        elif list_paused or content_paused:
            overall_status = "degraded"  # One queue paused
        else:
            overall_status = "healthy"  # All queues running

        return HealthCheckResponse(
            status=overall_status,
            timestamp=datetime.utcnow().isoformat() + "Z",
            queues={
                "list_queue": {
                    "running": list_status['is_running'],
                    "paused": list_status['is_paused'],
                    "pending_tasks": list_status['pending_tasks']
                },
                "content_queue": {
                    "running": content_status['is_running'],
                    "paused": content_status['is_paused'],
                    "pending_tasks": content_status['pending_tasks']
                }
            }
        )
    except Exception as e:
        print_error(f"Health check failed: {e}")
        # Return unhealthy status instead of raising exception
        # This allows load balancers to detect and handle failures gracefully
        return HealthCheckResponse(
            status="unhealthy",
            timestamp=datetime.utcnow().isoformat() + "Z",
            queues={
                "list_queue": {"running": False, "paused": False, "pending_tasks": 0},
                "content_queue": {"running": False, "paused": False, "pending_tasks": 0}
            }
        )


@router.get("/status", response_model=List[QueueStatusResponse], summary="获取队列状态")
async def get_queue_status():
    """
    获取所有队列的实时状态

    Returns:
        List[QueueStatusResponse]: 包含list_queue和content_queue的状态列表

    Raises:
        HTTPException: 500 if queue status retrieval fails
    """
    try:
        list_status = GlobalQueueManager.get_list_queue_status()
        content_status = GlobalQueueManager.get_content_queue_status()

        return [
            QueueStatusResponse(
                name="list_queue",
                is_paused=list_status['is_paused'],
                is_running=list_status['is_running'],
                pending_tasks=list_status['pending_tasks'],
                tag=list_status['tag']
            ),
            QueueStatusResponse(
                name="content_queue",
                is_paused=content_status['is_paused'],
                is_running=content_status['is_running'],
                pending_tasks=content_status['pending_tasks'],
                tag=content_status['tag']
            )
        ]
    except Exception as e:
        print_error(f"Failed to get queue status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve queue status: {str(e)}")


@router.post("/list/pause", response_model=QueueStatusResponse, summary="暂停文章列表采集队列")
async def pause_list_queue():
    """
    暂停文章列表采集队列

    使用场景:
    - 微信二维码过期时自动触发
    - 手动暂停列表采集
    - 系统维护或调试

    Returns:
        QueueStatusResponse: 暂停后的队列状态

    Raises:
        HTTPException: 500 if pause operation fails
    """
    try:
        GlobalQueueManager.pause_list_queue()
        status = GlobalQueueManager.get_list_queue_status()

        print_info("List queue paused successfully")
        return QueueStatusResponse(
            name="list_queue",
            is_paused=status['is_paused'],
            is_running=status['is_running'],
            pending_tasks=status['pending_tasks'],
            tag=status['tag']
        )
    except Exception as e:
        print_error(f"Failed to pause list queue: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to pause list queue: {str(e)}")


@router.post("/list/resume", response_model=QueueStatusResponse, summary="恢复文章列表采集队列")
async def resume_list_queue():
    """
    恢复文章列表采集队列

    使用场景:
    - 微信登录成功后自动触发
    - 手动恢复列表采集
    - 维护完成后恢复

    Returns:
        QueueStatusResponse: 恢复后的队列状态

    Raises:
        HTTPException: 500 if resume operation fails
    """
    try:
        GlobalQueueManager.resume_list_queue()
        status = GlobalQueueManager.get_list_queue_status()

        print_info("List queue resumed successfully")
        return QueueStatusResponse(
            name="list_queue",
            is_paused=status['is_paused'],
            is_running=status['is_running'],
            pending_tasks=status['pending_tasks'],
            tag=status['tag']
        )
    except Exception as e:
        print_error(f"Failed to resume list queue: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to resume list queue: {str(e)}")


@router.post("/content/pause", response_model=QueueStatusResponse, summary="暂停文章内容提取队列")
async def pause_content_queue():
    """
    暂停文章内容提取队列

    使用场景:
    - 浏览器资源限制
    - 系统负载过高
    - 手动调试

    注意: 内容队列独立于列表队列，通常不需要暂停

    Returns:
        QueueStatusResponse: 暂停后的队列状态

    Raises:
        HTTPException: 500 if pause operation fails
    """
    try:
        GlobalQueueManager.pause_content_queue()
        status = GlobalQueueManager.get_content_queue_status()

        print_info("Content queue paused successfully")
        return QueueStatusResponse(
            name="content_queue",
            is_paused=status['is_paused'],
            is_running=status['is_running'],
            pending_tasks=status['pending_tasks'],
            tag=status['tag']
        )
    except Exception as e:
        print_error(f"Failed to pause content queue: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to pause content queue: {str(e)}")


@router.post("/content/resume", response_model=QueueStatusResponse, summary="恢复文章内容提取队列")
async def resume_content_queue():
    """
    恢复文章内容提取队列

    Returns:
        QueueStatusResponse: 恢复后的队列状态

    Raises:
        HTTPException: 500 if resume operation fails
    """
    try:
        GlobalQueueManager.resume_content_queue()
        status = GlobalQueueManager.get_content_queue_status()

        print_info("Content queue resumed successfully")
        return QueueStatusResponse(
            name="content_queue",
            is_paused=status['is_paused'],
            is_running=status['is_running'],
            pending_tasks=status['pending_tasks'],
            tag=status['tag']
        )
    except Exception as e:
        print_error(f"Failed to resume content queue: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to resume content queue: {str(e)}")


@router.get("/jobs", response_model=List[JobStatusResponse], summary="获取任务列表")
async def get_jobs(
    queue_name: Optional[str] = Query(None, description="队列名称过滤 (list/content/all)", regex="^(list|content|all)?$")
):
    """
    获取所有队列中的任务列表

    Args:
        queue_name: 可选的队列名称过滤器
            - "list": 仅返回列表采集队列的任务
            - "content": 仅返回内容提取队列的任务
            - None 或 "all": 返回所有队列的任务

    Returns:
        List[JobStatusResponse]: 任务状态列表

    Raises:
        HTTPException: 500 if job retrieval fails
    """
    try:
        jobs = []

        # Get jobs from list queue
        if queue_name is None or queue_name == "all" or queue_name == "list":
            list_jobs = GlobalQueueManager.list_queue._jobs
            for job_id, job_data in list_jobs.items():
                jobs.append(JobStatusResponse(
                    job_id=job_id,
                    status=job_data['status'],
                    queue_name="list_queue",
                    task_name=job_data['task_name'],
                    created_at=job_data['created_at'],
                    updated_at=job_data['updated_at'],
                    progress=job_data['progress'],
                    error=job_data.get('error')
                ))

        # Get jobs from content queue
        if queue_name is None or queue_name == "all" or queue_name == "content":
            content_jobs = GlobalQueueManager.content_queue._jobs
            for job_id, job_data in content_jobs.items():
                jobs.append(JobStatusResponse(
                    job_id=job_id,
                    status=job_data['status'],
                    queue_name="content_queue",
                    task_name=job_data['task_name'],
                    created_at=job_data['created_at'],
                    updated_at=job_data['updated_at'],
                    progress=job_data['progress'],
                    error=job_data.get('error')
                ))

        return jobs
    except Exception as e:
        print_error(f"Failed to get jobs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve jobs: {str(e)}")
