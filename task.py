import os
import logging
from celery import Celery
from model import predict_disease
from dotenv import load_dotenv


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
load_dotenv()
app = Celery('tasks',
             broker=os.getenv('CELERY_BROKER_URL'),
             backend=os.getenv('CELERY_RESULT_BACKEND'))


@app.task
def prediction(image_path: str):
    logger.info(f"Received image path: {image_path}")

    if not os.path.exists(image_path):
        return {"error": f"Image path {image_path} does not exist"}

    try:
        # Gọi hàm dự đoán
        prediction_result = predict_disease(image_path)
        if prediction_result is None:
            return {"error": "No result returned"}
        return prediction_result
    except Exception as e:
        logger.error(f"Error during prediction: {e}")
        return {"error": str(e)}
