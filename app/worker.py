from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

celery_app.conf.task_routes = {
    "app.modules.ai_orchestrator.tasks.*": {"queue": "ai_queue"},
    "app.modules.finance.tasks.*": {"queue": "finance_queue"},
}

@celery_app.task
def test_task(word: str):
    return f"Hello {word} from Celery!"
