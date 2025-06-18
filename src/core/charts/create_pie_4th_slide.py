import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from core.data_processing import prepare_data, load_data
from constants import SUNBURST_CHANNEL_COLORS, SENTIMENT_COLORS, MAP_SENTIMENTS, MAP_CHANNELS
from io import BytesIO
from matplotlib.patches import Rectangle, Patch


def draw_doughnut(ax, radius, values, labels, colors, width=0.35):
    sizes = np.round(values / values.sum() * 100, 1)
    color_values = [colors[label] for label in labels]

    wedges, _ = ax.pie(
        sizes,
        labels=None,
        radius=radius,
        startangle=90,
        colors=color_values,
        wedgeprops=dict(width=width, edgecolor='white')
    )

    THRESHOLD = 16
    RECT_WIDTH = 0.45
    RECT_HEIGHT = 0.3
    angle_radians = []
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
        x, y = radius * np.cos(angle_radians[i]), radius * np.sin(angle_radians[i])
        if y > 0:
            y -= RECT_HEIGHT / 2
        rect = Rectangle((x - 0.15, y), RECT_WIDTH, RECT_HEIGHT,
                         color=color_values[i], ec='white', linewidth=0.5, zorder=3)
        ax.add_patch(rect)
        ax.text(x - 0.15 + RECT_WIDTH / 2, y + RECT_HEIGHT / 2,
                f'{sizes[i]}%', ha='center', va='center',
                fontsize=6.5, color='white', fontweight='bold', zorder=4)

def draw_legend(ax, labels, colors, title, bbox_anchor):
    legend_elements = [Patch(facecolor=colors[label], label=label) for label in labels]

    legend = ax.legend(
        title=title,
        handles=legend_elements,
        labels=labels,
        loc='center left',
        bbox_to_anchor=bbox_anchor,
        ncol=1,
        fontsize=8,
        frameon=True,
        handlelength=0.65,
        handletextpad=0.5,
        title_fontsize=9
    )
    legend.get_title().set_fontweight('bold')
    legend._legend_box.sep = 8

def draw_connection_arrow(ax, direction='right', total=0, text_label='THẢO LUẬN', percentage=None, color='#000000'):
    formatted_total = f"{total:,}" if total >= 1000 else str(total)
    if direction == 'right':
        x = [0, 1.5, 1.5]
        y = [0, 0, -0.254]
        ax.annotate('', xy=(3, -0.254), xytext=(1.45, -0.254),
                    arrowprops=dict(arrowstyle='-|>', color='#DDDDDD', lw=1))
        ax.text(2.3, 0.1, formatted_total, ha='center', va='center', fontsize=15, color='black', fontweight='bold')
        ax.text(2.3, -0.12, text_label, ha='center', va='center', fontsize=5, color='black', fontweight='bold')
        if percentage is not None:
            ax.text(2.3, -0.5, f"{percentage}%", ha='center', va='center', fontsize=10, color=color, fontweight='bold')
            ax.text(2.3, -0.75, 'so với tuần trước', ha='center', va='center', fontsize=10, color='#DDDDDD')
    else:
        x = [0, -1.5, -1.5]
        y = [0, 0, -0.254]
        ax.annotate('', xy=(-3, -0.254), xytext=(-1.45, -0.254),
                    arrowprops=dict(arrowstyle='-|>', color='#DDDDDD', lw=1))
        ax.text(-2.3, 0.1, formatted_total, ha='center', va='center', fontsize=15, color='black', fontweight='bold')
        ax.text(-2.3, -0.12, text_label, ha='center', va='center', fontsize=5, color='black', fontweight='bold')
        if percentage is not None:
            ax.text(-2.3, -0.5, f"{percentage}%", ha='center', va='center', fontsize=10, color=color, fontweight='bold')
            ax.text(-2.3, -0.75, 'so với tuần trước', ha='center', va='center', fontsize=10, color='#DDDDDD')
    ax.plot(0, 0, 'o', color='#DDDDDD', markersize=5)
    ax.plot(x, y, color='#DDDDDD', linewidth=1)

def setup_axes(ax, xlim, ylim):
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect('equal')
    ax.axis('off')

