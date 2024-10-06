import os
import shutil
from celery.result import AsyncResult
from fastapi import FastAPI, UploadFile, File, HTTPException
from task import predict

app = FastAPI()


@app.get("/")
def home():
    return {"Home page"}


@app.post("/predict")
async def create_task(file: UploadFile = File(...)):
    file_path = f"./temp_{file.filename}"
    # Lưu file được tải lên vào đường dẫn đã chỉ định
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    # Gửi tác vụ dự đoán tới Celery
    task = predict.delay(file_path)
    os.remove(file_path)
    # Trả về ID tác vụ cho client
    return {"task_id": task.id}


@app.get("/task_status/{task_id}")
def get_task_status(task_id: str):
    task_result = AsyncResult(task_id)

    # Kiểm tra trạng thái của tác vụ
    if task_result.state == "PENDING":
        return {"status": "Đang xử lý"}
    elif task_result.state == "SUCCESS":
        return {"status": "Thành công", "result": task_result.result}
    elif task_result.state == "FAILURE":
        return {"status": "Thất bại", "result": str(task_result.result)}
    else:
        return {"status": task_result.state}
