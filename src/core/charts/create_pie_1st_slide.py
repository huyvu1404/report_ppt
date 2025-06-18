from io import BytesIO
import numpy as np
import pandas as pd
from pydantic import BaseModel
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from core.data_processing import prepare_data
from constants import TOPIC_COLORS

def draw_doughnut(ax, channels, df, total_compare, title, position):
    RECT_WIDTH = 0.41
    RECT_HEIGHT = 0.18
    TOTAL_POSITION = (0, 0.1)
    BELOW_TEXT_POSITION = (0, -0.15)
    COMPARE_TEXT_POSITION = (0, -0.4)

    if position == 'left':
        xtitle, ytitle = -1.3, -1.25
    else:
        xtitle, ytitle = 1.3, -1.25

    total = df.sum().sum()
    sizes = np.round(df.iloc[0, :].tolist() / total * 100, 1)
    color_values = [TOPIC_COLORS[channel] for channel in channels]
    wedges, _ = ax.pie(sizes, labels=None, startangle=90, colors=color_values, wedgeprops=dict(width=0.35, edgecolor='white'))
    angle_radians = []
    THRESHOLD = 16
    for i, wedge in enumerate(wedges):
        if sizes[i] == 0:
            angle_radians.append(0)
            continue
        if i == 0:
            start = wedge.theta1  
            end = wedge.theta2
            if end - start < THRESHOLD:
                angle = start + THRESHOLD / 2
                start += THRESHOLD
            else: 
                angle = (start + end) / 2
                start = end
        else:
            end = wedge.theta2
            if end - start < THRESHOLD:
                angle = start + THRESHOLD / 2
                start += THRESHOLD
            else:
                angle = (start + end) / 2
                start = end
        angle_radians.append(np.radians(angle)) 
    for i in range(len(wedges)):
        if sizes[i] == 0:
            continue
        x, y = np.cos(angle_radians[i]), np.sin(angle_radians[i])
        if y > 0:
            y -= RECT_HEIGHT / 2
        rect = plt.Rectangle((x - 0.15, y), RECT_WIDTH, RECT_HEIGHT, color=color_values[i], ec='white', linewidth=0.5, zorder=3)
        ax.add_patch(rect)
        ax.text(x - 0.15 + RECT_WIDTH / 2, y + RECT_HEIGHT / 2, f'{sizes[i]}%', ha='center', va='center', fontsize=5, color='white', fontweight='bold', zorder=4)


    compare_value = total - total_compare
    percent_diff = np.round((compare_value / total_compare) * 100, 0) if total_compare != 0 else 0
    compare_text = f"{percent_diff}%" if percent_diff < 0 else f"+{percent_diff}%"
    compare_color = '#ff0000' if percent_diff < 0 else '#1EAB4D'
    
    ax.text(xtitle, ytitle, title, ha=position, va='bottom', fontsize=8, fontweight='bold', color='#00AEEF')
    ax.text(TOTAL_POSITION[0], TOTAL_POSITION[1], f"{total:,.0f}", ha='center', va='center', fontsize=16, fontweight='bold', color='#00AEEF')
    ax.text(BELOW_TEXT_POSITION[0], BELOW_TEXT_POSITION[1], "THẢO LUẬN", ha='center', va='center', fontsize=8, fontweight='bold', color='#00AEEF')
    ax.text(COMPARE_TEXT_POSITION[0], COMPARE_TEXT_POSITION[1], compare_text, ha='center', va='center', fontsize=10, fontweight='bold', color=compare_color)

def generate_doughnut_chart(current_data, previous_data) -> BytesIO: 
    if current_data is None or previous_data is None:
        print("No data available for doughnut chart.")
        return None
    try:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(5, 2.5))
        fig.subplots_adjust(wspace=0.05)
        current_channels = current_data.columns.tolist()
        previous_channels = previous_data.columns.tolist()
        channels = current_channels + [channel for channel in previous_channels if channel not in current_channels]
        current_data = current_data.reindex(columns=channels, fill_value=0)
        previous_data = previous_data.reindex(columns=channels, fill_value=0)
        draw_doughnut(ax1, channels, current_data, total_compare=previous_data.sum().sum(), title="Tuần này", position='left')
        draw_doughnut(ax2, channels, previous_data, total_compare=current_data.sum().sum(), title="Tuần trước", position='right')
        
        fig.legend(labels = channels, loc='upper center', bbox_to_anchor=(0.5, 0.1), ncol=len(channels), fontsize=4, frameon=False, handlelength=0.65, handletextpad=0.5, columnspacing=0.5)
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
        plt.close(fig) 
        buf.seek(0)
        return buf 
    except Exception as e:
        print(f"Error generating doughnut chart: {e}")
        return None

def prepare_doughnut_data(current_data: pd.DataFrame, previous_data: pd.DataFrame, main_topic: str, columns: str, values: str, aggfunc: str) -> pd.DataFrame:
    try:
        current_data = prepare_data(current_data, main_topic=main_topic, columns=columns, values=values, aggfunc=aggfunc)
        previous_data = prepare_data(previous_data, main_topic=main_topic, columns=columns, values=values, aggfunc=aggfunc)
        if current_data is None or previous_data is None:
            print("Error preparing data for doughnut chart.")
            return None
        return current_data, previous_data
    except Exception as e:
        print(f"Error preparing doughnut data: {e}")
        return None, None
