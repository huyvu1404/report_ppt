import pandas as pd
import json

def load_data(path):
    try:
        df = pd.read_excel(path) 
    except Exception as e:
        print(f"Error reading the file: {e}")
        return None 
    try:   
        mask = (df['Channel'] == 'Social') & df['UrlTopic'].str.contains('www.instagram.com', na=False)
        df.loc[mask, 'Channel'] = 'Instagram'
        # df = df[df['Channel'] != 'Social']
    except Exception as e:
        print(f"Error processing the data: {e}")
        return None
    return df

def pivot_data(df, main_topic='SHB', rows=None, columns=None, values=None, aggfunc=None):
    try:
        pivot = df.pivot_table(
            index=rows,
            columns=columns,
            values=values,
            aggfunc=aggfunc,
            fill_value=0
        )

        def clean_column(x):
            cleaned = [x[0].split('-')[0].strip()] + list(x[1:])
            return tuple(cleaned)

        if isinstance(pivot.columns, pd.MultiIndex):
            pivot.columns = pd.MultiIndex.from_tuples([clean_column(col) for col in pivot.columns])
        else:
            pivot.columns = [col.split('-')[0].strip() for col in pivot.columns]

        if isinstance(pivot.columns, pd.MultiIndex):
            all_topics = sorted({col[0] for col in pivot.columns})
            all_sentiments = sorted({col[1] for col in pivot.columns})
            full_columns = pd.MultiIndex.from_product([all_topics, all_sentiments])

            pivot = pivot.reindex(columns=full_columns, fill_value=0)

        if isinstance(pivot.columns, pd.MultiIndex):
            main_cols = [col for col in pivot.columns if main_topic in col[0]]
            other_cols = [col for col in pivot.columns if col not in main_cols]
        else:
            main_cols = [col for col in pivot.columns if main_topic in col]
            other_cols = [col for col in pivot.columns if col not in main_cols]

        pivot = pivot[main_cols + other_cols]

    except Exception as e:
        print(f"Error processing the data: {e}")
        return None

    return pivot

def prepare_data(df, main_topic='SHB', rows = None, columns = None, values = None, aggfunc = None):
    if df is None:
        return None
    pivot = pivot_data(df, main_topic, rows, columns, values, aggfunc)
    if pivot is None:
        return None
    
    return pivot

def generate_json_data(path: str):
    df = load_data(path)
    if df is None:
        return None

    top_10_posts_per_topic = (
        df.groupby("Topic")
        .apply(lambda x: x.nlargest(10, "Interactions"), include_groups=False)
    )
    top_10_posts_per_topic = top_10_posts_per_topic.reset_index().drop(columns="level_1")[['Topic', 'Title', 'Content', 'Description', 'UrlTopic', 'Channel', 'Interactions']]
    top_10_posts_per_topic = top_10_posts_per_topic.where(pd.notna(top_10_posts_per_topic), None)
    top_10_topics = top_10_posts_per_topic.groupby("Topic").apply(lambda x: x.to_dict(orient='records'), include_groups=False)
    top_10_topics.index = top_10_topics.index.map(lambda x: x.split('-')[0].strip())
    
    channel_breakdown = prepare_data(df, rows='Channel', columns=['Topic', 'Sentiment'], values='Id', aggfunc='count')
    label_breakdown = prepare_data(df, rows='Labels1', columns=['Topic', 'Sentiment'], values='Id', aggfunc='count')
    sentiment_breakdown = prepare_data(df, rows='Sentiment', values='Id', aggfunc='count')
    total = label_breakdown.sum().sum()
    
    final_dict = {
        "total": int(total),
        "sentiments": sentiment_breakdown['Id'].to_dict(),
        "details": []
    }
    all_details = []
    for topic in label_breakdown.columns.levels[0]:
        label_sentiments = label_breakdown[topic].to_dict(orient="index")
        channel_sentiments = channel_breakdown[topic].to_dict(orient="index")

        labels = [
            {
                "label": label,
                "total": int(sum(sentiments.values())),
                "sentiments": sentiments
            }
            for label, sentiments in label_sentiments.items()
        ]

        channels = [
            {  "channel": channel,
                "total": int(sum(sentiments.values())),
                "sentiments": sentiments
            }
            for channel, sentiments in channel_sentiments.items()
        ]

        detail = {
            "topic": topic,
            "total": int(label_breakdown[topic].sum().sum()),
            "percentage": round(label_breakdown[topic].sum().sum() / total * 100, 1),
            "sentiments": label_breakdown[topic].sum().to_dict(),
            "channels": channels,
            "labels": labels,
            "posts": top_10_topics.get(topic, [])
        }

        all_details.append(detail)

    sorted_details = sorted(all_details, key=lambda x: x["percentage"], reverse=True)
    final_dict["details"] = sorted_details
    
    jsonfile = json.dumps(final_dict, ensure_ascii=False, indent=2)
        
    return jsonfile

