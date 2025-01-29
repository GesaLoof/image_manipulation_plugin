from qtpy.QtWidgets import QMessageBox
import numpy as np

def error_image_selection():
    """
    Print a message error in a box
    """
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setText("Image selection error")
    msg.setInformativeText(("Please select an adequate image\n" "You can select point images on the left hand side of the viewer"))
    msg.setWindowTitle("Image selection error")
    msg.exec_()


def error_tif_selection():
    """
    Print a message error in a box
    """
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setText("File selection error")
    msg.setInformativeText(("The file you selected is not a TIF file.\nMake sure your regular expression only targets TIF files."))
    msg.setWindowTitle("File selection error")
    msg.exec_()

def error_mha_selection():
    """
    Print a message error in a box
    """
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setText("File selection error")
    msg.setInformativeText(("The file you selected is not a .mha file.\nMake sure your regular expression only targets .mha files."))
    msg.setWindowTitle("File selection error")
    msg.exec_()


def error_feature_file():
    """
    Print a message error in a box
    """
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setText("File selection error")
    msg.setInformativeText(("The file you selected is of a type that cannot be processed.\nPlease choose ASTEC or LineageTree output file."))
    msg.setWindowTitle("File selection error")
    msg.exec_()


def error_active_layer_features():
    """
    Print a message error in a box
    """
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setText("Feature error")
    msg.setInformativeText(("Your active layer has no features.\nPlease load a feature file first."))
    msg.setWindowTitle("Feature error")
    msg.exec_()

def error_image_selection_refresh():
    """
    Print a message error in a box
    """
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setText("Image selection error")
    msg.setInformativeText(('Please select an adequate image, load features and update your feature choices.'))
    msg.setWindowTitle("Image selection error")
    msg.exec_()



'''
    The following class and functions were copied from Robert Haase's process-points-and-surfaces plugin: https://github.com/haesleinhuepf/napari-process-points-and-surfaces/blob/main/napari_process_points_and_surfaces/_utils.py
'''
   
class _StaticMemory():
    viewers = []


def _init_viewer(viewer: "napari.Viewer"):
    """
    When calling this function, we make sure that the light follows the camera in napari when viewing a Surface layer.

    Code modified from: https://github.com/napari-threedee/napari-threedee/blob/1aa50ddf89c0a85c13ba3e148de791e2bd9c5d2b/src/napari_threedee/visualization/lighting_control.py#L51
    License: BSD-3 by the napari-team
    """
    if viewer is None:
        return

        # prevent registering the same event in one viewer multiple times
    if viewer in _StaticMemory.viewers:
        return
    _StaticMemory.viewers.append(viewer)

    def _on_camera_change(event=None):
        view_direction = np.asarray(viewer.camera.view_direction)

        selected_layer_visuals = [_get_napari_visual(viewer=viewer, layer=layer) for layer in viewer.layers]

        for layer, visual in zip(viewer.layers, selected_layer_visuals):
            dims_displayed = _get_dims_displayed(layer)
            layer_view_direction = np.asarray(layer._world_to_data_ray(view_direction))[dims_displayed]
            if hasattr(visual, "node") and hasattr(visual.node, "shading_filter"):
                visual.node.shading_filter.light_dir = layer_view_direction[::-1]

    viewer.camera.events.angles.connect(_on_camera_change)

def _get_dims_displayed(layer):
    """
    Code modified from: https://github.com/napari-threedee/napari-threedee/blob/1aa50ddf89c0a85c13ba3e148de791e2bd9c5d2b/src/napari_threedee/utils/napari_utils.py#L70
    License: BSD-3 by the napari-team
    """
    # layer._dims_displayed was removed in
    # https://github.com/napari/napari/pull/5003
    if hasattr(layer, "_slice_input"):
        return layer._slice_input.displayed
    return layer._dims_displayed


def _get_napari_visual(viewer, layer):
    """Get the visual class for a given layer

    Code modified from: https://github.com/napari-threedee/napari-threedee/blob/1aa50ddf89c0a85c13ba3e148de791e2bd9c5d2b/src/napari_threedee/utils/napari_utils.py#L23
    License: BSD-3 by the napari-team

    Parameters
    ----------
    viewer
        The napari viewer object
    layer
        The napari layer object for which to find the visual.
    Returns
    -------
    visual
        The napari visual class for the layer.
    """
    visual = viewer.window._qt_window._qt_viewer.layer_to_visual[layer]

    return visual