from enum import Enum

from .label_image_manipulation import CountLabels, ListLabels, MeasureLabelVolume, ChangeLabel, OpenTIFSequence, OpenMHASequence

__all__ = ("CountLabels", "ListLabels", "MeasureLabelVolume", "ChangeLabel", "OpenTIFSequence", "OpenMHASequence")

# All new widget should be listed here to be displayed in napari
__all_widgets__ = (CountLabels, ListLabels, MeasureLabelVolume, ChangeLabel, OpenTIFSequence, OpenMHASequence)
