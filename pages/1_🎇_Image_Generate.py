import streamlit as st
import my_image_gen as my_image_gen # 이미지 생성을 위한 모듈을 임포트
import requests
import textwrap
from datetime import datetime

# OpenAI 이미지 생성기 웹 앱
st.set_page_config(page_title="Image Generate", page_icon="🎇")

# ---- 세션 상태 초기화 --------
if 'image_caption' not in st.session_state:
    st.session_state['image_caption'] = "" # 빈 문자열로 초기화 
    
if 'shorten_text_for_image' not in st.session_state:
    st.session_state['shorten_text_for_image'] = "" # 빈 문자열로 초기화 
    
if 'image_urls' not in st.session_state:
    st.session_state['image_urls'] = [] # 빈 리스트로 초기화
    
if 'images' not in st.session_state:
    st.session_state['images'] = [] # 빈 리스트로 초기화    

if 'download_file_names' not in st.session_state:
    st.session_state['download_file_names'] = [] # 빈 리스트로 초기화    
    
if 'download_buttons' not in st.session_state:
    st.session_state['download_buttons'] = False # False로 초기화
    
# ---- 이미지 생성을 위한 텍스트와 생성된 이미지를 화면에 표시하는 함수 ----
def display_results():
    # 저장한 세션 상태 불러오기
    shorten_text_for_image = st.session_state['shorten_text_for_image']
    image_caption = st.session_state['image_caption']
    image_urls = st.session_state['image_urls']    
    
    # 텍스트를 표시
    st.write("[이미지 생성을 위한 텍스트]") 
    st.write(shorten_text_for_image)
    
    # 이미지와 다운로드 버튼을 화면에 표시
    for k, image_url in enumerate(image_urls):
        st.image(image_url, caption=image_caption) # 이미지 표시
        
        image_data = st.session_state['images'][k]
        download_file_name = st.session_state['download_file_names'][k]

        # 다운로드 버튼
        st.download_button( label="이미지 파일 다운로드",
                            data=image_data,
                            file_name=download_file_name,
                            mime="image/png",
                            key=k,
                            on_click=download_button_callback)
        
# ------------------- 콜백 함수 --------------------
def download_button_callback():
    st.session_state['download_buttons'] = True

def button_callback():
    
    if radio_selected_lang == "한국어":
        translated_text = my_image_gen.translate_text_for_image(input_text) # 한국어를 영어로 번역
    elif radio_selected_lang == "영어":
        translated_text = input_text
    
    if detail_description == 'Yes':        
        resp = my_image_gen.generate_text_for_image(translated_text) # 이미지 생성을 위한 상세 묘사 생성
        text_for_image = resp
        image_caption ="상세 묘사를 추가해 생성한 이미지"
    elif detail_description == 'No': 
        text_for_image = translated_text
        image_caption ="입력 내용으로 생성한 이미지"
    
    # 텍스트 축약
    shorten_text_for_image = textwrap.shorten(text_for_image, 200, placeholder=' [..이하 생략..]')
    
    # 이미지 생성
    image_urls = my_image_gen.generate_image_from_text(text_for_image, image_num, image_size)

    # 이미지와 다운로드 파일 이름 생성
    images = []
    download_file_names = []
    for k, image_url in enumerate(image_urls):
        
        # 생성한 이미지 다운로드
        r = requests.get(image_url)
        image_data = r.content # 이미지 데이터
        images.append(image_data)
        
        # 다운로드 파일 이름 생성
        now_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") # 이미지 생성 날짜와 시각
        download_file_name = f"gen_image_{k}_{now_datetime}.png"
        download_file_names.append(download_file_name)
        
    # 세션 상태 저장
    st.session_state['image_caption'] = image_caption
    st.session_state['shorten_text_for_image'] = shorten_text_for_image
    st.session_state['image_urls'] = image_urls
    st.session_state['download_file_names'] = download_file_names
    st.session_state['images'] = images

# ------------- 사이드바 화면 구성 --------------------------   


# ------------- 메인 화면 구성 --------------------------   
st.title("인공지능 이미지 생성기")

input_text = st.text_input("이미지 생성을 위한 설명을 입력하세요.",
                                    "빌딩이 보이는 호수가 있는 도시의 공원")

radio_selected_lang = st.radio('입력한 언어', ['한국어', '영어'], 
                                       index=0, horizontal=True)

# 라디오 버튼: 생성 이미지 개수 지정
image_num_options = [1, 2, 3] # 세 종류의 이미지 개수 선택 가능
image_num = st.radio('생성할 이미지 개수를 선택하세요.', 
                      image_num_options, index=0, horizontal=True)

# 라디오 버튼: 이미지 크기 지정
image_size_options = ['256x256', '512x512', '1024x1024'] # 세 종류의 이미지 크기 선택 가능
image_size = st.radio('생성할 이미지 크기를 선택하세요.', 
                      image_size_options, index=1, horizontal=True)

# 라디오 버튼: 상세 묘사 추가 여부 지정
detail_description = st.radio('상세 묘사를 추가하겠습니까?', 
                      ['Yes', 'No'], index=1, horizontal=True)

# 기본 버튼: 이미지 생성을 위해 사용
# clicked = st.button('이미지 생성')
clicked = st.button('이미지 생성', on_click=button_callback)

# [이미지 생성] 버튼 혹은 [이미지 파일 다운로드] 버튼 클릭 시 화면 표시 함수 실행    
if clicked or st.session_state['download_buttons'] == True:
    display_results()
