from celery import Celery

celery_app = Celery(
    "myapp",
    broker="redis://localhost:6379/0",  # Sử dụng tên container
    backend="redis://localhost:6379/0"  # Sử dụng tên container
)
