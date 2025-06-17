import requests
import json

def get_fourth_insight(json_data):
    url = "https://service-ai.radaa.net/llm/v1/chat/completions"

    payload = json.dumps({
    "model": "meta-llama/Llama-4-Scout-17B-16E-Instruct",
    "messages": [
        {
        "role": "user",
        "content": f"Dựa vào dữ liệu JSON bên dưới. Hãy viết một đoạn báo cáo tóm tắt.\n\nYêu cầu:\n- Báo cáo cần làm rõ các vấn đề sau:\n\t+ Tổng thảo luận của `topic` trong tuần này là bao nhiêu?Tăng hay giảm bao nhiêu % so với tuần trước?\n\t+ **Kênh** nào đang đang sở hữu thị phần dẫn đầu tại `topic`? Theo sau là **Kênh** với tỉ lệ bao nhiêu? Hai kênh này đóng vai trò chủ lực truyền thông với các tuyến nội dung nói về vấn đề gì?\n\t + Trong khi đó, **Kênh** đứng thứ 3 về thị phần là kênh nào? Nội bật với nội dung gì?\n\nYêu cầu định dạng:\n- Trình bày ngắn gọn, liên mạch, không liệt kê.\n - Chỉ trình bày nội dung chính, không mở đầu, không giới thiệu.\n- In đậm tên các ngân hàng và các kênh truyền thông.\n\nDữ liệu JSON:```json \n{json_data.replace('\\', '\\\\').replace('\"', '\\\"').replace('\\n', ' ')} \n```\n\nDữ liệu nằm trong các trường:\n+ `topic`: Tên thương hiệu\n+`total`: Tổng số thảo luận tuần này\n  - `last_total`: Tổng số thảo luận trong tuần trước.\n  - `channels[]`: Các kênh truyền thông và tổng số thảo luận tương ứng `channels[].total`.\n  - `posts[]`: Danh sách bài viết được sắp xếp giảm dần theo số lượng tương tác.\n\t +`posts[].Channel`: Kênh bài viết được đăng, `posts[].Interactions`: Tổng số tương tác của bài đăng."
    }]
    })
    headers = {
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    result = response.json().get('choices', [{}])[0].get('message', {}).get('content', '')
    return result

def prepare_json_data_4th(json_this_week, json_last_week, main_topic):

    this_week = json.loads(json_this_week)
    last_week = json.loads(json_last_week)
    last_week_map = {detail["topic"]: detail for detail in last_week["details"]}

    result = {}
    for topic_data in this_week["details"]:
        if topic_data["topic"] == main_topic:
            result["topic"] = topic_data["topic"]
            result["total"] = topic_data["total"]
            result["last_total"] = last_week_map.get(topic_data["topic"], {}).get("total", 0)
            result["channels"] = [
                {"channel": channel_data["channel"], "total": channel_data["total"]}
                for channel_data in topic_data.get("channels", [])
            ]
            result["posts"] = topic_data.get("posts", [])

    json_data = json.dumps(result, ensure_ascii=False, indent=2)
    return json_data
