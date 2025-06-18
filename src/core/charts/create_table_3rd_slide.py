import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.patches import Patch
import pandas as pd
import numpy as np
from core.data_processing import prepare_data
from constants import SENTIMENT_COLORS, MAP_SENTIMENTS
from io import BytesIO

def draw_table(axs, data, topics, sentiments, n_rows=11):
    ROW_HEIGHT = 1.4
    ROW_WIDTH = 110
   
    y = np.arange(0, 1.4 * n_rows, 1.4)
    y_middle = y - 0.7
    for i, (ax, topic) in enumerate(zip(axs, topics)):
        for spine in ax.spines.values():
            spine.set_visible(False)
        
        xmin = -120 if i == 0 else 0
        ax.set_xlim(xmin, ROW_WIDTH)
        ax.set_ylim(-1.2, n_rows*1.3)
        ax.hlines(y=y[:-1], xmin=xmin, xmax=ROW_WIDTH, colors='gray', linestyles='-', linewidth=1, alpha=0.7, zorder=0)
        ax.vlines(x=0, ymin=-1.4, ymax=n_rows * 1.4, colors='gray', linestyles='-', linewidth=1, alpha=0.7, zorder=1)
        ax.set_yticklabels([])
        ax.set_xticks([])
        ax.tick_params(axis='x', which='both', length=0)
        ax.tick_params(axis='y', which='both', length=0)
        
        bottom = np.full((n_rows,), 4.0)
        df = data[topic].fillna(0)
        for sentiment in sentiments:
            values = np.round(df[sentiment].tolist(), 1)[::-1]
            ax.barh(y_middle, values, left=bottom, color=SENTIMENT_COLORS[sentiment], height=0.8, zorder=10)
            bottom += values
        for k, bottom in enumerate(bottom):
            x_pos = bottom + 15
            y_pos = y_middle[k]
            if bottom - 4 > 0:
                ax.text(x_pos, y_pos, f'{round(bottom - 4, 2)}%', ha='center', va='center', 
                    fontsize=10, color='black', fontweight='bold', zorder=20)

def prepare_table_data(data, main_topic, rows, columns, values, aggfunc):
    try:
        pivot_data = prepare_data(data, main_topic=main_topic, rows=rows, columns=columns, values=values, aggfunc=aggfunc)
        if pivot_data is None:
            print("Error preparing data for horizontal bar chart.")
            return None
        totals = {group: pivot_data[group].sum().sum() for group in pivot_data.columns.levels[0]}

        pivot_data_normalized = pivot_data.copy()
        for group in pivot_data.columns.levels[0]:
            pivot_data_normalized[group] = np.round(pivot_data[group] / totals[group] * 100, 1)
        indexes = pivot_data_normalized[main_topic].sum(axis=1).sort_values(ascending=False).head(11).index.tolist()
        filtered_data = pivot_data_normalized.loc[indexes,:]
        return filtered_data
    except Exception as e:
        print(f"Error preparing data for horizontal bar chart: {e}")
        return None
    
def generate_table(data):
    if data is None:
        print("No data available for horizontal bar chart.")
        return None
    try:
        labels = data.index.tolist()
        topics = data.columns.map(lambda x: x[0]).unique().to_list()
        sentiments = data.columns.map(lambda x: x[1]).unique().tolist()
        n_rows, n_cols = len(labels), len(topics)
        fig = plt.figure(figsize=(22, 8))
        WIDTH_RATIOS = [2, 0.8, 1.1, 1, 1.1, 1, 1.2, 0.95][:n_cols]
        
        gs = GridSpec(1, len(topics), width_ratios=WIDTH_RATIOS, wspace=0)
        
        first_ax = fig.add_subplot(gs[0])
        axs = [first_ax]
        for i in range(1, n_cols):
            ax = fig.add_subplot(gs[i], sharey=first_ax)
            axs.append(ax)

        draw_table(axs, data, topics, sentiments, n_rows=n_rows)
        legend_elements = [Patch(facecolor=SENTIMENT_COLORS[sentiment], label=MAP_SENTIMENTS[sentiment]) for sentiment in sentiments]
        fig.legend(
            handles=legend_elements,
            labels=[MAP_SENTIMENTS[sentiment] for sentiment in sentiments],
            loc='lower center',
            bbox_to_anchor=(0.5, 0.07),
            ncol=len(sentiments),
            prop={'weight': 'bold', 'size': 10},  
            frameon=False,
            handlelength=0.65,
            handletextpad=0.5,
            columnspacing=1.5
        )
        buf = BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight', dpi=300)
        plt.close(fig)
        buf.seek(0)
        
        return buf, topics, labels, WIDTH_RATIOS
    except Exception as e:
        print(f"Error generating horizontal bar chart: {e}")
        return None, None, None, None
