from celery.result import AsyncResult
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import task
import os
import uvicorn


app = FastAPI()


@app.get("/")
def home():
    return {"Home page"}


@app.post("/predict/")
async def create_task(file: UploadFile = File(...)):
    file_path = f"./temp_{file.filename}"
    with open(file_path, "wb") as buffer:
        # Lưu tệp hình ảnh vào thư mục
        buffer.write(await file.read())
    
    task_result = task.prediction.delay(file_path)
    return {"task_id": task_result.id}



@app.get("/result/{task_id}")
async def get_result(task_id: str):
    res = AsyncResult(task_id)
    if res.ready():
        results = res.result
        return {"task_id": task_id, "result":results}
    else:
        return "Vui lòng ấn reload"



if __name__ == "__main__":
    uvicorn.run("app:main", host="127.0.0.1", port=8000, log_level="info")