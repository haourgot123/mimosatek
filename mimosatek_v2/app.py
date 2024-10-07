import streamlit as st
from dotenv import load_dotenv
import os
import requests
from groq import Groq
import config
import json
import time
########################################### CSS ###############################
css = '''
    <style>
    [data-testid='stFileUploader'] {
        width: max-content;
    }
    [data-testid='stFileUploader'] section {
        padding: 0;
        float: left;
    }
    [data-testid='stFileUploader'] section > input + div {
        display: none;
    }
    }
    [data-testid='stFileUploader'] section + div {
        float: right;
        padding-top: 0;
    }
    </style>
    '''
st.markdown("""
<style>
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
################################################################################
load_dotenv()
client = Groq(api_key = os.getenv('GROQ_API_KEY'))

st.title('🤖 Vision - Large Language Model')



if 'groqai_model' not in st.session_state:
    st.session_state['groqai_model'] = 'llama3-8b-8192'

if 'messages' not in st.session_state:
    st.session_state.messages = []





with st.sidebar:
    st.image('image.png', use_column_width=True)
    if st.button('🎯 New chat', use_container_width=True):
        st.session_state.messages = []
    st.button(f"📤 Upload Image", use_container_width=True)
    upload_file = st.file_uploader(f"🚩Click here to upload image")
    st.markdown(css, unsafe_allow_html=True)
    send_flag = False
    result, task_id = '', ''
    
    if upload_file is not None:
        st.image(upload_file, use_column_width=True)
        if st.button('Send', key='send_button', help='Gửi hình ảnh', use_container_width=True):
            if upload_file is not None:
                file = {
                    'file': upload_file
                }
                task_id = requests.post("http://127.0.0.1:1712/upload", files=file)
                task_id = json.loads(task_id.text)['task_id']
                print(task_id)
                time.sleep(1)
                response = requests.get(f'http://127.0.0.1:1712/result/{task_id}')
                print(response.text)
                result = json.loads(response.text)['result']
                if result != 'Running':
                    result = config.label_mapping[result]
                # Check trạng thái của respone
                if response.status_code == 200:
                    st.markdown('<p class = "success-message">Send Successfully !</p>', unsafe_allow_html=True)
                    send_flag = True
                else:
                    st.markdown(f'<p class="error-message">Có lỗi xảy ra khi gửi ảnh. Mã lỗi: {response.status_code}</p>', unsafe_allow_html=True)

if len(st.session_state.messages) == 0:
    with st.chat_message('assistant'):
        st.markdown('🙋‍♂️ Xin chào ! Tôi có thể giúp gì cho bạn.')

for message in st.session_state.messages:
    with st.chat_message(message['role']):
        st.markdown(message['content'])


if send_flag == True:
    if result == 'Running':
        answers = '🕐 Bạn vui lòng đợi trong giây lát...'
    elif result == 'Unknown':
        answers = '❌ Đây không phải ảnh lá cây. Vui lòng gửi ảnh lá cây để được hỗ trợ !'
        send_flag = False
    else:
        answers = f'✅ Bệnh của cây đang gặp phải là : {result}. Dưới đây là thông tin của bệnh:'

    with st.chat_message('assistant'):
        st.markdown(answers)               



if prompt := st.chat_input('Hãy nhập câu hỏi của bạn') or send_flag == True:
    if send_flag == True and result != 'Running':
        st.session_state.messages.append(
            {
                'role': 'user',
                'content': f'Bạn là một chuyên gia nông nghiêp. Đưa ra các thông tin về {result} trên cây cà chua, bao gồm: Khái niệm, nguyên nhân, cách phòng ngừa. '
            }
        )
    else:
        st.session_state.messages.append(
            {
                'role': 'user', 
                'content': prompt
            }
        )
        with st.chat_message('user'):
            st.markdown(prompt)
    with st.chat_message('assistant'):
        full_res = ''
        holder = st.empty()
        for response in client.chat.completions.create(
            model = st.session_state['groqai_model'],
            messages = [
                {'role': m['role'],  'content': m['content']}
                for m in st.session_state.messages
            ],
            stream = True,
        ):
            full_res += (response.choices[0].delta.content or "")
            holder.markdown(full_res + '|')
            holder.markdown(full_res)
        holder.markdown(full_res)
        if send_flag == True and result != 'Running':
            st.session_state.messages.pop()
            send_flag = False
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": full_res
        }
    )


