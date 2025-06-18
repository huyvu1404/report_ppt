import pandas as pd
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import matplotlib.pyplot as plt

class PieChartData(BaseModel):
    sizes: List[float] = Field(..., description="Sizes of each wedge in the pie chart.")
    colors: List[str] = Field(..., description="Colors corresponding to each wedge in the pie chart.")
    startangle: int = Field(90, description="Starting angle for the pie chart.")
    wedgeprops: Dict[str, str] = Field(
        default_factory=lambda: {"width": "0.35", "edgecolor": "white"},
        description="Properties for the wedges in the pie chart."
    )
    radius: float = Field(1.0, description="Radius of the pie chart.")

class PieLabelConfig(BaseModel):
    wedges: List[plt.patches.Wedge] = Field(..., description="List of wedges in the pie chart.")
    sizes: List[float] = Field(..., description="Sizes of each wedge in the pie chart.")
    # values: List[float] = Field(..., description="Values corresponding to each wedge in the pie chart.")
    colors: List[str] = Field(..., description="Colors corresponding to each wedge in the pie chart.")
    label_sizes: List[float] = Field(..., description="Sizes of the data labels for each wedge.")
    threshold: int = Field(16, description="Minimum angle in degrees for a wedge to be labeled.")