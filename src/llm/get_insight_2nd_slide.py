import requests
import json

def get_second_insight(json_data):
    url = "https://service-ai.radaa.net/llm/v1/chat/completions"

    payload = json.dumps({
    "model": "meta-llama/Llama-4-Scout-17B-16E-Instruct",
    "messages": [
        {
        "role": "user",
        "content": f"Dựa trên dữ liệu JSON và ví dụ bên dưới, hãy viết một đoạn báo cáo ngắn.\n\nYêu cầu:\n- Báo cáo trình bày trong 2 đoạn theo đúng bố cục 2 dòng gồm:\n\t**Dòng 1**: **Tổng thảo luận tích cực của các ngân hàng tăng/giảm X % so với tuần trước**. Tên thương hiệu có tỷ lệ tích cực cao nhất, sau đó là thương hiệu thứ hai. Nhấn mạnh lý do/các chiến dịch nổi bật tạo ra sự chú ý.\n\t**Dòng 2**: **Tổng thảo luận tiêu cực tuần này tăng/giảm X % so với tuần trước**. Tên 2 thương hiệu tiêu cực đáng chú ý nhất, nêu các lý do, phản ánh hoặc chiến dịch gây tranh cãi.\n\nLưu ý:\n Chỉ trình bày nội dung chính, không mở đầu, không dẫn dắt.\n- In đậm các tên thương hiệu (từ trường `topic`)\n\nDữ liệu JSON:```json \n{json_data.replace('\\', '\\\\').replace('\"', '\\\"').replace('\\n', ' ')} \n```.\n\nDữ liệu nằm trong các trường:\n+ `current.Negative`: Tổng số thảo luận tiêu cực trong tuần\n+ `previous.Negative`: Tổng số thảo luận tiêu cực tuần trước.\n+ `current.Positive`: Tổng số thảo luận tích cực trong tuần\n+ `previous.Positive`: Tổng số thảo luận tích cực tuần trước\n+ `details[]`: Danh sách các ngân hàng với trường:\n  - `topic`: Tên thương hiệu\n  - `sentiments.Negative`: Số lượng thảo luận tiêu cực trong tuần.\n  - `sentiments.Positive`: Số lượng thảo luận tích cực trong tuần\n  - `posts[]`: Danh sách bài viết tiêu biểu."
    }]
    })
    headers = {
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    result = response.json().get('choices', [{}])[0].get('message', {}).get('content', '')
    return result

def prepare_json_data_2nd(json_this_week, json_last_week):

    this_week = json.loads(json_this_week)
    last_week = json.loads(json_last_week)

    summary = {
        "current": this_week["sentiments"],
        "previous": last_week["sentiments"],
        "details": [
            {
                "topic": topic_data["topic"],
                "sentiments": topic_data["sentiments"],
                "posts": [post["Content"] for post in topic_data.get("posts", [])[:5]]
            }
            for topic_data in sorted(this_week["details"], key=lambda x: x["percentage"], reverse=True)[:4]
        ]
    }

    json_data = json.dumps(summary, ensure_ascii=False, indent=2)
    return json_data


