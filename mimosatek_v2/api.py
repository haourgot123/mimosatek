from celery.result import AsyncResult
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from celery_config import celery, prediction
import os
import uvicorn



app = FastAPI()


@app.post('/upload')
async def upload(file: UploadFile = File(...)):
    file_path = f"statics/temp_{file.filename}"
    with open(file_path, "wb") as buffer:
        # Lưu tệp hình ảnh vào thư mục
        buffer.write(await file.read())
    
    task = prediction.apply_async(args = [file_path])
    return {"task_id": task.id}

@app.get('/result/{task_id}')
async def get_result(task_id:str):
    res = celery.AsyncResult(task_id)
    result = ''
    if res.ready():
        result = res.result
    else:
        result = 'Running'
    return {
        'result': result
    }

if __name__ == "__main__":
    uvicorn.run('api:app', host="0.0.0.0", port=1712, reload=True)