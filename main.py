from celery.result import AsyncResult
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import task

app = FastAPI()


@app.get("/")
def home():
    return {"Home page"}


@app.post("/predict/")
async def create_task(file: UploadFile = File(...)):
    file_path = f"./temp_{file.filename}"
    task_result = task.prediction.delay(file_path)
    return {"task_id": task_result.id}


@app.get("/result/{task_id}")
async def get_result(task_id: str):
    # Tạo đối tượng AsyncResult từ task_id
    result = AsyncResult(task_id)
    # Kiểm tra trạng thái của tác vụ
    if result.ready():
        # Nếu tác vụ đã hoàn thành, trả về kết quả
        return {"task_id": task_id, "result": result.result}
    else:
        # Nếu tác vụ chưa hoàn thành, trả về trạng thái
        return JSONResponse(status_code=202, content={"task_id": task_id, "status": "pending"})
