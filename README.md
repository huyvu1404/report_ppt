import requests
import json

def get_fifth_insight(json_data):

    url = "https://service-ai.radaa.net/llm/v1/chat/completions"

    payload = json.dumps({
    "model": "meta-llama/Llama-4-Scout-17B-16E-Instruct",
    "messages": [
        {
        "role": "user",
        "content": f"Dựa vào dữ liệu JSON chứa 6 chủ đề được đề cập nhiều nhất trên mạng xã hội liên quan tới thương hiệu `topic`. Hãy viết một đoạn báo cáo tóm tắt.\n\nYêu cầu:\n- Báo cáo cần làm rõ các vấn đề sau:\n- Tóm tắt các nội dung liên quan tới từng chủ đề. Mỗi tóm tắt sẽ được nằm ở 1 dòng khác nhau.\n\nYêu cầu định dạng:\n- Trình bày ngắn gọn, không kèm số liệu, mỗi ý chỉ gói gọn trong 1 câu.\n - Chỉ trình bày đúng 6 dòng nội dung chính, không kèm theo dẫn dắt, không mở đầu.\n - Không liệt kê lại tên chủ đề.\n- In đậm tên các ngân hàng và các chủ đề.\n\nDữ liệu JSON:```json \n{json_data.replace('\\', '\\\\').replace('\"', '\\\"').replace('\\n', ' ')} \n```.\n\nDữ liệu nằm trong các trường:\n+ `topic`: Tên thương hiệu\n- `labels[]`: Các chủ đề thảo luận.\n  - `posts[]`: Danh sách bài viết.\n\t +`posts[].Channel`: Kênh bài viết được đăng, `posts[].Interactions`: Tổng số tương tác của bài đăng."
    }]
    })
    headers = {
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    result = response.json().get('choices', [{}])[0].get('message', {}).get('content', '')
    return result

def prepare_json_data_5th(json_this_week, main_topic):
 
    this_week = json.loads(json_this_week)

    result = {}
    for topic_data in this_week["details"]:
        if topic_data["topic"] == 'SHB':
            result["topic"] = topic_data["topic"]

            sorted_labels = sorted(
                topic_data.get("labels", []),
                key=lambda x: x.get("total", 0),
                reverse=True
            )[:6]
            result["labels"] = [sorted_label['label'] for sorted_label in sorted_labels]

            result["posts"] = topic_data.get("posts", [])

    json_data = json.dumps(result, ensure_ascii=False, indent=2)
    return json_data
