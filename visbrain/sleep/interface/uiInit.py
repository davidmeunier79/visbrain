"""This script group the diffrent graphical components.

Grouped components :
    * PyQt elements (window, Pyqt functions...)
    * Vispy canvas functions
    * User shortcuts
"""
import numpy as np

from PyQt4 import QtGui
from vispy import app, scene
import vispy.visuals.transforms as vist

from .gui import Ui_MainWindow
from ...utils import color2vb

__all__ = ['uiInit']


class uiInit(QtGui.QMainWindow, Ui_MainWindow, app.Canvas):
    """Group and initialize the graphical elements and interactions."""

    def __init__(self):
        """Init."""
        # Create the main window :
        super(uiInit, self).__init__(None)
        self.setupUi(self)


class TimeAxis(object):
    """Create a unique time axis."""

    def __init__(self, axis=True, x_label='', x_heightMax=40,
                 font_size=12, color='white', title='', axis_label_margin=50,
                 tick_label_margin=5, name='', bgcolor=(.9, .9, .9), cargs={},
                 xargs={}, indic_color='darkred', fcn=[]):
        # Create the main canvas :
        self.canvas = scene.SceneCanvas(keys=None, bgcolor=bgcolor,
                                        show=False, title=name, **cargs)
        _ = [self.canvas.connect(k) for k in fcn]

        # Create a grid :
        grid = self.canvas.central_widget.add_grid(margin=0)
        grid.spacing = 0

        # Add x-axis :
        self.xaxis = scene.AxisWidget(orientation='bottom', axis_label=x_label,
                                      axis_font_size=font_size,
                                      axis_label_margin=axis_label_margin,
                                      tick_label_margin=tick_label_margin,
                                      **xargs)
        self.xaxis.height_max = x_heightMax
        grid.add_widget(self.xaxis, row=1, col=0)

        # Main plot :
        self.wc = grid.add_view(row=0, col=0, border_color=color)

        # Add a square indicator :
        image = color2vb(indic_color)[np.newaxis, ...]
        self.mesh = scene.visuals.Image(image, name='indicator')
        self.mesh.parent = self.wc.scene

    def set_data(self, tox, width, time, unit='seconds'):
        """Move the main square."""
        # Get factor according to unit :
        if unit == 'seconds':
            fact = 1.
        elif unit == 'minutes':
            fact = 60.
        elif unit == 'hours':
            fact = 3660.
        # Move the square
        self.mesh.transform = vist.STTransform(translate=tox / fact,
                                               scale=width / fact)
        # Update camera :
        self.wc.camera.rect = (0, 0, (time.max() - time.min()) / fact, 1)

    def set_camera(self, camera):
        """Set a camera and link all objects inside."""
        # Set camera to the main widget :
        self.wc.camera = camera
        # Link transformations with axis :
        self.xaxis.link_view(self.wc)


# class AxisCanvas(object):
#     """Create a canvas with an embeded axis."""

#     def __init__(self, axis=True, x_label='', x_heightMax=40, y_label='',
#                  y_widthMax=80, font_size=7, color='white', title='',
#                  axis_label_margin=0, tick_label_margin=5, name='',
#                  bgcolor=(.9, .9, .9), cargs={}, xargs={}, yargs={}):
#         """Init."""
#         # Save variables :
#         self._axis = axis
#         self._title = title
#         self._xlabel = x_label
#         self._ylabel = y_label

#         # Create the main canvas :
#         self.canvas = scene.SceneCanvas(keys=None, bgcolor=bgcolor,
#                                         show=True, title=name, **cargs)

#         # Add axis :
#         if axis:
#             # Create a grid :
#             grid = self.canvas.central_widget.add_grid(margin=0)
#             grid.spacing = 0

#             # Add top padding :
#             self._tpad = grid.add_widget(row=0, col=0)
#             self._tpad.height_max = 10

#             # Add y-axis :
#             self.yaxis = scene.AxisWidget(orientation='left', domain=(0, 129),
#                                           axis_label=y_label,
#                                           axis_font_size=font_size,
#                                           axis_label_margin=axis_label_margin,
#                                           tick_label_margin=tick_label_margin,
#                                           **yargs)
#             self.yaxis.width_max = y_widthMax
#             grid.add_widget(self.yaxis, row=1, col=0)

#             # Add x-axis :
#             self.xaxis = scene.AxisWidget(orientation='bottom',
#                                           axis_label=x_label,
#                                           axis_font_size=font_size,
#                                           axis_label_margin=axis_label_margin,
#                                           tick_label_margin=tick_label_margin,
#                                           **xargs)
#             self.xaxis.height_max = x_heightMax
#             grid.add_widget(self.xaxis, row=2, col=1)

