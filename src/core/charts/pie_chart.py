import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pydantic import BaseModel
from typing import Optional, Union, List
from core.data_processing import prepare_data
from core.models import PieChartData, PieLabelConfig

def draw_pie_label(ax, config: PieLabelConfig):
    SHAPE_ZORDER, TEXT_ZORDER = 3, 4
    SHAPE_LINE_WIDTH = 0.5
    FONT_SIZE = 5

    wedges, sizes, colors, label_sizes, threshold = config.wedges, config.sizes, config.colors, \
                                                    config.label_sizes, config.threshold
    width, height = label_sizes
    angle_radians = []
    start = wedges[0].theta1
    for i, wedge in enumerate(wedges):
        if sizes[i] == 0:
            angle_radians.append(0)
            continue

        end = wedge.theta2
        span = end - start
        if span < threshold:
            angle = start + threshold / 2
            start += threshold
        else:
            angle = (start + end) / 2
            start = end

        angle_radians.append(np.radians(angle))

    for i, angle in enumerate(angle_radians):
        if sizes[i] == 0:
            continue

        x, y = np.cos(angle), np.sin(angle)
        y -= height / 2 if y > 0 else 0

        rect = plt.Rectangle((x - 0.15, y), width, height,
                            color=colors[i], ec='white',
                            linewidth=SHAPE_LINE_WIDTH, zorder=SHAPE_ZORDER)
        ax.add_patch(rect)

        ax.text(x - 0.15 + width / 2, y + height / 2,
                f'{sizes[i]}%', ha='center', va='center',
                fontsize=FONT_SIZE, color='white',
                fontweight='bold', zorder=TEXT_ZORDER)


class DoughnutChartGenerator(BaseModel):
    current_data: pd.DataFrame
    previous_data: pd.DataFrame
    main_topic: str
    rows: Optional[Union[str, List[str]]] = None
    columns: Optional[Union[str, List[str]]] = None
    values: str
    aggfunc: str


    def prepare_data(self):
        try:
            self.current_data = prepare_data(
                self.current_data,
                main_topic=self.main_topic,
                columns=self.columns,
                values=self.values,
                aggfunc=self.aggfunc
            )
            self.previous_data = prepare_data(
                self.previous_data,
                main_topic=self.main_topic,
                columns=self.columns,
                values=self.values,
                aggfunc=self.aggfunc
            )
            if self.current_data is None or self.previous_data is None:
                print("Error preparing data for doughnut chart.")
                return False
            
            return True
        except Exception as e:
            print(f"Error preparing doughnut data: {e}")
            return False

        
    def setup_figure(self, ncols: int = 1, nrows: int = 2, fig_width: float = 5, fig_height: float = 2.5):
        fig, axs = plt.figure(ncols, nrows, figsize=(fig_width, fig_height))
        fig.subplots_adjust(wspace=0.05)
        return fig, axs

    def draw_doughnut(self, ax: plt.Axes, label_sizes, threshold, data: PieChartData):
        wedges, _ = ax.pie(
            data.sizes,
            labels=None,
            startangle=data.startangle,
            colors=data.colors,
            wedgeprops=dict(width=float(data.wedgeprops.get("width")), edgecolor=data.wedgeprops.get("edgecolor"))
        )
        label_configs = PieLabelConfig(
            wedges=wedges,
            sizes=data.sizes,
            colors=data.colors,
            label_sizes=label_sizes,
            threshold=threshold
        )
        draw_pie_data_label(ax, label_configs)
        

    # def generate(self) -> BytesIO:
    #     fig, axs = self.setup_figure()
    #     if not self.prepare_data():
    #         return None
        
    #     current_data, previous_data = prepare_doughnut_data(
    #         self.current_data, self.previous_data, self.main_topic, self.columns, self.values, self.aggfunc
    #     )
    #     return generate_doughnut_chart(current_data, previous_data)
