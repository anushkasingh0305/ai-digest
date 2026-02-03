"""
Scheduled digest runner for AI Digest system.
Uses APScheduler to run digests on a recurring schedule.
"""

import asyncio
import logging
from datetime import datetime, time
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from ..workflows.pipeline import Pipeline
from ..logging_config import get_logger

logger = get_logger(__name__)

# Global scheduler instance
_scheduler: BackgroundScheduler | None = None


def _run_pipeline_sync(deliver: bool = True) -> None:
    """
    Synchronous wrapper to run async pipeline.

    Args:
        deliver: Whether to send digest via email and Telegram.
    """
    try:
        logger.info(
            "Scheduled pipeline run started",
            extra={"deliver": deliver, "component": "scheduler"},
        )
        pipeline = Pipeline()
        asyncio.run(pipeline.run(deliver=deliver))
        logger.info(
            "Scheduled pipeline run completed",
            extra={"component": "scheduler"},
        )
    except Exception as e:
        logger.error(
            f"Scheduled pipeline run failed: {str(e)}",
            extra={"component": "scheduler", "error": str(e)},
            exc_info=True,
        )


def start_scheduler(deliver: bool = True) -> BackgroundScheduler:
    """
    Start the background scheduler.

    Args:
        deliver: Whether to send digests via email and Telegram.

    Returns:
        The started BackgroundScheduler instance.

    Raises:
        RuntimeError: If scheduler is already running.
    """
    global _scheduler

    if _scheduler is not None:
        logger.warning(
            "Scheduler already running, returning existing instance",
            extra={"component": "scheduler"},
        )
        return _scheduler

    logger.info(
        "Starting background scheduler",
        extra={"deliver": deliver, "component": "scheduler"},
    )

    _scheduler = BackgroundScheduler()

    # Schedule daily at 6 AM UTC
    _scheduler.add_job(
        _run_pipeline_sync,
        CronTrigger(hour=6, minute=0),
        args=(deliver,),
        id="daily_digest_6am",
        name="Daily digest at 6 AM UTC",
        replace_existing=True,
    )
    logger.info(
        "Added job: daily digest at 06:00 UTC",
        extra={"job_id": "daily_digest_6am", "component": "scheduler"},
    )

    _scheduler.start()
    logger.info(
        "Scheduler started successfully",
        extra={"component": "scheduler"},
    )

    return _scheduler


def schedule_job(
    job_name: str,
    hour: int = 6,
    minute: int = 0,
    deliver: bool = True,
) -> str:
    """
    Schedule a daily digest job at specific time.

    Args:
        job_name: Unique name for the job (e.g., "digest_morning").
        hour: Hour (0-23) in UTC.
        minute: Minute (0-59).
        deliver: Whether to send digest.

    Returns:
        Job ID for later reference.

    Raises:
        RuntimeError: If scheduler is not running.
    """
    global _scheduler

    if _scheduler is None:
        raise RuntimeError("Scheduler not started. Call start_scheduler() first.")

    job_id = f"digest_{job_name}_{hour:02d}{minute:02d}"

    logger.info(
        f"Scheduling job: {job_name} at {hour:02d}:{minute:02d} UTC",
        extra={
            "job_id": job_id,
            "hour": hour,
            "minute": minute,
            "deliver": deliver,
            "component": "scheduler",
        },
    )

    _scheduler.add_job(
        _run_pipeline_sync,
        CronTrigger(hour=hour, minute=minute),
        args=(deliver,),
        id=job_id,
        name=f"{job_name} at {hour:02d}:{minute:02d} UTC",
        replace_existing=True,
    )

    logger.info(
        f"Job scheduled: {job_id}",
        extra={"job_id": job_id, "component": "scheduler"},
    )

    return job_id


def list_jobs() -> list[dict]:
    """
    List all scheduled jobs.

    Returns:
        List of job information dicts.

    Raises:
        RuntimeError: If scheduler is not running.
    """
    global _scheduler

    if _scheduler is None:
        raise RuntimeError("Scheduler not started.")

    jobs = []
    for job in _scheduler.get_jobs():
        job_info = {
            "id": job.id,
            "name": job.name,
            "next_run_time": (
                job.next_run_time.isoformat()
                if job.next_run_time
                else None
            ),
            "trigger": str(job.trigger),
        }
        jobs.append(job_info)

    logger.debug(
        f"Listed {len(jobs)} scheduled jobs",
        extra={"job_count": len(jobs), "component": "scheduler"},
    )

    return jobs


def pause_job(job_id: str) -> None:
    """
    Pause a scheduled job.

    Args:
        job_id: ID of the job to pause.

    Raises:
        RuntimeError: If scheduler is not running or job not found.
    """
    global _scheduler

    if _scheduler is None:
        raise RuntimeError("Scheduler not started.")

    try:
        _scheduler.pause_job(job_id)
        logger.info(
            f"Job paused: {job_id}",
            extra={"job_id": job_id, "component": "scheduler"},
        )
    except Exception as e:
        logger.error(
            f"Failed to pause job {job_id}: {str(e)}",
            extra={"job_id": job_id, "error": str(e), "component": "scheduler"},
            exc_info=True,
        )
        raise


def resume_job(job_id: str) -> None:
    """
    Resume a paused job.

    Args:
        job_id: ID of the job to resume.

    Raises:
        RuntimeError: If scheduler is not running or job not found.
    """
    global _scheduler

    if _scheduler is None:
        raise RuntimeError("Scheduler not started.")

    try:
        _scheduler.resume_job(job_id)
        logger.info(
            f"Job resumed: {job_id}",
            extra={"job_id": job_id, "component": "scheduler"},
        )
    except Exception as e:
        logger.error(
            f"Failed to resume job {job_id}: {str(e)}",
            extra={"job_id": job_id, "error": str(e), "component": "scheduler"},
            exc_info=True,
        )
        raise


def remove_job(job_id: str) -> None:
    """
    Remove a scheduled job.

    Args:
        job_id: ID of the job to remove.

    Raises:
        RuntimeError: If scheduler is not running or job not found.
    """
    global _scheduler

    if _scheduler is None:
        raise RuntimeError("Scheduler not started.")

    try:
        _scheduler.remove_job(job_id)
        logger.info(
            f"Job removed: {job_id}",
            extra={"job_id": job_id, "component": "scheduler"},
        )
    except Exception as e:
        logger.error(
            f"Failed to remove job {job_id}: {str(e)}",
            extra={"job_id": job_id, "error": str(e), "component": "scheduler"},
            exc_info=True,
        )
        raise


def stop_scheduler() -> None:
    """
    Stop the background scheduler.

    Logs a warning if scheduler is not running.
    """
    global _scheduler

    if _scheduler is None:
        logger.warning(
            "Scheduler not running, nothing to stop",
            extra={"component": "scheduler"},
        )
        return

    try:
        logger.info(
            "Stopping scheduler",
            extra={"component": "scheduler"},
        )
        _scheduler.shutdown(wait=True)
        _scheduler = None
        logger.info(
            "Scheduler stopped",
            extra={"component": "scheduler"},
        )
    except Exception as e:
        logger.error(
            f"Error stopping scheduler: {str(e)}",
            extra={"error": str(e), "component": "scheduler"},
            exc_info=True,
        )
        raise
