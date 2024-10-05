import streamlit as st
import requests
import json
# Thêm CSS tùy chỉnh cho header, nút Send và giao diện chat
# Thêm CSS tùy chỉnh cho header, nút Send, giao diện chat và thông báo
st.markdown("""
<style>
.header-style {
    font-size: 24px;
    font-weight: bold;
    background-color: #f0f2f6;
    padding: 10px;
    border-radius: 5px;
    margin-bottom: 10px;
    border: 1px solid #d1d5db;
    text-align: center;
}
.send-button {
    width: 100%;
    background-color: #4CAF50;
    color: white;
    padding: 14px 20px;
    margin: 8px 0;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}
.send-button:hover {
    background-color: #45a049;
}
.chat-container {
    height: 300px;
    overflow-y: auto;
    border: 1px solid #ccc;
    padding: 10px;
    border-radius: 5px;
    background-color: white;
}
.chat-message {
    padding: 1rem;
    border-radius: 0.5rem;
    margin-bottom: 1rem;
}
.chat-message.user {
    background-color: #2b313e;
    color: black;
}
.chat-message.bot {
    background-color: #475063;
    color: black;
}
.chat-message .avatar {
    width: 20%;
}
.chat-message .avatar img {
    max-width: 78px;
    max-height: 78px;
    border-radius: 50%;
    object-fit: cover;
}
.chat-message .message {
    width: 80%;
    padding: 0 1rem;
    color: #fff;
}
.success-message {
    color: #4CAF50;
    font-weight: bold;
}
.error-message {
    color: #FF0000;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)


st.title('🐬 Vision - Large Language Model')

# Tạo 3 cột với tỷ lệ 10:1:10
view_1, divider, view_2 = st.columns([10, 1, 10])

with view_1:
    st.markdown('<p class="header-style">Upload Image</p>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Chọn một hình ảnh", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        st.image(uploaded_file, caption='Hình ảnh đã tải lên', use_column_width=True)
    send_flag = False
    if st.button('Send', key='send_button', help='Gửi hình ảnh', use_container_width=True):
        # Xử lý khi nút được nhấn
        if uploaded_file is not None:
            files = {
                'file': uploaded_file
            }
            respone = requests.post("http://127.0.0.1:1712/upload", files=files)
            print(respone.text)
            mapping_label = {
                'EB1': 'Bệnh bạc lá sớm',
                'LB2': 'Bệnh mốc sương (bệnh sương mai)',
                'TS3': 'Bệnh virus đốm héo cà chua',
                'PM4': 'Bệnh phấn trắng',
                'SL5': 'Bệnh lá đốm',
                'BS6': 'Bệnh đốm vi khuẩn',
                'MV7': 'Bệnh xoăn lá',
                'YL8': 'Bệnh khảm lá',
                'FW9': 'Bệnh héo vàng',
                'VW10': 'Bệnh héo rủ',
                'GM11': 'Bệnh Nấm Mốc Xám',
                'HT12': 'HT12',
                'Unknown': 'Unknown'
            }
            result = json.loads(respone.text)['result']
            result = mapping_label[result]
            send_flag = True
            if respone.status_code == 200:
                st.markdown('<p class = "success-message">Send Successfully !</p>', unsafe_allow_html=True)
            else:
                st.markdown(f'<p class="error-message">Có lỗi xảy ra khi gửi ảnh. Mã lỗi: {respone.status_code}</p>', unsafe_allow_html=True)
        else:
            st.markdown('<p class="error-message">Please select a photo before submitting !</p>', unsafe_allow_html=True)

# Thêm đường kẻ dọc vào cột giữa
with divider:
    st.markdown('<div style="border-left: 1px solid #ccc; height: 100vh;"></div>', unsafe_allow_html=True)

with view_2:
    st.markdown('<p class="header-style">Chatbot</p>', unsafe_allow_html=True)
    
    # Tạo một container cho toàn bộ giao diện chat
    chat_container = st.container()
    
    # Tạo một container riêng cho trường nhập liệu
    input_container = st.container()
    
    # Khởi tạo lịch sử trò chuyện nếu chưa có
    if 'messages' not in st.session_state:
        st.session_state.messages = [
             {"role": "assistant", "content": "Xin chào, tôi có thể giúp gì cho bạn?"}
        ]
    if send_flag == True:
        if result == 'Unknown':
             st.session_state.messages = [
                 {"role": "assistant", "content": f"Đây không phải là ảnh lá cây. Vui lòng gửi ảnh lá cây để được hỗ trợ!"}
             ]
             send_flag = False
        else:
            st.session_state.messages = [
                {"role": "assistant", "content": f"Bệnh mà cây đang gặp phải là: {result}. Dưới đây là các thông tin về bệnh này:"}
            ]
    # Hiển thị lịch sử trò chuyện trong chat_container
    with chat_container:
        # chat_placeholder = st.empty()
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
            
    # Đặt trường nhập liệu ở cuối, trong input_container
    with input_container:
        if prompt := st.chat_input("Nhập câu hỏi của bạn...", key="user_input") or send_flag == True:
            if send_flag == True:
                prompt = f'Hãy cho biết {result} là gì? Nguyên nhân gây ra {result} là gì? Cách phòng tránh và chữa {result} trên cây là gì? Hãy trả lời câu hỏi trên không có kí tự đặc biệt'
                send_flag = False
            else:
                st.session_state.messages.append({"role": "user", "content": prompt})
                with chat_container:
                    with st.chat_message("user"):
                        st.markdown(prompt)
            prompt_json = {
                "message" : prompt
            }
            response1= requests.post("http://127.0.0.1:1712/chatbot",json = prompt_json)
            
            st.session_state.messages.append({"role": "assistant", "content": response1.text})
            with chat_container:
                with st.chat_message("assistant"):
                    st.markdown(response1.text)
    # chat_content = ""
    # for message in st.session_state.messages:
    #     role_class = "bot" if message["role"] == "assistant" else "user"
    #     chat_content += f'<div class="chat-message {role_class}">{message["content"]}</div>'
    
    # # Cập nhật placeholder với nội dung chat mới
    # chat_placeholder.markdown(f'<div class="chat-container">{chat_content}</div>', unsafe_allow_html=True)
    # Tự động cuộn xuống cuối cùng của chat_container
    st.markdown('<script>window.scrollTo(0,document.body.scrollHeight);</script>', unsafe_allow_html=True)