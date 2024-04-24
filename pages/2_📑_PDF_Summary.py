import my_text_sum as my_text_sum # 텍스트를 요약하기 위한 모듈
import streamlit as st
from PyPDF2 import PdfReader
import textwrap

# PDF 문서를 요약하는 웹 앱
st.set_page_config(page_title="PDF Summary", page_icon="📑")

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

# ------------- 메인 화면 구성 --------------------------  
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
