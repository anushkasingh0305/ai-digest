import argparse
import asyncio
import os
import signal
import sys
from ..workflows.pipeline import Pipeline
from ..logging_config import setup_logging, get_logger
from ..services.scheduler import (
    start_scheduler,
    schedule_job,
    list_jobs,
    stop_scheduler,
)

logger = get_logger(__name__)


async def _main(args):
    """Run the pipeline with optional delivery."""
    try:
        logger.info(
            "Starting CLI main",
            extra={"deliver": args.deliver, "component": "cli"},
        )
        pipeline = Pipeline()
        await pipeline.run(deliver=args.deliver)
        logger.info("CLI execution completed successfully", extra={"component": "cli"})
    except Exception as e:
        logger.error(
            f"CLI execution failed: {str(e)}",
            extra={"component": "cli", "error": str(e)},
            exc_info=True,
        )
        raise


def main():
    """Parse arguments and run pipeline or scheduler."""
    parser = argparse.ArgumentParser(description="AI Digest System")
    parser.add_argument(
        "--deliver",
        action="store_true",
        help="Send digest via email and Telegram",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging level (default: INFO)",
    )
    parser.add_argument(
        "--log-file",
        default="logs/ai_digest.log",
        help="Path to log file (default: logs/ai_digest.log)",
    )
    parser.add_argument(
        "--schedule",
        action="store_true",
        help="Run in scheduled mode (continuous background)",
    )
    parser.add_argument(
        "--hour",
        type=int,
        default=6,
        help="Hour for daily digest (0-23, UTC). Default: 6",
    )
    parser.add_argument(
        "--minute",
        type=int,
        default=0,
        help="Minute for daily digest (0-59). Default: 0",
    )
    args = parser.parse_args()

    # Validate time arguments
    if args.hour < 0 or args.hour > 23:
        parser.error("--hour must be 0-23")
    if args.minute < 0 or args.minute > 59:
        parser.error("--minute must be 0-59")

    # Initialize logging
    setup_logging(log_level=args.log_level, log_file=args.log_file)
    logger.info(
        "Logging initialized",
        extra={"log_level": args.log_level, "log_file": args.log_file},
    )

    if args.schedule:
        # Scheduled mode
        logger.info(
            f"Starting in scheduled mode - digest at {args.hour:02d}:{args.minute:02d} UTC",
            extra={
                "mode": "scheduled",
                "hour": args.hour,
                "minute": args.minute,
                "deliver": args.deliver,
                "component": "cli",
            },
        )

        try:
            scheduler = start_scheduler(deliver=args.deliver)
            
            # Override default job with custom time
            if args.hour != 6 or args.minute != 0:
                scheduler.remove_job("daily_digest_6am")
                schedule_job("daily", hour=args.hour, minute=args.minute, deliver=args.deliver)

            logger.info(
                "Scheduler started, listing jobs",
                extra={"component": "cli"},
            )
            
            # List scheduled jobs
            jobs = list_jobs()
            for job in jobs:
                logger.info(
                    f"Scheduled: {job['name']}",
                    extra={
                        "job_id": job["id"],
                        "next_run": job["next_run_time"],
                        "component": "cli",
                    },
                )

            print(f"\nScheduler running (delivering: {args.deliver})")
            print(f"Scheduled jobs: {len(jobs)}")
            for job in jobs:
                print(f"  - {job['name']} (next: {job['next_run_time']})")
            print("\nPress Ctrl+C to stop\n")

            # Handle graceful shutdown
            def signal_handler(sig, frame):
                logger.info(
                    "Interrupt signal received, shutting down scheduler",
                    extra={"component": "cli"},
                )
                stop_scheduler()
                print("\nScheduler stopped.")
                sys.exit(0)

            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)

            # Keep the main thread alive
            while True:
                asyncio.run(asyncio.sleep(1))

        except Exception as e:
            logger.error(
                f"Scheduler mode failed: {str(e)}",
                extra={"component": "cli", "error": str(e)},
                exc_info=True,
            )
            raise

    else:
        # One-time run mode
        asyncio.run(_main(args))


if __name__ == "__main__":
    main()
