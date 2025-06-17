import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from data_processing import prepare_data
from utils import SENTIMENT_COLORS
from io import BytesIO
from matplotlib.patches import Patch


def draw_stacked_bar_5th(ax, df, sentiments, x_positions):
    bottom = np.zeros(len(x_positions))
    rect_distance = np.zeros(len(x_positions))
    y_positions = np.zeros(len(x_positions))
    WIDTH_BAR = 0.7
    HEIGHT_RECT = 4.8
    for sentiment in sentiments:
        sizes = df[sentiment].tolist()

        ax.bar(x_positions, sizes, bottom=bottom, color=SENTIMENT_COLORS[sentiment], label=sentiment, width=WIDTH_BAR)
        
        for i, (x, size) in enumerate(zip(x_positions, sizes)):
            if size > 0:
                if size < HEIGHT_RECT:
                    if bottom[i] == 0:
                        y_positions[i] = HEIGHT_RECT / 2
                        rect_distance[i] += HEIGHT_RECT
                    else:
                        y_positions[i] = rect_distance[i] + HEIGHT_RECT / 2
                        rect_distance[i] += HEIGHT_RECT
                else:
                    if size / 2 >= rect_distance[i] + HEIGHT_RECT / 2:
                        y_positions[i] = bottom[i] + size / 2
                        rect_distance[i] = bottom[i] + size
                    else:
                        y_positions[i] = rect_distance[i] + HEIGHT_RECT / 2
                        rect_distance[i] += HEIGHT_RECT
        
        for i in range(len(x_positions)):
            if sizes[i] > 0:
                width_rect = WIDTH_BAR * 0.8           
                rect = plt.Rectangle(
                    (x_positions[i] - width_rect / 2, y_positions[i] - HEIGHT_RECT / 2),
                    width_rect, HEIGHT_RECT,
                    facecolor=SENTIMENT_COLORS[sentiment],
                    linewidth=0.5,
                    zorder=3
                )
                ax.add_patch(rect)
                label = f'{sizes[i]}%'

                ax.text(
                    x_positions[i], y_positions[i],
                    label,
                    ha='center', va='center',
                    fontsize=5.5, color='white', fontweight='bold',
                    zorder=4
                )
        bottom += sizes

def prepare_stacked_bar_data_5th(current_df: pd.DataFrame, main_topic: str, rows: str, columns: str, values: str, aggfunc: str) -> pd.DataFrame:
    current_data = prepare_data(current_df, main_topic=main_topic, rows=rows, columns=columns, values=values, aggfunc=aggfunc)
    if current_data is None:
        print("Error preparing data for stacked bar chart.")
        return None
    return current_data[main_topic]

def generate_stacked_bar_chart_5th(data) -> BytesIO:
    if data is None:
        print("No data available for stacked chart.")
        return None
    FIGSIZE = (9.74, 2.18)
    fig, ax = plt.subplots(figsize=FIGSIZE)
    total_mentions = data.sum().sum()
    data['Total'] = data.sum(axis=1)
    top_data = data.sort_values(
        by='Total', 
        ascending=False
    ).head(6)
    percentage_data = round(top_data / total_mentions * 100, 2)
    sentiments = percentage_data.columns[:-1].tolist() 
    x_labels = percentage_data.index.unique().tolist()
    x_positions = []
    for i in range(len(x_labels)):
        base = i * 2
        x_positions.extend([base])
    draw_stacked_bar_5th(ax, percentage_data, sentiments, x_positions)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.axhline(0, color='gray', linewidth=0.5)
    ax.tick_params(axis='x', length=0, width=0)
    ax.set_xticks(x_positions)
    x_labels = [f"{x_label.split(" ")[0]}..."  if len(x_label) > 10 else x_label for x_label in x_labels]  # Giới hạn độ dài nhãn
    ax.set_xticklabels(x_labels, fontsize = 5.5, fontweight='bold', color='black', rotation=45, ha='right')
    ax.set_xlim(-0.8 , max(x_positions) + 0.8)
    ax.set_ylim(0, 35)
    ax.yaxis.set_visible(False)
    legend_elements = [Patch(facecolor=SENTIMENT_COLORS[sentiment], label=sentiment) for sentiment in sentiments]
    fig.legend(
        handles=legend_elements,
        labels=sentiments,
        loc='lower center',
        bbox_to_anchor=(0.5, -0.05),
        ncol=len(sentiments),
        prop={'weight': 'bold', 'size': 6},  
        frameon=False,
        handlelength=0.65,
        handletextpad=0.5,
        columnspacing=1.5
    )
    plt.tight_layout()
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)

    return buf
   