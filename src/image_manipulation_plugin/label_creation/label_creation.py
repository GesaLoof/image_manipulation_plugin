from qtpy.QtWidgets import (
    QWidget,
    QPushButton,
    QHBoxLayout,
    QComboBox
)
from image_manipulation_plugin.utils import (
    error_image_selection,
    error_tif_selection,
    error_mha_selection
)
from matplotlib import pyplot as plt
from magicgui import widgets
import numpy as np
from napari import layers
from tifffile import imread
import glob
from scipy.ndimage import sum_labels
from medpy.io import load
from skimage.filters import (
threshold_otsu,
threshold_yen,
threshold_li,
threshold_isodata,
threshold_mean,
try_all_threshold,
)


class ThresholdLabels(QWidget):
    """
    This class creates labels using a chosen thresholding method given an intensity image
    """

    # Name that will be displayed
    name = "Try all thresholding methods"

    def _on_click_use_all_thresholds(self):
        # Get the selected image (make sure that it isn't none)
        image = self.viewer.layers.selection.active
        if image is None:
            error_image_selection()
            return
        # only run function if the selected layer is an intensity image
        if isinstance(self.viewer.layers.selection.active, layers.Image):
            import matplotlib.pyplot as plt
            image = image.data
            fig, _ = try_all_threshold(image, figsize=(10, 8), verbose=False)
            try:
                plt.show()
            except Exception:
                # If a backend issue occurs, close the figure to avoid a resource leak
                plt.close(fig)
        else:
            self.count.value = "Careful, this is not an intensty image."

    def __init__(self, napari_viewer):
        super().__init__()

        self.viewer = napari_viewer

        btn = QPushButton("Test all thresholds")
        btn.native = btn
        btn.name = "Test all thresholds"
        btn.clicked.connect(self._on_click_use_all_thresholds)
        self.setLayout(QHBoxLayout())
        self.layout().addWidget(btn)
        self.count = widgets.Label(value="")

        container = widgets.Container(widgets=[self.count], labels=False)

        self.setLayout(QHBoxLayout())
        self.layout().addWidget(container.native)


class ApplyThresholdOfChoice(QWidget):
    """
    This class allows selection of thresholding method to create labels from an intensity image
    """

    # Name that will be displayed on the combobox
    name = "Apply threshold"

    def _on_click_threshold_image(self):
        # Get the selected image (make sure that it isn't none)
        image = self.viewer.layers.selection.active
        if image is None:
            error_image_selection()
            return
        # only run function if the selected layer is an intensity image
        if isinstance(self.viewer.layers.selection.active, layers.Image):
            image = image.data
            method = str(self.threshold.value)
            if method == "Otsu":
                thresh = threshold_otsu(image)
            elif method == "Yen":
                thresh = threshold_yen(image)
            elif method == "Li":
                thresh = threshold_li(image)
            elif method == "Isodata":
                thresh = threshold_isodata(image)
            elif method == "Mean":
                thresh = threshold_mean(image)
            if self.image_type.value == "electron micriscopy":
                binary = image < thresh
            if self.image_type.value == "light microscopy":
                binary = image > thresh
            self.viewer.add_labels(binary.astype(int), name="Labels")
            self.output_str.value = f"Labels created using {method} threshold at {thresh:.2f}"
        else:
            self.output_str.value = "Careful, the selected image is not an intensity image."

    def __init__(self, napari_viewer):
        super().__init__()

        self.viewer = napari_viewer

        self.threshold_label = widgets.Label(value="")
        self.threshold_label.value = "select thresholding algorithm"
        self.threshold = widgets.ComboBox(choices=["Otsu", "Yen", "Li", "Isodata", "Mean"])
        self.image_type_label = widgets.Label(value="")
        self.image_type_label.value = "select image type"
        self.image_type = widgets.ComboBox(choices=["light microscopy", "electron micriscopy"])
        btn1 = QPushButton("threshold image")
        btn1.native = btn1
        btn1.name = "Create labels image"
        btn1.clicked.connect(self._on_click_threshold_image)
        self.output_str = widgets.Label(value="")

        container = widgets.Container(widgets=[self.threshold_label,
                                               self.threshold,
                                               self.image_type_label,
                                               self.image_type,
                                               self.output_str,
                                               btn1   
                                               ], labels=False)

        self.setLayout(QHBoxLayout())
        self.layout().addWidget(container.native)


class ManualThresholding(QWidget):
    """
    This class creates a labels image by thresholding an intensity image according to a manually provided intensity value.
    Each time the user moves the slider, the labels image is updated.
    """

    # Name that will be displayed on the combobox
    name = "Manual thresholding"

    def _on_click_threshold(self):
        # Get the selected image (make sure that it isn't none)
        image = self.viewer.layers.selection.active
        if image is None:
            error_image_selection()
            return
        if isinstance(self.viewer.layers.selection.active, layers.Image):
            image = image.data
            threshold = self.btn.value
            binary = image > threshold
            #TODO check whether I am overwriting layers like this
            self.viewer.add_labels(binary.astype(int), name="Labels")

        else:
            self.message.value = "Careful, this is not an intensity image."

    def __init__(self, napari_viewer):
        super().__init__()
        self.viewer = napari_viewer

        btn = widgets.Slider(min=0, max=100, step=1, value=50)
        btn.name = "Threshold value (in % of max intensity)"
        btn.changed.connect(self._on_click_threshold)

        container = widgets.Container(
            widgets=[
                btn
            ],
            labels=False,
        )

        self.setLayout(QHBoxLayout())
        self.layout().addWidget(container.native)
