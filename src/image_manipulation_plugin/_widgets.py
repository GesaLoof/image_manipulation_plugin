"""
This module is the backbone of the whole structure.
It is not meant to be changed much.
The action takes place in the different module places.
"""
from typing import TYPE_CHECKING

from qtpy.QtWidgets import QWidget, QComboBox, QStackedWidget, QVBoxLayout
from magicgui import widgets
from . import label_image_manipulation


if TYPE_CHECKING:
    import napari


class MainWidget(QWidget):
    """Abstract class for all the widgets"""

    # Module to parse (here None because it is the abstract class)
    module = None

    def __make_widget_combobox(self) -> QComboBox:
        """
        Function to generate a combo box of
        a list of widgets from a module
        """
        if self.module is None:
            return

        main_combobox = QComboBox()
        main_combobox._explicitly_hidden = False
        main_combobox.native = main_combobox

        main_stack = QStackedWidget()
        main_stack.native = main_stack

        for im_info_class in self.module.__all_widgets__:
            w_created = im_info_class(self.viewer)

            main_combobox.addItem(w_created.name)

            main_stack.addWidget(w_created)

        main_combobox.currentIndexChanged.connect(main_stack.setCurrentIndex)
        main_combobox.name = "main_combobox"
        main_stack.name = "main_stack"

        main_control = widgets.Container(
            widgets=[
                main_combobox,
                main_stack,
            ],
            labels=False,
        )
        return main_control

    def __init__(self, napari_viewer):
        super().__init__()
        self.viewer = napari_viewer
        main_control = self.__make_widget_combobox()
        layout = QVBoxLayout()
        layout.addStretch(1)
        layout.setSpacing(0)
        self.setLayout(layout)
        self.layout().addWidget(main_control.native)

class LabelImageManipulationWidget(MainWidget):
    module = label_image_manipulation

