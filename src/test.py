import streamlit as st
import pandas as pd
from slides_builder import create_presentation
from io import BytesIO
import os
import base64
from data_processing import generate_json_data, load_data

# Theme setup (this must be done via config.toml — see instructions below)
st.set_page_config(page_title="Slide Generator", layout="centered")

def add_logo():
    logo_path = "src/assets/logo.png"
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            data_url = base64.b64encode(f.read()).decode("utf-8")
        st.markdown(
            f"""
            <div style="text-align: left;">
                <img src="data:image/png;base64,{data_url}" alt="logo" style="height: 80px; margin-bottom: 1rem;">
            </div>
            """,
            unsafe_allow_html=True
        )

def main():


  
    this_week = load_data('/home/huyvu/workspace/kompa/pptx/data/current_data.xlsx')
    last_week = load_data('/home/huyvu/workspace/kompa/pptx/data/previous_data.xlsx')
    df_this_week = generate_json_data('/home/huyvu/workspace/kompa/pptx/data/current_data.xlsx')
    df_last_week = generate_json_data('/home/huyvu/workspace/kompa/pptx/data/previous_data.xlsx')
    if df_this_week is None or df_last_week is None:
        st.error("❌ Lỗi khi tải dữ liệu. Vui lòng kiểm tra tệp tin.")
        return
    
    prs = create_presentation(this_week, last_week, 'SHB', df_this_week, df_last_week)

    
if __name__ == "__main__":
    main()