#             # Add right padding :
#             self._rpad = grid.add_widget(row=0, col=2, row_span=1)
#             self._rpad.width_max = 10

#             # Add top padding :
#             self._rpad = grid.add_widget(row=2, col=0)
#             self._rpad.height_max = 10

#             # Main plot :
#             self.wc = grid.add_view(row=1, col=1, border_color=color)
#         # Ignore axis :
#         else:
#             self.wc = self.canvas.central_widget.add_view()

#     def set_camera(self, camera):
#         """Set a camera and link all objects inside."""
#         # Set camera to the main widget :
#         self.wc.camera = camera
#         # Link transformations with axis :
#         if self._axis:
#             # self.xaxis.link_view(self.wc)
#             self.yaxis.link_view(self.wc)

#     def set_info(self, title=None, xlabel=None, ylabel=None):
#         """Set title and labels for the axis of the canvas."""
#         # Set label / title only for grid axis :
#         if self._axis:
#             # X-label :
#             if xlabel is not None:
#                 self.xaxis.axis.axis_label = xlabel
#                 self.xaxis.update()
#             # Y-label :
#             if ylabel is not None:
#                 self.yaxis.axis.axis_label = ylabel
#                 self.yaxis.update()
#             self.canvas.update()
#         else:
#             raise ValueError("For defining infos, you must use an axis canvas")

#     def visible_axis(self, visible=True):
#         """Display or hide the axis."""
#         self._axis = visible
#         # self.xaxis.visible = visible
#         self.yaxis.visible = visible
#         # self._rpad.visible = visible


class AxisCanvas(object):
    """Create a canvas with an embeded axis."""

    def __init__(self, axis=True, x_label='', x_heightMax=40, y_label='',
                 y_widthMax=80, font_size=14, color='white', title='',
                 axis_label_margin=50, tick_label_margin=5, name='',
                 bgcolor=(.9, .9, .9), cargs={}, xargs={}, yargs={}, fcn=[]):
        """Init."""
        # Save variables :
        self._axis = axis
        self._title = title
        self._xlabel = x_label
        self._ylabel = y_label

        # Create the main canvas :
        self.canvas = scene.SceneCanvas(keys=None, bgcolor=bgcolor,
                                        show=True, title=name, **cargs)
        _ = [self.canvas.connect(k) for k in fcn]

        # Add axis :
        if axis:
            # Create a grid :
            grid = self.canvas.central_widget.add_grid(margin=0)
            grid.spacing = 0

            # Add y-axis :
            self.yaxis = scene.AxisWidget(orientation='left', domain=(0, 129),
                                          axis_label=y_label,
                                          axis_font_size=font_size,
                                          axis_label_margin=axis_label_margin,
                                          tick_label_margin=tick_label_margin,
                                          **yargs)
            self.yaxis.width_max = y_widthMax
            grid.add_widget(self.yaxis, row=0, col=0)

            # Add x-axis :
            self.xaxis = scene.AxisWidget(orientation='bottom',
                                          axis_label=x_label,
                                          axis_font_size=font_size,
                                          axis_label_margin=axis_label_margin,
                                          tick_label_margin=tick_label_margin,
                                          **xargs)
            self.xaxis.height_max = x_heightMax
            grid.add_widget(self.xaxis, row=1, col=1)

            # Add right padding :
            self._rpad = grid.add_widget(row=0, col=2, row_span=1)
            self._rpad.width_max = 50

            # Main plot :
            self.wc = grid.add_view(row=0, col=1, border_color=color)
        # Ignore axis :
        else:
            self.wc = self.canvas.central_widget.add_view()

    def set_camera(self, camera):
        """Set a camera and link all objects inside."""
        # Set camera to the main widget :
        self.wc.camera = camera
        # Link transformations with axis :
        if self._axis:
            self.xaxis.link_view(self.wc)
            self.yaxis.link_view(self.wc)

    def set_info(self, title=None, xlabel=None, ylabel=None):
        """Set title and labels for the axis of the canvas."""
        # Set label / title only for grid axis :
        if self._axis:
            # X-label :
            if xlabel is not None:
                self.xaxis.axis.axis_label = xlabel
                self.xaxis.update()
            # Y-label :
            if ylabel is not None:
                self.yaxis.axis.axis_label = ylabel
                self.yaxis.update()
            self.canvas.update()
        else:
            raise ValueError("For defining infos, you must use an axis canvas")

    def visible_axis(self, visible=True):
        """Display or hide the axis."""
        self._axis = visible
        self.xaxis.visible = visible
        self.yaxis.visible = visible
        self._rpad.visible = visible
