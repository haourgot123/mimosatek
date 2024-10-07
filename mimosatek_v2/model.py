import numpy as np
from PIL import Image
import tflite_runtime.interpreter as tflite
import config

# Tải mô hình TFLite
interpreter = tflite.Interpreter(model_path = config.model['path'])
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

disease_id = ['BS6', 'EB1', 'FW9', 'GM11', 'HT12', 'LB2', 'MV7', 'PM4', 'SL5', 'TS3',  'VW10', 'YL8']

def predict_disease(image_path, confidence_threshold=0.6):
    # Tiền xử lý hình ảnh
    input_shape = input_details[0]['shape']

    try:
        # Load và xử lý ảnh
        img = Image.open(image_path).resize((input_shape[1], input_shape[2]))
        img = img.convert('RGB')
        img_array = np.array(img).astype(np.uint8)

        # Thêm chiều batch
        img_array = np.expand_dims(img_array, axis=0).astype(input_details[0]['dtype'])

        # Thiết lập tensor đầu vào và thực hiện dự đoán
        interpreter.set_tensor(input_details[0]['index'], img_array)
        interpreter.invoke()

        # Lấy kết quả dự đoán
        output_data = interpreter.get_tensor(output_details[0]['index'])

    except Exception as e:
        return {"status_code": 500, "message": "Internal Server Error", "error": str(e)}

    # Lấy giá trị dự đoán và confidence
    result = np.array(output_data[0])
    argmax_result = np.argmax(result)
    confidence = result[argmax_result]

    # Kiểm tra confidence threshold
    if confidence > confidence_threshold:
        result_json = disease_id[argmax_result]  # Dự đoán dựa trên index lớn nhất
    else:
        result_json = "Unknown"

    return result_json


