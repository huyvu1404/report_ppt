from utils import PROJECT_DIR
from slides_builder import create_presentation
from data_processing import generate_json_data, load_data

def main():
    this_week = load_data(str(PROJECT_DIR / 'data/current_data.xlsx'))
    last_week = load_data(str(PROJECT_DIR / 'data/previous_data.xlsx'))
    df_this_week = generate_json_data(str(PROJECT_DIR / 'data/current_data.xlsx'))
    df_last_week = generate_json_data(str(PROJECT_DIR / 'data/previous_data.xlsx'))
    if df_this_week is None or df_last_week is None:
        print("❌ Lỗi khi tải dữ liệu. Vui lòng kiểm tra tệp tin.")
        return
    prs = create_presentation(this_week, last_week, 'SHB', df_this_week, df_last_week)

if __name__ == "__main__":
    main()
