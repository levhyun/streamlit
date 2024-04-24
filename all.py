# OpenAI 이미지 생성기 웹 앱

import my_image_gen as my_image_gen # 이미지 생성을 위한 모듈을 임포트
import streamlit as st
import openai
import os
import requests
import textwrap
from datetime import datetime
import my_text_sum as my_text_sum # 텍스트를 요약하기 위한 모듈
from openai import OpenAI
from PyPDF2 import PdfReader
import tiktoken
import my_yt_tran  # 유튜브 동영상 정보와 자막을 가져오기 위한 모듈 임포트
import textwrap
import deepl

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

# PDF 파일을 요약하는 함수
def summarize_PDF_file(pdf_file, lang, trans_checked):
    if (pdf_file is not None):
        st.write("PDF 문서를 요약 중입니다. 잠시만 기다려 주세요.") 
        reader = PdfReader(pdf_file) # PDF 문서 읽기

        text_summaries = []
        
        for page in reader.pages:
            page_text = page.extract_text() # 페이지의 텍스트 추출
            text_summary = my_text_sum.summarize_text(page_text, lang)
            text_summaries.append(text_summary)
            
        token_num, final_summary = my_text_sum.summarize_text_final(text_summaries, lang)
        
        if final_summary != "":
            shorten_final_summary = textwrap.shorten(final_summary, 
                                                     250, 
                                                     placeholder=' [..이하 생략..]')

            st.write("- 최종 요약(축약):", shorten_final_summary) # 최종 요약문 출력 (축약)
            #st.write("- 최종 요약:", shorten_final_summary) # 최종 요약문 출력

            if trans_checked:
                trans_result = my_text_sum.traslate_english_to_korean_using_openAI(final_summary)
                shorten_trans_result = textwrap.shorten(trans_result, 
                                                        200, 
                                                        placeholder=' [..이하 생략..]')
                st.write("- 한국어 요약(축약):", shorten_trans_result) # 한국어 번역문 출력 (축약)
                #st.write("- 한국어 요약:", trans_result) # 한국어 번역문 출력
        else:
            st.write("- 통합한 요약문의 토큰 수가 커서 요약할 수 없습니다.")

# 텍스트의 토큰 수를 계산하는 함수(모델: "gpt-3.5-turbo")
def calc_token_num(text, model="gpt-4-turbo-2024-04-09"):
    enc = tiktoken.encoding_for_model(model)
    encoded_list = enc.encode(text) # 텍스트 인코딩해 인코딩 리스트 생성
    token_num= len(encoded_list)    # 인코딩 리스트의 길이로 토큰 개수 계산
    
    return token_num

# 토큰에 따라 텍스트를 나눠 분할하는 함수
def divide_text(text, token_num):
    req_max_token = 2000 # 응답을 고려해 설정한 최대 요청 토큰
    
    divide_num = int(token_num/req_max_token) + 1 # 나눌 계수를 계산
    divide_char_num = int(len(text) / divide_num) # 나눌 문자 개수 
    divide_width =  divide_char_num + 20 # wrap() 함수로 텍스트 나눌 때 여유분 고려해 20 더함

    divided_text_list = textwrap.wrap(text, width=divide_width)
    
    return divide_num, divided_text_list

# 유튜브 동영상을 요약하는 함수
def summarize_youtube_video(video_url, selected_lang, trans_method):
    
    if selected_lang == '영어':
        lang = 'en' 
    else:
        lang = 'ko' 
    
    # 유튜브 동영상 플레이
    st.video(video_url, format='video/mp4') # st.video(video_url) 도 동일

    # 유튜브 동영상 제목 가져오기
    _, yt_title, _, _, yt_duration = my_yt_tran.get_youtube_video_info(video_url)
    st.write(f"[제목] {yt_title}, [길이(분:초)] {yt_duration}") # 제목 및 상영 시간출력
    
    # 유튜브 동영상 자막 가져오기
    yt_transcript = my_yt_tran.get_transcript_from_youtube(video_url, lang)

    # 자막 텍스트의 토큰 수 계산
    token_num = calc_token_num(yt_transcript)
    
    # 자막 텍스트를 분할해 리스트 생성
    div_num, divided_yt_transcripts = divide_text(yt_transcript, token_num)

    st.write("유튜브 동영상 내용 요약 중입니다. 잠시만 기다려 주세요.") 
    
    # 분할 자막의 요약 생성
    summaries = []
    for divided_yt_transcript in divided_yt_transcripts:
        summary = my_text_sum.summarize_text(divided_yt_transcript, lang) # 텍스트 요약
        summaries.append(summary)
        
    # 분할 자막의 요약을 다시 요약     
    _, final_summary = my_text_sum.summarize_text_final(summaries, lang)

    if selected_lang == '영어':
        shorten_num = 200 
    else:
        shorten_num = 120 
        
    shorten_final_summary = textwrap.shorten(final_summary, shorten_num, placeholder=' [..이하 생략..]')
    st.write("- 자막 요약(축약):", shorten_final_summary) # 최종 요약문 출력 (축약)
    # st.write("- 자막 요약:", final_summary) # 최종 요약문 출력

    if selected_lang == '영어': 
        if trans_method == 'OpenAI':
            trans_result = my_text_sum.traslate_english_to_korean_using_openAI(final_summary)
        elif trans_method == 'DeepL':
            trans_result = my_text_sum.traslate_english_to_korean_using_deepL(final_summary)

        shorten_trans_result = textwrap.shorten(trans_result, 120 ,placeholder=' [..이하 생략..]')
        st.write("- 한국어 요약(축약):", shorten_trans_result) # 한국어 번역문 출력 (축약)
        #st.write("- 한국어 요약:", trans_result) # 한국어 번역문 출력

# ------------------- 콜백 함수 --------------------
def button_callback():
    st.session_state['input'] = ""
    

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


st.title("PDF 문서를 요약하는 웹 앱")

uploaded_file = st.file_uploader("PDF 파일을 업로드하세요.", type='pdf')

radio_selected_lang = st.radio('PDF 문서 언어', ['한국어', '영어'], index=1, horizontal=True)

if radio_selected_lang == '영어':
    lang_code = 'en' 
    checked = st.checkbox('한국어 번역 추가') # 체크박스 생성
else:
    lang_code = 'ko' 
    checked = False # 체크박스 불필요
    
clicked = st.button('PDF 문서 요약')

if clicked:
    summarize_PDF_file(uploaded_file, lang_code, checked) # PDF 파일 요약 수행

st.title("요약 설정 ")
url_text = st.text_input("유튜브 동영상 URL을 입력하세요.", key="input")

clicked_for_clear = st.button('URL 입력 내용 지우기',  on_click=button_callback)

yt_lang = st.radio('유튜브 동영상 언어 선택', ['한국어', '영어'], index=1, horizontal=True)
    
if yt_lang == '영어':
    trans_method = st.radio('번역 방법 선택', ['OpenAI', 'DeepL'], index=1, horizontal=True)
else:
    trans_method = ""

clicked_for_sum = st.button('동영상 내용 요약')

st.title("유튜브 동영상 요약")

# 텍스트 입력이 있으면 수행
if url_text and clicked_for_sum: 
    yt_video_url = url_text.strip()
    summarize_youtube_video(yt_video_url, yt_lang, trans_method)