from apscheduler.schedulers.asyncio import AsyncIOScheduler
from src.app import enrichment_service
import asyncio

scheduler = AsyncIOScheduler()

@scheduler.scheduled_job('cron', hour=2)
async def daily_job():
    await enrichment_service.process_daily_batch()

if __name__ == "__main__":
    scheduler.start()
    try:
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        pass
