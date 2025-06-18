import requests
import json

def get_first_insight(json_data, max_attempts=3):
    for _ in range(max_attempts):
        try:
            url = "https://service-ai.radaa.net/llm/v1/chat/completions"

            payload = json.dumps({
            "model": "meta-llama/Llama-4-Scout-17B-16E-Instruct",
            "messages": [
                {
                "role": "user",
                "content": f"Dựa trên dữ liệu JSON được cung cấp, hãy viết một đoạn báo cáo ngắn. \n\t  \nYêu cầu:\n- Báo cáo là một đoạn văn có đúng 4 dòng:\n\t+ Dòng 1: Tổng thảo luận toàn ngành ghi nhận mức tăng/giảm `percentage_change`% so với tuần trước, với tổng thảo luận là Y thảo luận.\n\n\t+ Dòng 2: Tên thương hiệu đứng đầu (có tỷ lệ cao nhất), nêu bật các nội dung nổi bật hoặc chiến dịch truyền thông.\n\n\t+ Dòng 3: Tên thương hiệu đứng thứ hai, nêu bật các biến động (tăng/giảm so với tuần trước), nêu bật các nội dung nổi bật hoặc chiến dịch truyền thông.\n\n\t+ Dòng 4: Hai thương hiệu còn lại và các xu hướng nổi bật hoặc gây chú ý, được gom chung thành 1 đoạn.\n- Ở dòng 1, in đậm từ đầu cho tới X%.\n- In đậm các tên topic\n\nDữ liệu JSON:```json \n{json_data.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')} ```.\n\nDữ liệu nằm trong các trường:\n\t+`total`: Tổng số thảo luận trong tuần.\n\t+`percentage_change`: Tỉ lệ % thay đổi của tổng số thảo luận so với tuần trước.\n\t+`details[].topic`: Tên thương hiệu.\n\t+`details[].percentage`: Thị phần của thương hiệu.\n\t+ `details[].last_percentage`: Thị phần của thương hiệu trong tuần trước.\n\t+`details[].posts[]`: Các bài viết nổi bật liên quan tới thương hiệu."
            }]
            })
            headers = {
            'Content-Type': 'application/json'
            }

            response = requests.request("POST", url, headers=headers, data=payload)
            result = response.json().get('choices', [{}])[0].get('message', {}).get('content', '')
            return result
        except Exception as e:
            print(f"Error calling LLM API: {e}")
    print("Failed to get a valid response from the LLM API after multiple attempts.")
    return None

def prepare_json_data(json_this_week, json_last_week):
    try:
        this_week = json.loads(json_this_week)
        last_week = json.loads(json_last_week)
        percentage_change = round((this_week["total"] - last_week["total"]) / last_week["total"] * 100, 0) if last_week["total"] != 0 else 0

        summary = {
            "total": this_week["total"],
            "percentage_change": percentage_change,
            "details": [
                {
                    "topic": topic_data["topic"],
                    "percentage": topic_data["percentage"],
                    "posts": [post["Content"] for post in topic_data.get("posts", [])[:5]]
                }
                for topic_data in sorted(this_week["details"], key=lambda x: x["percentage"], reverse=True)[:4]
            ]
        }

        json_data = json.dumps(summary, ensure_ascii=False, indent=2)
        return json_data
    except Exception as e:
        print(f"Error preparing JSON data: {e}")
        return None
