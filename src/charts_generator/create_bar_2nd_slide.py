import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from data_processing import prepare_data
from utils import SENTIMENT_COLORS
from io import BytesIO


def draw_stacked_bar(ax, df, sentiments, x_positions, bottom):
    
    y_positions = np.zeros(len(x_positions))
    rect_distance = np.zeros(len(x_positions))
    x = [pos - 0.25 for pos in x_positions]  
    WIDTH_BAR = 0.8
    HEIGHT_RECT = 10
    for sentiment in sentiments:
        values = df[sentiment].astype(int).tolist()
        sizes = [
            round((v / t) * 100, 1) if t != 0 else 0
            for v, t in zip(df[sentiment], df['Total'])
        ]
        ax.bar(x, sizes, bottom=bottom, color=SENTIMENT_COLORS[sentiment], label=sentiment, width=WIDTH_BAR)
        for i, size in enumerate(sizes):
            if size > 0:
                if size < HEIGHT_RECT:
                    y_positions[i] = rect_distance[i] + HEIGHT_RECT / 2
                    rect_distance[i] += HEIGHT_RECT
                else:
                    center_pos = bottom[i] + size / 2
                    if center_pos >= rect_distance[i] + HEIGHT_RECT / 2:
                        y_positions[i] = center_pos
                        rect_distance[i] = bottom[i] + size
                    else:
                        y_positions[i] = rect_distance[i] + HEIGHT_RECT / 2
                        rect_distance[i] += HEIGHT_RECT

        for i in range(0, len(x_positions), 2):
            if sizes[i] > 0:
                if i + 1 < len(x_positions):
                    offset = 12
                    if sizes[i] > sizes[i + 1]:
                        rect_distance[i] = max(rect_distance[i + 1] + offset, rect_distance[i]) if rect_distance[i] <= y_positions[i] + HEIGHT_RECT / 2 else rect_distance[i]
                        y_positions[i] = max(y_positions[i + 1] + offset, y_positions[i])
                        
                    else:
                        y_positions[i + 1] = max(y_positions[i] + offset, y_positions[i + 1])
                        rect_distance[i + 1] = max(rect_distance[i] + offset, rect_distance[i + 1]) if rect_distance[i + 1] <= y_positions[i + 1] + HEIGHT_RECT / 2 else rect_distance[i  + 1]

        for i in range(len(x_positions)):
            if sizes[i] > 0:
                width_rect = WIDTH_BAR * (1.4 if values[i] < 100 else 1.6 if values[i] < 1000 else 1.8)

                rect = plt.Rectangle(
                    (x[i] - width_rect / 2, y_positions[i] - HEIGHT_RECT / 2),
                    width_rect, HEIGHT_RECT,
                    facecolor=SENTIMENT_COLORS[sentiment],
                    linewidth=0.5,
                    zorder=3
                )
                ax.add_patch(rect)

                label = f'{values[i]}, {sizes[i]}%'
                ax.text(
                    x[i], y_positions[i],
                    label,
                    ha='center', va='center',
                    fontsize=4.5, color='white', fontweight='bold',
                    zorder=4
                )

        bottom += sizes

def prepare_stacked_bar_data_2nd(current_df: pd.DataFrame, previous_df: pd.DataFrame, main_topic: str, rows: str, columns: str, values: str, aggfunc: str) -> pd.DataFrame:
    current_data = prepare_data(current_df, main_topic=main_topic, rows=rows, columns=columns, values=values, aggfunc=aggfunc)
    previous_data = prepare_data(previous_df, main_topic=main_topic, rows=rows, columns=columns, values=values, aggfunc=aggfunc)
    if current_data is None or previous_data is None:
        print("Error preparing data for stacked chart.")
        return None
    current_topics = current_data.columns.tolist()
    previous_topics = previous_data.columns.tolist()
    topics = current_topics + [topic for topic in previous_topics if topic not in current_topics]

    current_data = current_data.reindex(columns=topics, fill_value=0)
    previous_data = previous_data.reindex(columns=topics, fill_value=0)
    
    merged = pd.concat([current_data.T, previous_data.T])
    merged = merged.sort_index(kind='stable', ascending=False) 
    shb_rows = merged[merged.index == "SHB"]

    other_rows = merged[merged.index != "SHB"]

    result = pd.concat([shb_rows, other_rows])
    
    return result

def generate_stacked_bar_chart_2nd(data) -> BytesIO: 
    if data is None:
        print("No data available for stacked chart.")
        return None
    topics = data.index.unique().tolist()
    FIGSIZE = (9.74 * len(topics) / 8, 2.18)
    BAR_DISTANCE = 3

    fig, ax = plt.subplots(figsize=FIGSIZE)
    sentiments = data.columns.tolist()
    data['Total'] = data.sum(axis=1)

    
    x_labels = ["Tuần này", "Tuần trước"] * len(topics)
    x_positions = []
    for i in range(len(topics)):
        base = i * BAR_DISTANCE
        x_positions.extend([base, base + 1])
    bottom = np.zeros(len(x_positions))

    draw_stacked_bar(ax, data, sentiments, x_positions, bottom)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.axhline(0, color='gray', linewidth=0.5)
    ax.tick_params(axis='x', length=0, width=0)
    ax.set_xticks(x_positions)
    ax.set_xticklabels(x_labels, fontsize=4.5, fontweight='bold', color='black', rotation=45, ha='right')
    ax.set_xlim(-1, max(x_positions) + 0.8)
    ax.set_ylim(bottom=0)
    ax.yaxis.set_visible(False)

    plt.tight_layout()
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return buf, topics

