from enum import Enum

from .label_creation import ThresholdLabels, ApplyThresholdOfChoice, ManualThresholding

__all__ = ("ThresholdLabels", "ApplyThresholdOfChoice", "ManualThresholding")

# All new widget should be listed here to be displayed in napari
__all_widgets__ = (ThresholdLabels, ApplyThresholdOfChoice, ManualThresholding)
