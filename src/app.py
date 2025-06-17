
import os
import base64
import streamlit as st
from io import BytesIO
from utils import PROJECT_DIR
from slides_builder import create_presentation
from data_processing import generate_json_data, load_data

st.set_page_config(page_title="Slide Generator", layout="centered")

def add_logo():
    logo_path = PROJECT_DIR / "assets/logo.png"
    if os.path.exists(str(logo_path)):
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
    add_logo()

    st.markdown(
        "<h3 style='text-align: top-center;'>📊 Tạo Slide Báo Cáo Tự Động</h3>",
        unsafe_allow_html=True
    )
    uploaded_this_week = st.file_uploader("📂 Upload dữ liệu **tuần này** (.xlsx)", type=["xlsx"])
    uploaded_last_week = st.file_uploader("📂 Upload dữ liệu **tuần trước** (.xlsx)", type=["xlsx"])

    topic = None

    if uploaded_this_week and uploaded_last_week:
        try:
            # topics = ["SHB", "Vietcombank", "Techcombank", "MBBank", "VPBank", "MSB"]
            topics = ["SHB"]
            topic = st.selectbox("📌 Chọn chủ đề chính", sorted(topics))
        except Exception as e:
            st.error(f"❌ Lỗi khi tải dữ liệu: {e}")

    if uploaded_this_week and uploaded_last_week and topic:
        if st.button("🚀 Tạo Slide"):
            try:
                current_json = generate_json_data(uploaded_this_week)
                previous_json = generate_json_data(uploaded_last_week)

                df_this_week = load_data(uploaded_this_week)
                df_last_week = load_data(uploaded_last_week)
                if df_this_week is None or df_last_week is None:
                    st.error("❌ Lỗi khi tải dữ liệu. Vui lòng kiểm tra tệp tin.")
                    return
                
                prs = create_presentation(df_this_week, df_last_week, topic, current_json, previous_json)

                output = BytesIO()
                prs.save(output)
                output.seek(0)

                st.success("✅ Tạo slide thành công!")
                st.download_button(
                    label="📥 Tải slide",
                    data=output,
                    file_name=f"report_{topic}.pptx",
                    mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
                )
            except Exception as e:
                st.error(f"❌ Lỗi khi tạo slide: {e}")

if __name__ == "__main__":
    main()
