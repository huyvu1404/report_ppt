import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from core.data_processing import prepare_data
from constants import SENTIMENT_COLORS, MAP_SENTIMENTS
from io import BytesIO
from matplotlib.patches import Patch

def draw_stacked_bar(ax, df, sentiments, x_positions, bottom):
    
    y_positions = np.zeros(len(x_positions))
    prev_y = np.zeros(len(x_positions))
    # rect_distance = np.zeros(len(x_positions))
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
            prev_y = y_positions[i]
            if size > 0:
                y_positions[i] = bottom[i] + size / 2
                if y_positions[i] - prev_y < HEIGHT_RECT / 2:
                    if bottom[i] == 0:
                        y_positions[i] = HEIGHT_RECT / 2
                    else:
                        y_positions[i] = prev_y + HEIGHT_RECT
        
        
            # if size > 0:
            #     if size < HEIGHT_RECT:
            #         y_positions[i] = rect_distance[i] + HEIGHT_RECT / 2
            #         rect_distance[i] += HEIGHT_RECT
            #     else:
            #         center_pos = bottom[i] + size / 2
            #         if center_pos >= rect_distance[i] + HEIGHT_RECT / 2:
            #             y_positions[i] = center_pos
            #             rect_distance[i] = bottom[i] + size
            #         else:
            #             y_positions[i] = rect_distance[i] + HEIGHT_RECT / 2
            #             rect_distance[i] += HEIGHT_RECT
        offset = 12
        for i in range(0, len(x_positions), 2):
            if (values[i] > 100 and len(str(sizes[i])) > 3) or (values[i] > 1000 and len(str(sizes[i])) > 2):
                if i + 1 < len(x_positions):
                    if sizes[i] > sizes[i + 1]:
                        # rect_distance[i] = max(rect_distance[i + 1] + offset, rect_distance[i]) if rect_distance[i] <= y_positions[i] + HEIGHT_RECT / 2 else rect_distance[i]
                        y_positions[i] = min(max(y_positions[i + 1] - offset, HEIGHT_RECT / 2), y_positions[i])
                        
                    else:
                        y_positions[i + 1] = min(max(y_positions[i] - offset, HEIGHT_RECT / 2), y_positions[i + 1])
                        # rect_distance[i + 1] = max(rect_distance[i] + offset, rect_distance[i + 1]) if rect_distance[i + 1] <= y_positions[i + 1] + HEIGHT_RECT / 2 else rect_distance[i  + 1]
        scaling = 0.12
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

                  # Tùy vào fontsize
                distance = (len(str(values[i])) + 1) * scaling

                ax.text(
                    x[i] - width_rect / 3, y_positions[i],
                    f'{values[i]};',
                    ha='left', va='center',
                    fontsize=4.5, color='yellow', fontweight='bold',
                    zorder=4
                )
                ax.text(
                    x[i] - width_rect / 3 + distance, y_positions[i],
                    f'{sizes[i]}%',
                    ha='left', va='center',
                    fontsize=4.5, color='white', fontweight='bold',
                    zorder=4
                )
        bottom += sizes
        

def prepare_stacked_bar_data_2nd(current_df: pd.DataFrame, previous_df: pd.DataFrame, main_topic: str, rows: str, columns: str, values: str, aggfunc: str) -> pd.DataFrame:
    try:    
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
    except Exception as e:
        print(f"Error preparing data for stacked bar chart: {e}")
        return None

def generate_stacked_bar_chart_2nd(data) -> BytesIO: 
    if data is None:
        print("No data available for stacked chart.")
        return None
    topics = data.index.unique().tolist()
    FIGSIZE = (9.74 * len(topics) / 8, 2.18)
    BAR_DISTANCE = 3
    try:
        fig, ax = plt.subplots(figsize=FIGSIZE)
        sentiments = ["Positive", "Neutral", "Negative"]
        data = data[sentiments].copy()
        
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

        legend1 = [
            Patch(facecolor='yellow', edgecolor='black', label='Số lượng thảo luận'),
            Patch(facecolor='white', edgecolor='black', label='Tỉ lệ (%)')  
        ]
        legend_obj1 = ax.legend(
            handles=legend1,
            loc='upper right',
            bbox_to_anchor=(1, 1.15),  # dịch lên trên một chút
            fontsize=6,
            frameon=False,
            ncol=2,
            handlelength=0.65,
            handletextpad=0.5,
            columnspacing=0.5,
        )

        # Thêm legend1 thủ công vào ax
        ax.add_artist(legend_obj1)

        legend_elements = [
            Patch(facecolor=SENTIMENT_COLORS[sentiment], label=MAP_SENTIMENTS[sentiment])
            for sentiment in sentiments
        ]
        ax.legend(
            handles=legend_elements,
            ncols=3,
            loc='upper left',
            bbox_to_anchor=(0, 1.12),  
            fontsize=6,
            frameon=False,
            handlelength=0.65,
            handletextpad=0.5,
            columnspacing=0.5,
        )
        plt.tight_layout()
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
        plt.close(fig)
        buf.seek(0)
        return buf, topics
    except Exception as e:
        print(f"Error generating stacked bar chart: {e}")
        return None, None

