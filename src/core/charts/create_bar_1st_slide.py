import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import pandas as pd
import numpy as np
from core.data_processing import prepare_data
from constants import BAR_CHANNEL_COLORS, MAP_CHANNELS
from io import BytesIO

def draw_stacked_bar(ax, channels, x_positions, df, bottom, top, label=False):
    WIDTH_BAR = 0.9
    height_rect = top / 8
    rect_distance = np.zeros(len(x_positions))
    for channel in channels:
        if channel in df.index: 
            values = df.loc[channel].astype(int).tolist() 
            if label:
                ax.bar(x_positions, values, bottom=bottom, color=BAR_CHANNEL_COLORS[channel],label=channel, width=WIDTH_BAR)
            else:
                ax.bar(x_positions, values, bottom=bottom, color=BAR_CHANNEL_COLORS[channel], width=WIDTH_BAR)
            for i, (x, val) in enumerate(zip(x_positions, values)):
                if val > 0:
                    if val < 10:
                        width_rect = 0.4
                    elif val < 100:
                        width_rect = 0.55
                    elif val < 1000:
                        width_rect = 0.7
                    elif val < 10000:
                        width_rect = 0.85
                    elif val < 100000:
                        width_rect = 1
                    else:
                        width_rect = 1.15

                    if rect_distance[i] > 0:
                        if val/2 > rect_distance[i]:
                            y = val / 2 
                            rect_distance[i] = val/2 + top / 8
                        else:
                            y  =  rect_distance[i]
                            rect_distance[i] += top / 8
                    else:
                        y = 0
                        rect_distance[i] += top / 8
                    
                    rect = plt.Rectangle((x - width_rect / 2, y), width_rect, height_rect, color=BAR_CHANNEL_COLORS[channel], linewidth=0.5, zorder=3)
                    ax.add_patch(rect)
                    ax.text(x,  y + height_rect/2, str(val), ha='center', va='center', fontsize=5, color='white', fontweight='bold', zorder=4)           
            bottom += values
    for x, total, position in zip(x_positions, bottom, rect_distance):
        ax.text(x, position * 1.1, str(int(total)), ha='center', va='bottom', fontsize=7, fontweight='bold', color='black')

def generate_stacked_bar_chart(current_data, previous_data) -> BytesIO: 
    if current_data is None or previous_data is None:
        print("No data available for stacked chart.")
        return None
    fig_width = 9.74
    fig_height = 2.18
    BAR_DISTANCE = 3
    try:
        current_channels = current_data.index.tolist()
        previous_channels = previous_data.index.tolist()
        channels = current_channels + [channel for channel in previous_channels if channel not in current_channels]

        current_topics = current_data.columns.unique().tolist()
        previous_topics = previous_data.columns.unique().tolist()
        topics = current_topics + [topic for topic in previous_topics if topic not in current_topics]
        current_data = current_data.reindex(columns=topics, fill_value=0)
        previous_data = previous_data.reindex(columns=topics, fill_value=0)
        fig, ax = plt.subplots(figsize=(fig_width * len(topics) / 8 , fig_height))
        fig.subplots_adjust(wspace=0.05)
        x_labels = ["Tuần này", "Tuần trước"] * len(topics)
        x_positions = []
        for i in range(len(topics)):
            base = i * BAR_DISTANCE
            x_positions.extend([base, base + 1])
        bottom = np.zeros(len(x_positions))
        max_value = max(current_data.iloc[:, :].sum().max(), previous_data.iloc[:, :].sum().max())
        draw_stacked_bar(ax, channels, x_positions[::2], current_data, bottom[::2], top=max_value, label=True)
        draw_stacked_bar(ax, channels, x_positions[1::2], previous_data, bottom[1::2], top=max_value, label=False)
        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.axhline(0, color='gray', linewidth=0.5)
        ax.tick_params(axis='x', length=2, width=0.5, colors='gray')
        ax.set_xticks(x_positions)
        ax.set_xticklabels(x_labels, fontsize=4.5, fontweight='bold', color='black')
        ax.set_xlim(-0.51, max(x_positions) + 0.51)
        ax.set_ylim(bottom=0)
        fig.subplots_adjust(top=0.6)
        legend_elements = [Patch(facecolor=BAR_CHANNEL_COLORS[channel], label=MAP_CHANNELS.get(channel, channel)) for channel in channels]
        ax.legend(
            handles=legend_elements,
            labels=[MAP_CHANNELS.get(channel, channel) for channel in channels],
            loc='upper right',
            bbox_to_anchor=(1.0, 1.3),
            ncol=len(channels),
            fontsize=6,
            frameon=False,
            handlelength=0.65,
            handletextpad=0.5,
            columnspacing=0.5,
        )
        ax.yaxis.set_visible(False)
        plt.tight_layout()
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
        plt.close(fig)
        buf.seek(0)
    except:
        print("Error generating stacked bar chart.")
        return None, None

    return buf, topics

def prepare_stacked_bar_data(current_df: pd.DataFrame, previous_df: pd.DataFrame, main_topic: str, rows: str, columns: str, values: str, aggfunc: str) -> pd.DataFrame:
    try:
        current_data = prepare_data(current_df, main_topic=main_topic, rows=rows, columns=columns, values=values, aggfunc=aggfunc)
        previous_data = prepare_data(previous_df, main_topic=main_topic, rows=rows, columns=columns, values=values, aggfunc=aggfunc)
        if current_data is None or previous_data is None:
            print("Error preparing data for stacked chart.")
            return None, None
        return current_data, previous_data
    except Exception as e:
        print(f"Error preparing stacked bar data: {e}")
        return None, None

 
