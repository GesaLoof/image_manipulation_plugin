from qtpy.QtWidgets import (
    QWidget,
    QPushButton,
    QHBoxLayout,
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


class CountLabels(QWidget):
    """
    This class counts the number of labels in an image
    """

    # Name that will be displayed on the combobox
    name = "Count labels"

    def _on_click_count_labels(self):
        # Get the selected image (make sure that it isn't none)
        image = self.viewer.layers.selection.active
        if image is None:
            error_image_selection()
            return
        # only run function if the selected layer is a labels layer
        if isinstance(self.viewer.layers.selection.active, layers.Labels):
            image = image.data
            count = len(np.unique(image))
            self.count.value = (
                f"There are {count} labels\nin your image (incl. background)"
            )
        else:
            self.count.value = "Careful, this is not a labels layer."

    def __init__(self, napari_viewer):
        super().__init__()

        self.viewer = napari_viewer

        btn = QPushButton("Count labels")
        btn.native = btn
        btn.name = "Count labels"
        btn.clicked.connect(self._on_click_count_labels)
        self.setLayout(QHBoxLayout())
        self.layout().addWidget(btn)
        self.count = widgets.Label(value="")

        container = widgets.Container(widgets=[self.count], labels=False)

        self.setLayout(QHBoxLayout())
        self.layout().addWidget(container.native)


class ListLabels(QWidget):
    """
    This class lists all labels in an image
    """

    # Name that will be displayed on the combobox
    name = "List labels"

    def _on_click_find_labels(self):
        # Get the selected image (make sure that it isn't none)
        image = self.viewer.layers.selection.active
        if image is None:
            error_image_selection()
            return
        # only run function if the selected layer is a labels layer
        if isinstance(self.viewer.layers.selection.active, layers.Labels):
            image = image.data
            labels = np.sort((np.unique(image)))
            output_str = self.format_output_list(labels)
            self.output_str.value = f"Labels: {output_str}"
        else:
            self.output_str.value = "Careful, this is not a labels layer."

    def format_output_list(self, output):
        output_str = "Labels: "
        for i, element in enumerate(output):
            if i == 0:
                output_str += f"\n {str(element)},"
            elif i + 1 == len(output):
                output_str += f" {str(element)}"
            elif (i + 1) % 10 == 0:
                output_str += f" {str(element)},\n"
            else:
                output_str += f" {str(element)},"
        return output_str

    def __init__(self, napari_viewer):
        super().__init__()

        self.viewer = napari_viewer

        btn = QPushButton("List labels")
        btn.native = btn
        btn.name = "List labels"
        btn.clicked.connect(self._on_click_find_labels)
        self.setLayout(QHBoxLayout())
        self.layout().addWidget(btn)
        self.output_str = widgets.Label(value="")

        container = widgets.Container(widgets=[self.output_str], labels=False)

        self.setLayout(QHBoxLayout())
        self.layout().addWidget(container.native)


class MeasureLabelVolume(QWidget):
    """
    This class counts the number of voxel of a given (or all) label(s) in a 3D image. 
    If the provided image is 4D it will measure volumes at the selected timepoint.
    Outputs are displayed as histogram (all labels) or printed (single label).
    """

    # Name that will be displayed on the combobox
    name = "Measure label volume"

    def _on_click_single(self):
        # Get the selected image (make sure that it isn't none)
        image = self.viewer.layers.selection.active
        if image is None:
            error_image_selection()
            return
        if isinstance(self.viewer.layers.selection.active, layers.Labels):
            image = image.data
            label = self.btn_input.value
            if (
                len(self.viewer.dims.current_step) == 4
            ):  # means data is 4 dimensional
                t_position = self.viewer.dims.current_step[0]
                volume = np.sum(image[t_position, :, :, :] == label)
            else:
                volume = np.sum(image == label)
            if volume > 0:
                self.volume.value = f"Label {label} has {volume} voxels"
            else:
                self.volume.value = (
                    f"Label {label} is not present in this image"
                )
        else:
            self.message.value = "Careful, this is not a labels layer."

    def _on_click_all(self):
        # Get the selected image (make sure that it isn't none)
        image = self.viewer.layers.selection.active
        if image is None:
            error_image_selection()
            return
        # only run function if the selected layer is a labels layer
        if isinstance(self.viewer.layers.selection.active, layers.Labels):
            image = image.data
            if (
                len(self.viewer.dims.current_step) == 4
            ):  # means data is 4 dimensional
                t_position = self.viewer.dims.current_step[0]
                labels = np.unique(image[t_position, :, :, :])
                input_ones = np.ones_like(image[t_position, :, :, :])
                volumes = sum_labels(
                    input_ones, image[t_position, :, :, :], labels
                )
            else:
                labels = np.unique(image)
                input_ones = np.ones_like(image)
                volumes = sum_labels(input_ones, image, labels)
            print(volumes)
            fig, ax = plt.subplots()
            ax.hist(volumes)
            ax.set_xlabel("amount")
            ax.set_ylabel("volumes in voxels")
            ax.set_title(f"Volumes at time {t_position} in voxels")
            fig.tight_layout()
            plt.show()
            self.message.value = "Volume histogram in pop-up window"
        else:
            self.message.value = "Careful, this is not a labels layer."

    def __init__(self, napari_viewer):
        super().__init__()
        self.viewer = napari_viewer

        self.btn_input = widgets.SpinBox()
        self.btn_input.name = "Enter a label"

        btn_calc = QPushButton("Calculate volume")
        btn_calc.native = btn_calc
        btn_calc.name = "Calculate volume"
        btn_calc.clicked.connect(self._on_click_single)
        self.volume = widgets.Label(value="")

        btn_histo = QPushButton("Show all volumes")
        btn_histo.native = btn_histo
        btn_histo.name = "Show all volumes"
        btn_histo.clicked.connect(self._on_click_all)
        self.message = widgets.Label(value="")

        container = widgets.Container(
            widgets=[
                self.btn_input,
                btn_calc,
                self.volume,
                btn_histo,
                self.message,
            ],
            labels=False,
        )

        self.setLayout(QHBoxLayout())
        self.layout().addWidget(container.native)


class ChangeLabel(QWidget):
    "This class changes a desired label ID to a new ID"

    # Name that will be displayed on the combobox
    name = "Change label"

    def _on_click(self):
        # Get the selected image (make sure that it isn't none)
        image = self.viewer.layers.selection.active
        if image is None:
            error_image_selection()
            return
        # only run function if the selected layer is a labels layer
        if isinstance(self.viewer.layers.selection.active, layers.Labels):
            image = image.data
            label1 = self.btn_input.value
            label2 = self.btn_new.value
            all_labels = np.unique(image)
            if label1 in all_labels:
                if label2 not in all_labels:
                    if self.btn_copy.value == "No":
                        if self.btn_time.value == "Yes":  # if all t
                            image[image == label1] = label2
                            self.message.value = f"Label {label1} has been changed to {label2} in all time frames."
                        else:
                            if (
                                len(self.viewer.dims.current_step) == 4
                            ):  # means data is 4 dimensional
                                t_position = self.viewer.dims.current_step[0]
                                image[t_position, :, :, :][
                                    image[t_position, :, :, :] == label1
                                ] = label2
                            else:
                                image[image == label1] = label2
                                t_position = 0
                            self.message.value = f"Label {label1} has been changed to {label2} in time frame {t_position}."
                    else:
                        # now we create a copy of the image and change the label in the copy only
                        new_image = image.copy()
                        if self.btn_time.value == "Yes":
                            new_image[new_image == label1] = label2
                            self.message.value = f"Label {label1} has been changed to {label2} \nin a copy of your image in all times frames."
                        else:
                            if (
                                len(self.viewer.dims.current_step) == 4
                            ):  # means data is 4 dimensional
                                t_position = self.viewer.dims.current_step[0]
                                new_image[t_position, :, :, :][
                                    new_image[t_position, :, :, :] == label1
                                ] = label2
                            else:
                                new_image[new_image == label1] = label2
                                t_position = 0
                            self.message.value = f"Label {label1} has been changed to {label2} in a copy\nof your image exclusively in time frame {t_position}."
                else:
                    if self.btn_force.value is not False:
                        if self.btn_copy.value == "No":
                            if self.btn_time.value == "Yes":  # if yes, then change label in all t
                                image[image == label1] = label2
                                self.message.value = f"Label {label1} has been changed to {label2} in all time frames."
                            else:
                                if (
                                    len(self.viewer.dims.current_step) == 4
                                ):  # means data is 4 dimensional
                                    t_position = self.viewer.dims.current_step[0]
                                    image[t_position, :, :, :][
                                        image[t_position, :, :, :] == label1
                                    ] = label2
                                else:
                                    image[image == label1] = label2
                                    t_position = 0
                                self.message.value = f"Label {label1} has been changed to {label2} in time frame {t_position}."
                        else:
                            new_image = image.copy()
                            if self.btn_time.value == "Yes":
                                new_image[image == label1] = label2
                                self.message.value = f"Label {label1} has been changed to {label2} \nin a copy of your image in all times frames."
                            else:
                                if (
                                    len(self.viewer.dims.current_step) == 4
                                ):  # means data is 4 dimensional
                                    t_position = self.viewer.dims.current_step[0]
                                    new_image[t_position, :, :, :][
                                        new_image[t_position, :, :, :] == label1
                                    ] = label2
                                    self.message.value = f"Label {label1} has been changed to {label2} in a copy\nof your image exclusively in time frame {t_position}."
                                else:
                                    new_image[new_image == label1] = label2
                                    t_position = 0
                                self.message.value = f"Label {label1} has been changed to {label2} in a copy\nof your image exclusively in time frame {t_position}."
                        # always retrieve the image scale to remain flexible to all sorts of images
                            scale = self.viewer.layers.selection.active.scale
                            self.viewer.add_labels(
                                new_image, name="new_labels", scale=scale
                            )
                    else: self.message.value = (f"Label {label2} already exists, if you want to change \nLabel {label1} to Label {label2}, you need to force it (checkbox).")
            else:
                self.message.value = (
                    f"Label {label1} does not exits in the input image."
                )

        else:
            self.message.value = "Careful, this is not a labels layer."

    def __init__(self, napari_viewer):
        super().__init__()
        self.viewer = napari_viewer

        self.btn_input = widgets.SpinBox()
        self.button1_label = widgets.Label(value="")
        self.button1_label.value = "Change label:"

        self.btn_new = widgets.SpinBox()
        self.button2_label = widgets.Label(value="")
        self.button2_label.value = "to label:"

        self.btn_force = widgets.CheckBox(value = False)
        self.btn_force.changed()
        self.button_force_label = widgets.Label(value="")
        self.button_force_label.value = "Force change even if new label already exists"

        btn_calc = QPushButton("Change label")
        btn_calc.native = btn_calc
        btn_calc.name = "Change label"
        btn_calc.clicked.connect(self._on_click)
        self.message = widgets.Label(value="")

        self.btn_copy = widgets.RadioButtons(choices=["No", "Yes"], value="No")
        self.btn_copy_label = widgets.Label(value="")
        self.btn_copy_label.value = "Create new layer with changes:"

        self.btn_time = widgets.RadioButtons(
            choices=["No", "Yes"], value="Yes"
        )
        self.btn_time_label = widgets.Label(value="")
        self.btn_time_label.value = "Apply to all time frames:"

        container_checkbox = widgets.Container(
            widgets=[
                self.btn_force,
                self.button_force_label,
            ],
            labels = False,
            layout = "horizontal"
        )

        container = widgets.Container(
            widgets=[
                self.button1_label,
                self.btn_input,
                self.button2_label,
                self.btn_new,
                container_checkbox,
                self.btn_copy_label,
                self.btn_copy,
                self.btn_time_label,
                self.btn_time,
                btn_calc,
                self.message,
            ],
            labels=False,
        )

        self.setLayout(QHBoxLayout())
        self.layout().addWidget(container.native)


class OpenTIFSequence(QWidget):
    """
    This class opens a sequence of 3D images as a 4D time series
    Currently it only works for tiff files
    """

    # Name that will be displayed on the combobox
    name = "Open TIF sequence"

    def _on_click(self):
        regex = str(self.regex.value)
        path = str(self.path_first_image.value)
        folder = "/".join(path.split("/")[:-1])
        list_of_files = sorted(glob.glob(f"{folder}/{regex}"))

        # is there another way to test whether file is a tif?
        if not ".tif" in path.lower():
            error_tif_selection()
            return
        else:
            first_image = imread(path)
        image_dim = first_image.shape

        # initialize outpout and then load single images and append them to one array
        output_array = np.zeros(
            (len(list_of_files), image_dim[0], image_dim[1], image_dim[2])
        )
        for i, file in enumerate(list_of_files):
            if i == 0:
                output_array[i, :] = first_image

            else:
                if not ".tif" in file:
                    error_tif_selection()
                    return
                im = imread(file)
                output_array[i, :] = im
        scale = self.scale.value
        if str(self.type.value) == "Labels":
            self.viewer.add_labels(
                output_array.astype(int),
                name="Movie",
                scale=(scale[0], scale[1], scale[2]),
            )
        else:
            self.viewer.add_image(
                output_array,
                name="Movie",
                scale=(scale[0], scale[1], scale[2]),
            )

    def __init__(self, napari_viewer):
        super().__init__()
        self.viewer = napari_viewer

        self.label_path_first_image = widgets.Label(value="")
        self.label_path_first_image.value = "Path to first image"
        self.path_first_image = widgets.FileEdit()

        self.regex_label = widgets.Label(value="")
        self.regex_label.value = "Regex (optional)"
        self.regex = widgets.LineEdit()

        self.type_label = widgets.Label(value="")
        self.type_label.value = "Image type"
        self.type = widgets.ComboBox(choices=["Labels", "Intensity"])

        self.scale_label = widgets.Label(value="")
        self.scale_label.value = "Scale"
        self.scale = widgets.TupleEdit(
            value=[1.0001, 1.0001, 1.0001], label={"max": 10000}
        )

        # do I want to add a range for t?
        # Do I want to ask for the background label so I can change it to 0?

        btn_calc = QPushButton("Open sequence")
        btn_calc.native = btn_calc
        btn_calc.name = "Open sequence"
        btn_calc.clicked.connect(self._on_click)

        container = widgets.Container(
            widgets=[
                self.label_path_first_image,
                self.path_first_image,
                self.regex_label,
                self.regex,
                self.type_label,
                self.type,
                self.scale_label,
                self.scale,
                btn_calc,
            ],
            labels=False,
        )

        self.setLayout(QHBoxLayout())
        self.layout().addWidget(container.native)
        self.layout().addStretch(1)


class OpenMHASequence(QWidget):
    """
    This class opens a sequence of 3D images as a 4D time series
    Currently it only works for tiff files
    """

    # Name that will be displayed on the combobox
    name = "Open .mha sequence"

    def _on_click(self):
        regex = str(self.regex.value)
        path = str(self.path_first_image.value)
        folder = "/".join(path.split("/")[:-1])
        list_of_files = sorted(glob.glob(f"{folder}/{regex}"))

        # is there another way to test whether file is a tif?
        if not ".mha" in path.lower():
            error_mha_selection()
            return
        else:
            first_image, header = load(path)
            #transpose to regular order --> how do I make sure that this always goes in the right direction?
            #should I add a button that asks for the order of axes?
            first_image = np.transpose(first_image, (2, 1, 0))
        image_dim = first_image.shape

        # initialize outpout and then load single images and append them to one array
        output_array = np.zeros(
            (len(list_of_files), image_dim[0], image_dim[1], image_dim[2])
        )
        for i, file in enumerate(list_of_files):
            if i == 0:
                output_array[i, :] = first_image

            else:
                if not ".mha" in file:
                    error_mha_selection()
                    return
                im, header = load(file)
                #transpose to regular order --> how do I make sure that this always goes in the right direction?
                #should I add a button that asks for the order of axes?
                im = np.transpose(im, (2, 1, 0))
                output_array[i, :] = im
        scale = self.scale.value
        if str(self.type.value) == "Labels":
            self.viewer.add_labels(
                output_array.astype(int),
                name="Movie",
                scale=(scale[0], scale[1], scale[2]),
            )
        else:
            self.viewer.add_image(
                output_array,
                name="Movie",
                scale=(scale[0], scale[1], scale[2]),
            )

    def __init__(self, napari_viewer):
        super().__init__()
        self.viewer = napari_viewer

        self.label_path_first_image = widgets.Label(value="")
        self.label_path_first_image.value = "Path to first image"
        self.path_first_image = widgets.FileEdit()

        self.regex_label = widgets.Label(value="")
        self.regex_label.value = "Regex (optional)"
        self.regex = widgets.LineEdit()

        self.type_label = widgets.Label(value="")
        self.type_label.value = "Image type"
        self.type = widgets.ComboBox(choices=["Labels", "Intensity"])

        self.scale_label = widgets.Label(value="")
        self.scale_label.value = "Scale"
        self.scale = widgets.TupleEdit(
            value=[1.0001, 1.0001, 1.0001], label={"max": 10000}
        )

        # do I want to add a range for t?
        # Do I want to ask for the background label so I can change it to 0?

        btn_calc = QPushButton("Open sequence")
        btn_calc.native = btn_calc
        btn_calc.name = "Open sequence"
        btn_calc.clicked.connect(self._on_click)

        container = widgets.Container(
            widgets=[
                self.label_path_first_image,
                self.path_first_image,
                self.regex_label,
                self.regex,
                self.type_label,
                self.type,
                self.scale_label,
                self.scale,
                btn_calc,
            ],
            labels=False,
        )

        self.setLayout(QHBoxLayout())
        self.layout().addWidget(container.native)
        self.layout().addStretch(1)
