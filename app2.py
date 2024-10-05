import uvicorn
import numpy as np
from PIL import Image
import tflite_runtime.interpreter as tflite
from fastapi import FastAPI, File, UploadFile, Request, HTTPException
from fastapi.responses import JSONResponse
# from fastapi.staticfiles import StaticFiles
# from starlette.requests import Request
import shutil
import os
import requests
from langchain.chains import LLMChain
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain_core.messages import SystemMessage
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain_groq import ChatGroq
from pydantic import BaseModel
# import jwt
os.environ['GROQ_API_KEY'] = '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'
# Thông tin payload của JWT
payload = {
    "user_id": 123,
    "username": "exampleuser",
    "zone/area": "examplearea"
}

disease_id = ['BS6', 'EB1', 'FW9', 'GM11', 'HT12', 'LB2', 'MV7', 'PM4', 'SL5', 'TS3',  'VW10', 'YL8']

# Mã hóa JWT
secret_key = "ifjarihq875469kyvestamvlw23d3"
# token = jwt.encode(payload, secret_key, algorithm="HS256")

app = FastAPI()
model_path = "models/model.tflite"

# Load model TFLite
interpreter = tflite.Interpreter(model_path=model_path)
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Khai báo thư mục tĩnh để lưu trữ ảnh đã upload
# app.mount("/static", StaticFiles(directory="static"), name="static")


@app.post("/upload")
async def upload(request: Request, file: UploadFile = File(...)):
    headers = request.headers
    print(headers)
    # try:
    #     # Giải mã JWT
    #     decoded_payload = jwt.decode(headers, secret_key, algorithms=["HS256"])
    # except jwt.ExpiredSignatureError:
    #     print("Token đã hết hạn")
    # except jwt.InvalidTokenError:
    #     print("Token không hợp lệ")
    # userID = decoded_payload #headers.get("userID")
        
     # Validate input
    if not file.filename.endswith((".jpg", ".jpeg", ".png", ".JPG", ".JPEG", ".PNG")):
        raise HTTPException(status_code=400, detail="Invalid file format")

    if file.size > 10 * 1024 * 1024:  # 10MB
        raise HTTPException(status_code=413, detail="File size exceeds limit")

    # # Lưu file vào thư mục 'static'
    with open(f"static/{file.filename}", "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Đường dẫn file ảnh
    image_path = f"static/{file.filename}"
    
    # Xử lý ảnh với model TFLite
    input_shape = input_details[0]['shape']
    try:
        img = Image.open(image_path).resize((input_shape[1], input_shape[2]))
        img = img.convert("RGB")
        img_array = np.array(img).astype(np.uint8)
        img_array = np.expand_dims(img_array, axis=0).astype(input_details[0]['dtype'])
        
        interpreter.set_tensor(input_details[0]['index'], img_array)
        interpreter.invoke()
        output_data = interpreter.get_tensor(output_details[0]['index'])

    except Exception as x:
        return JSONResponse(status_code=500, content={"message": "Internal Server Error"})
    
    # Kết quả xử lý
    result = (np.array(output_data[0]))
    
    # Trong phương thức post upload
    # Tính argmax của biến result
    argmax_result = np.argmax(result)
    confedence = (result[argmax_result])
    # Chuyển kết quả argmax thành int
    argmax_result_int = int(argmax_result)
    result_json = disease_id[argmax_result_int] if confedence > 0.6 else "Unknown"

    return JSONResponse(status_code=200, content={"result": result_json, 
                                                  "confidence":str(confedence) ,
                                                  "image_path": image_path,
                                                  "user_id": payload["user_id"],
                                                  "username": payload["username"],
                                                  "zone_area": payload["zone/area"]})
class UserInput(BaseModel):
    message: str
conversational_memory_length = 50
memory = ConversationBufferWindowMemory(k=conversational_memory_length, memory_key="chat_history", return_messages=True)
@app.post('/chatbot')
async def chatbot(user_input: UserInput):
    groq_api_key = os.environ['GROQ_API_KEY']
    model = 'llama3-8b-8192'
    groq_chat = ChatGroq(
        groq_api_key = groq_api_key,
        model_name = model,
        temperature = 0
    )
    system_prompt = 'Xin chào, Tôi có thể giúp gì cho bạn ?'
    if user_input.message:
        prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessage(
                    content = system_prompt
                ),
                MessagesPlaceholder(
                    variable_name="chat_history"
                ),
                HumanMessagePromptTemplate.from_template(
                    "{human_input}"
                ),
            ]
        )
        conversation = LLMChain(
            llm= groq_chat,
            prompt = prompt,
            verbose = False,
            memory = memory
        )
        respone = conversation.predict(human_input=user_input.message)
        return respone


if __name__ == "__main__":
    uvicorn.run('app2:app', host="0.0.0.0", port=1712, reload=True)
# , ssl_keyfile='path/to/keyfile', ssl_certfile='path/to/certfile'