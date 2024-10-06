import os
import logging
from celery import Celery
from model import predict_disease
from dotenv import load_dotenv

# Cấu hình logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Tải biến môi trường từ tệp .env
load_dotenv()
os.environ.setdefault('FORKED_BY_MULTIPROCESSING', '1')
# Khởi tạo ứng dụng Celery
app = Celery(
    'tasks',
    broker=os.getenv('CELERY_BROKER_URL'),
    backend=os.getenv('CELERY_RESULT_BACKEND')
)

@app.task
def prediction(image_path: str):
    try:
        logger.info(f"Starting prediction for image: {image_path}")
        
        # Gọi hàm dự đoán
        prediction_result = predict_disease(image_path)
        
        # Kiểm tra xem kết quả dự đoán có hợp lệ không
        if prediction_result is None:
            logger.warning(f"No result returned for image: {image_path}")
            return {"error": "No result returned"}
        
        logger.info(f"Prediction result for {image_path}: {prediction_result}")
        return prediction_result
    
    except Exception as e:
        logger.error(f"Error during prediction for {image_path}: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    img_path = r'D:\Research_ICNLab\ML_Deploy\Images\00d798f7-d21b-41c9-bb08-895cd315f7e6__RS_HL 0317.JPG'
    print(prediction(img_path))
