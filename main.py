# main.py
from fastapi import FastAPI, Query
from add import add_cal  # Nhập hàm add từ file math_operations.py

# Khởi tạo ứng dụng FastAPI
app = FastAPI()

# Định nghĩa phương thức cộng
@app.post("/add")
async def add_numbers(a: float = Query(...), b: float = Query(...)):
    result = add_cal(a, b)  # Sử dụng hàm add từ math_operations
    return {"result": result}  # Trả về kết quả
