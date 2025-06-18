import requests
import json

def get_third_insight(json_data, max_attempts=3):
    for _ in range(max_attempts):
        try:     
            url = "https://service-ai.radaa.net/llm/v1/chat/completions"

            payload = json.dumps({
            "model": "meta-llama/Llama-4-Scout-17B-16E-Instruct",
            "messages": [
                {
                "role": "user",
                "content": f"Dựa vào dữ liệu JSON bên dưới. Hãy viết một đoạn báo cáo tóm tắt không quá 150 từ.\n\nYêu cầu:\n- Báo cáo cần làm rõ các vấn đề sau\n\t+ **Chủ đề** nào đang tạo thảo luận tích cực tại các ngân hàng (dựa vào số lượng `labels[].sentiments.Positive`)? Nhờ vào các hoạt động truyền thông, chiến dịch nào?\nThảo luận tiêu cực hiện đang xoay quanh **chủ đề** nào? Nêu các thương hiệu có thảo luận tiêu cực nổi bật nhất.\n- Nêu rõ các vấn đề gây tiêu cực \n\nYêu cầu định dạng:\n- Trình bày ngắn gọn, liên mạch, không liệt kê.\n - Chỉ trình bày nội dung chính, không mở đầu, không giới thiệu, không kèm theo số liệu.\n - Trình bày trong 2 đoạn văn duy nhất.\n- In đậm tên các ngân hàng và chủ đề thảo luận.\n\nDữ liệu JSON:```json \n{json_data.replace('\\', '\\\\').replace('\"', '\\\"').replace('\\n', ' ')}\n ```.\n\nDữ liệu nằm trong các trường:\n+ `details[]`: Danh sách các thương hiệu:\n  - `topic`: Tên ngân hàng\n  - `sentiments`: Số lượng thảo luận tương ứng với các cảm xúc\n  - `posts[]`: Danh sách bài viết tích cực tiêu biểu\n+ `labels[].label`: Các chủ đề thảo luận, `labels[].sentiments.Positive`: Số lượng phản hồi tích cực liên quan tới chủ đề này, `labels[].sentiments.Negative`: Số lượng phản hồi tiêu cực liên quan tới chủ đề này."
            }]
            })
            headers = {
            'Content-Type': 'application/json'
            }

            response = requests.request("POST", url, headers=headers, data=payload)
            result = response.json().get('choices', [{}])[0].get('message', {}).get('content', '')
            if result:
                return result
        except Exception as e:
            print(f"Error calling LLM API: {e}")
    print("Failed to get a valid response from the LLM API after multiple attempts.")
    return None

def prepare_json_data_3rd(json_this_week):
    try:
        this_week = json.loads(json_this_week)
        summary = []
        for topic_data in sorted(this_week["details"], key=lambda x: x["percentage"], reverse=True)[:3]:
            labels = topic_data.get("labels", [])

            top_positive = sorted(
                labels, 
                key=lambda x: x.get("sentiments", {}).get("Positive", 0), 
                reverse=True
            )[:2]

            top_negative = sorted(
                labels, 
                key=lambda x: x.get("sentiments", {}).get("Negative", 0), 
                reverse=True
            )[:2]

            combined = top_positive + top_negative
            unique_labels = {label["label"]: label for label in combined}
            merged_labels = list(unique_labels.values())

            summary.append({
                "topic": topic_data["topic"],
                "labels": merged_labels,
                "posts": [post["Content"] for post in topic_data.get("posts", [])[:4]]
            })
        json_data = json.dumps(summary, ensure_ascii=False, indent=2)

        return json_data
    except Exception as e:
        print(f"Error preparing JSON data: {e}")
        return None