def render_single_chart(ax, df_sentiment, df_channel, legend_labels, colors_sentiment, colors_channel, colors_legend,
                        direction='right', legend_title='Sắc thái', bbox_anchor=(0, 0.4), total_last_week=None):
    
    draw_doughnut(ax, 1, df_sentiment.iloc[0, :].values, df_sentiment.columns.to_list(), colors_sentiment)
    draw_doughnut(ax, 1.4, df_channel.iloc[0, :].values, df_channel.columns.to_list(), colors_channel, width=0.45)
    draw_legend(ax,legend_labels, colors_legend, title=legend_title, bbox_anchor=bbox_anchor)
    total_value = df_sentiment.iloc[0, :].values.sum()
    if total_last_week is not None:   
        percent_diff = np.round(((total_value - total_last_week) / total_last_week) * 100, 0) if total_last_week != 0 else 0
        compare_text = f"{int(percent_diff)}%" if percent_diff < 0 else f"+{int(percent_diff)}%"
        compare_color = '#ff0000' if percent_diff < 0 else '#1EAB4D'  
        draw_connection_arrow(ax, direction=direction, total=total_value, percentage=compare_text, color=compare_color)
    else:
        draw_connection_arrow(ax, direction=direction, total=total_value, text_label='THẢO LUẬN')
    setup_axes(ax, xlim=(-3, 3), ylim=(-2, 2))

def prepare_nested_data(current_data, previous_data, main_topic):
    try:
        current_sentiment_data = prepare_data(current_data, 
            main_topic=main_topic, 
            columns=['Topic', 'Sentiment'], 
            values='Id', 
            aggfunc='count'
        )
        current_channel_data = prepare_data(current_data, 
            main_topic=main_topic, 
            columns=['Topic', 'Channel'], 
            values='Id', 
            aggfunc='count'
        )

        previous_sentiment_data = prepare_data(previous_data,
            main_topic=main_topic, 
            columns=['Topic', 'Sentiment'],
            values='Id', 
            aggfunc='count'
        )
        previous_channel_data = prepare_data(previous_data,
            main_topic=main_topic, 
            columns=['Topic', 'Channel'], 
            values='Id', 
            aggfunc='count'
        )
        if current_sentiment_data is None or current_channel_data is None or \
        previous_sentiment_data is None or previous_channel_data is None:
            print("Error preparing data for nested chart.")
            return None, None, None, None
        return current_sentiment_data[main_topic], current_channel_data[main_topic], previous_sentiment_data[main_topic], previous_channel_data[main_topic]
    except Exception as e:
        print(f"Error preparing nested data: {e}")
        return None, None, None, None
        
def generate_nested_chart(current_sentiment_data, current_channel_data, previous_sentiment_data, previous_channel_data):
    fig, (ax_left, ax_right) = plt.subplots(1, 2, figsize=(10, 5))
    try:
        current_channels = current_channel_data.columns.tolist()
        previous_channels = previous_channel_data.columns.tolist()
        channels = current_channels + [channel for channel in previous_channels if channel not in current_channels]
        current_channel_data = current_channel_data.reindex(columns=channels, fill_value=0)
        previous_channel_data = previous_channel_data.reindex(columns=channels, fill_value=0)
        render_single_chart(
            ax=ax_left,
            df_sentiment=current_sentiment_data,
            df_channel=current_channel_data,
            legend_labels=[MAP_CHANNELS.get(channel, channel) for channel in current_channel_data.columns.tolist()],
            colors_sentiment=SENTIMENT_COLORS,
            colors_channel=SUNBURST_CHANNEL_COLORS,
            colors_legend={MAP_CHANNELS.get(channel, channel): SUNBURST_CHANNEL_COLORS[channel] for channel in SUNBURST_CHANNEL_COLORS},
            direction='right',
            legend_title='Channel',
            bbox_anchor=(0, 0.4),
            total_last_week=previous_channel_data.iloc[0, :].values.sum()
        )
        render_single_chart(
            ax=ax_right,
            df_sentiment=previous_sentiment_data,
            df_channel=previous_channel_data,
            legend_labels=[MAP_SENTIMENTS[sentiment] for sentiment in previous_sentiment_data.columns.tolist()],
            colors_sentiment=SENTIMENT_COLORS,
            colors_channel=SUNBURST_CHANNEL_COLORS,
            colors_legend={MAP_SENTIMENTS[sentiment]: SENTIMENT_COLORS[sentiment] for sentiment in SENTIMENT_COLORS},
            direction='left',
            legend_title='Sắc thái',
            bbox_anchor=(0.8, 0.4)
        )

        buf = BytesIO()
       
        plt.tight_layout()
        plt.show()
        plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
        plt.close(fig)
        buf.seek(0)

        return buf
    except Exception as e:
        print(f"Error rendering current chart: {e}")
        return None