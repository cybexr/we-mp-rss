"""
Scheduler Management API - APScheduler Job Monitoring

This module provides REST API endpoints for monitoring and managing
the APScheduler-based task scheduling system.

Endpoints:
    GET  /scheduler/jobs   - Get all scheduled jobs with their details
    GET  /scheduler/status - Get scheduler running status and job count
"""

from typing import List, Dict, Any
from datetime import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from core.task import GlobalScheduler
from core.print import print_error, print_info
from apis.base import success_response, error_response


# Pydantic Response Schemas
class SchedulerJobInfo(BaseModel):
    """Single scheduler job information model"""
    id: str = Field(..., description="Unique job identifier")
    name: str = Field(..., description="Job name (typically the function name)")
    trigger: str = Field(..., description="Trigger expression (cron format)")
    next_run_time: str = Field(None, description="Next scheduled run time (ISO 8601)")
    last_run_time: str = Field(None, description="Last execution time (ISO 8601)")
    status: str = Field(..., description="Job status (active/paused)")

    class Config:
        schema_extra = {
            "example": {
                "id": "job_1234567890",
                "name": "fetch_articles",
                "trigger": "cron[hour='*/6', minute='0']",
                "next_run_time": "2026-01-22T12:00:00+08:00",
                "last_run_time": "2026-01-22T06:00:00+08:00",
                "status": "active"
            }
        }


class SchedulerStatusResponse(BaseModel):
    """Scheduler status response model"""
    running: bool = Field(..., description="Whether the scheduler is running")
    job_count: int = Field(..., description="Total number of scheduled jobs")

    class Config:
        schema_extra = {
            "example": {
                "running": True,
                "job_count": 5
            }
        }


# FastAPI Router
router = APIRouter(prefix="/scheduler", tags=["调度器管理"])


@router.get("/jobs", summary="获取所有调度任务")
async def get_scheduler_jobs():
    """
    获取调度器中所有任务的详细信息

    Returns:
        Dict with code, message, and data containing List[SchedulerJobInfo]

    Raises:
        HTTPException: 500 if job retrieval fails
    """
    try:
        # Get scheduler status which contains job information
        status = GlobalScheduler.get_scheduler_status()
        jobs: List[SchedulerJobInfo] = []

        # Get details for each job
        for job_id in GlobalScheduler.get_job_ids():
            try:
                job_detail = GlobalScheduler.get_job_details(job_id)

                # Determine job status based on next run time
                job_status = "active" if job_detail.get('next_run_time') else "paused"

                jobs.append(SchedulerJobInfo(
                    id=job_detail['id'],
                    name=job_detail['name'],
                    trigger=job_detail['trigger'],
                    next_run_time=job_detail.get('next_run_time') or "",
                    last_run_time=job_detail.get('last_run_time') or "",
                    status=job_status
                ))
            except Exception as e:
                # Skip individual job errors but log them
                print_error(f"Failed to get details for job {job_id}: {e}")
                continue

        print_info(f"Retrieved {len(jobs)} scheduler jobs")
        return success_response(data=jobs, message=f"Retrieved {len(jobs)} jobs")

    except Exception as e:
        print_error(f"Failed to get scheduler jobs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve scheduler jobs: {str(e)}")


@router.get("/status", summary="获取调度器状态")
async def get_scheduler_status():
    """
    获取调度器运行状态

    Returns:
        Dict with code, message, and data containing SchedulerStatusResponse

    Raises:
        HTTPException: 500 if status retrieval fails
    """
    try:
        status = GlobalScheduler.get_scheduler_status()

        status_data = SchedulerStatusResponse(
            running=status['running'],
            job_count=status['job_count']
        )
        return success_response(data=status_data, message="Scheduler status retrieved")

    except Exception as e:
        print_error(f"Failed to get scheduler status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve scheduler status: {str(e)}")
