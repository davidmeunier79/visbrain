"""Main class for managing sub-structures (areas).

Areas are sub-divided parts of the brain. The present file display those areas
using either Automated Anatomical Labeling (AAL) or Brodmann area labeling.
"""

import numpy as np
from scipy.signal import fftconvolve

import warnings
import os
import sys

from vispy.geometry.isosurface import isosurface
import vispy.visuals.transforms as vist

from .visuals import BrainMesh
from ...utils import array2colormap, color2vb, color2faces

# warnings.filterwarnings('ignore', r'with ndim')
__all__ = ['AreaBase']


class AreaBase(object):
    """Main class for managing sub-division brain areas.

    This class contains several method for managing areas (loading, color,
    ploting...)
    """

    def __init__(self, structure='brod', select=None, color='white', cmap=None,
                 scale_factor=1, name='', transform=None, smooth=3):
        """Init."""
        self.atlaspath = os.path.join(sys.modules[__name__].__file__.split(
            'Area')[0], 'templates')
        self.file = 'roi.npz'
        self._roitype = {}
        self._structure = structure
        self._select = select
        self._selectAll = True
        self._unicolor = True
        self._color = color
        self.cmap = cmap
        self._scale_factor = scale_factor
        self.name = name
        self.mesh = None
        self.smoothsize = smooth
        self.need_update = True
        self.creation = True

        if transform is not None:
            self._transform = transform

    def __str__(self):
        """Return labels of selected ROI type."""
        return '\n'.join(self._label)

    # ========================================================================
    # PROCESSING FUNCTIONS
    # ========================================================================
    def _load(self):
        """Load the matrice which contains the labeling atlas.

        This method load the volume, the index of each structure and the
        appropriate name.
        """
        # Load the atlas :
        atlas = np.load(os.path.join(self.atlaspath, self.file))
        self._hdr = atlas['hdr'][0:-1, -1]

        # Manage atlas :
        if self._structure not in ['aal', 'brod']:
            raise ValueError("structure must be either 'aal' or 'brod'")
        else:
            # ==================== AAL ====================
            if self._structure == 'aal':
                # Get volume, index and unique index list :
                self._vol = atlas['vol']
                self._uidx = np.unique(atlas['aal_idx'])
                self._nlabel = len(atlas['aal_label'])*2
                # Get labels for left / right hemispheres :
                label_L = np.array(["%.2d" % (num+1) + ': '+k+' (L)' for num, k
                                    in zip(np.arange(0, self._nlabel, 2),
                                           atlas['aal_label'])])
                label_R = np.array(["%.2d" % (num+1)+': '+k + ' (R)' for num, k
                                    in zip(np.arange(1, self._nlabel + 1, 2),
                                           atlas['aal_label'])])
                # Cat labels in alternance (L, R, L, R...) :
                self._label = np.column_stack((label_L, label_R)).flatten()
            # ==================== BRODMANN ====================
            elif self._structure == 'brod':
                # Get volume, index and unique index list :
                self._vol = atlas['brod_idx']
                self._uidx = np.unique(self._vol)[1::]
                self._label = np.array(["%.2d" % k + ': BA' + str(k) for num, k
                                        in enumerate(self._uidx)])

    def _preprocess(self):
        """Pre-processing function.

        This method can be used to manage area selection (select some areas,
        all of them...). Then, pre-process color (unique color, colormap...).
        Finally, find the index of the selected areas and corresponding labels.
        """
        # ====================== Manage area selection ======================
        # Select is None -> Select all areas :
        if self._select is None:
            self._select = self._uidx
            self._selectAll = True
        # Select is a list of integers :
        elif not isinstance(self._select, list):
            self._select = list(self._select)
            self._selectAll = False
        else:
            self._selectAll = False
        # Check if every selected element is present in the possibilities :
        for k in self._select:
            if k not in self._uidx:
                raise ValueError(str(k)+' not in :', self._uidx)

        # ====================== Manage color ======================
        # Use a list of colors (uniform color) :
        if not isinstance(self._color, list):
            self._color = list([self._color])
            self._unicolor = True
        # Non-uniform color :
        else:
            self._unicolor = False
        # Check if the length of color is the same as the number of selected
        # areas. Otherwise, use only the first color in the list :
        if len(self._color) != len(self._select):
            self._color = [self._color[0]]*len(self._select)
            self._unicolor = True
        else:
            self._unicolor = False
        # Use a colormap for the area color :
        if self.cmap is not None:
            # Generate an array of colors using a linearly spaced vector :
            self._color = array2colormap(np.arange(len(self._select)),
                                         cmap=self.cmap)
            # Turn it into a list :
            self._color = list(self._color)
            # self._color = [tuple(self._color[k, :]) for k in range(
            #                                             self._color.shape[0])]
            self._unicolor = False
            self._selectAll = False

        # ====================== Manage index ======================
        # Find selected areas in the unique list :
        self._selectedIndex = [np.argwhere(self._uidx == k)[0][
            0] for k in self._select]
        # Select labels :
        self._selectedLabels = self._label[self._selectedIndex]
        # Transform each color into a RGBA format :
        self._color = [color2vb(k) for k in self._color]
        # Initialize variables :
        self._color_idx, self.vertex_colors = np.array([]), np.array([])

    def _get_vertices(self):
        """Get vertices and faces of selected areas and pre-allocate color.

        Description
        """
        # --------------------------------------------------------------------
        # The volume array (self._vol) is composed with integers where each
        # integer encode for a specific area.
        # The isosurface turn a 3D array into a surface mesh compatible.
        # Futhermore, this function use a level parameter in order to get
        # vertices and faces of specific index. Unfortunately, the level can
        # only be >=, it's not possible to only select some specific levels.
        # --------------------------------------------------------------------
        # ============ Unicolor ============
        if self._unicolor:
            if not self._selectAll:
                # Create an empty volume :
                vol = np.zeros_like(self._vol)
                # Build the condition list :
                cd_lst = ['(self._vol==' + str(k) + ')' for k in self._select]
                # Set vol to 1 for selected index :
                vol[eval(' | '.join(cd_lst))] = 1
            else:
                vol = self._vol
            # Extract the vertices / faces of non-zero values :
            self.vert, self.faces = isosurface(self._smooth(vol), level=.5)
            # Turn the unique color tuple into a faces compatible ndarray:
            self.vertex_colors = color2faces(self._color[0],
                                             self.faces.shape[0])
            # Unique color per ROI :
            self._color_idx = np.zeros((self.faces.shape[0],))

        # ============ Specific selection + specific colors ============
        # This is where problems begin. In this part, there's a specific area
        # selection with each one of them having a specific color. The program
        # below loop over areas, make a copy of the volume, turn all
        # non-desired area index to 0, transform into an isosurface and finally
        # concatenate vertices / faces / color. This is is very slow and it's
        # only because of the color.
        else:
            self.vert, self.faces = np.array([]), np.array([])
            q = 0
            for num, k in enumerate(self._select):
                # Remove unecessary index :
                vol = np.zeros_like(self._vol)
                vol[self._vol == k] = 1
                # Get vertices/faces for this structure :
                vertT, facesT = isosurface(self._smooth(vol), level=.5)
                # Update faces index :
                facesT += (q+1)
                # Concatenate vertices/faces :
                self.vert = np.concatenate(
                    (self.vert, vertT)) if self.vert.size else vertT
                self.faces = np.concatenate(
                    (self.faces, facesT)) if self.faces.size else facesT
                # Update colors and index :
                idxT = np.full((facesT.shape[0],), k, dtype=np.int64)
                self._color_idx = np.concatenate(
                    (self._color_idx, idxT)) if self._color_idx.size else idxT
                color = color2faces(self._color[num], facesT.shape[0])
                self.vertex_colors = np.concatenate(
                    (self.vertex_colors, color)) if self.vertex_colors.size else color
                # Update maximum :
                q = self.faces.max()

        # ============ Transformations ============
        # Finally, apply transformations to vertices :
        tr = vist.STTransform(translate=self._hdr)
        self.vert = tr.map(self.vert)[:, 0:-1]
        self.vert = self._transform.map(self.vert)[:, 0:-1]

    def _smooth(self, data):
        """Volume smoothing.

        Args:
            data: np.ndarray
                Data volume (M, N, P)

        Return:
            data_sm: np.ndarray
                The smoothed data with the same shape as the data (M, N, P)
        """
        if self.smoothsize >= 3:
            # Define smooth arguments :
            sz = np.full((3,), self.smoothsize, dtype=int)
            smooth = np.ones([self.smoothsize] * 3) / np.prod(sz)
            return fftconvolve(data, smooth, mode='same')
        else:
            return data

    def _plot(self):
        """Plot deep areas.

        This method use the BrainMesh class, which is the same as the class
        used for plotting the main MNI brain.
        """
        if self.creation:
            self.mesh = BrainMesh(vertices=self.vert, faces=self.faces,
                                  vertex_colors=self.vertex_colors,
                                  scale_factor=self._scale_factor,
                                  name=self.name, recenter=False)
            self.name = 'displayed'
            self.creation = False
        else:
            # Clean the mesh :
            self.mesh.set_data(vertices=self.vert, faces=self.faces,
                               vertex_colors=self.vertex_colors)

    def _get_idxMask(self, index):
        """Get a boolean array where each structure is located.

        For a list of index, this function return where those index are
        located.

        Args:
            index: list
                List of index. Each index must be an integer. If this parameter
                is None, the entire list is returned.

        Return:
            mask: np.ndarray
                An array of boolean values.
        """
        # Get list of unique index :
        uindex = np.unique(self._color_idx)
        # Create an empty mask :
        mask = np.zeros((len(self._color_idx),), dtype=bool)
        # Convert index :
        if index is None:
            index = list(uindex)
        if not isinstance(index, list):
            index = [index]
        # Check if index exist :
        for k in index:
            if k not in uindex:
                warnings.warn(str(k)+" not found in the list of existing "
                              "areas")
            else:
                mask[self._color_idx == k] = True
        return mask

    # ========================================================================
    # SET FUNCTIONS
    # ========================================================================
    def set_alpha(self, alpha, index=None):
        """Set the transparency level of selected areas.

        This method can be used to set the transparency of deep structures.

        Args:
            alpha: float
                The transparency level. This number must be between 0 and 1.

        Kargs:
            index: list, optional, (def: None)
                List of structures to modify their transparency. This parameter
                must be a list of integers. If index is None, the transparency
                is applied to all structures.
        """
        # Get corresponding index of areas :
        mask = self._get_idxMask(index)
        # Set alpha :
        self.mesh.set_alpha(alpha, index=np.tile(mask[:, np.newaxis], (1, 3)))

    def set_color(self, color, index=None):
        """Set the color of selected areas.

        This method can be used to set the color of deep structures.

        Args:
            color: string/tuple
                The color to use. This parameter can either be a matplotlib
                color or a RGB tuple.

        Kargs:
            index: list, optional, (def: None)
                List of structures to modify their color. This parameter must
                be a list of integers. If index is None, the color is applied
                to all structures.
        """
        # Get corresponding index of areas :
        mask = self._get_idxMask(index)
        # Get RGBA color :
        color = color2vb(color)
        # Set color to vertex color :
        self.vertex_colors[mask, ...] = color
        self.mesh.set_color(self.vertex_colors)
        # Update the mesh :
        self.mesh.update()

    def set_camera(self, camera):
        """Set a camera to the area mesh.

        The camera is essential to get the rotation / translation
        transformations that are then applied to each vertex for adapting the
        color.
        """
        self.mesh.set_camera(camera)

    def update(self):
        """Update ROI."""
        if self.need_update:
            self._load()
            self.need_update = False

    def plot(self):
        """Plot ROI"""
        if self.need_update:
            self._load()
            self.need_update = False
        self._preprocess()
        self._get_vertices()
        self._plot()

    # ========================================================================
    # PROPERTIES
    # ========================================================================
    @property
    def structure(self):
        """Get structure name ('aal' or 'brod)'."""
        return self._structure

    @structure.setter
    def structure(self, value):
        """Set structure name ('aal' or 'brod)'."""
        self._structure = value
        self.need_update = True

    @property
    def select(self):
        """Get selected structures."""
        return self._select

    @select.setter
    def select(self, value):
        """Set selected structures."""
        self._select = value
        self.need_update = True

    @property
    def color(self):
        """Get structure color."""
        return self._color

    @color.setter
    def color(self, value):
        """Set structure color."""
        self._color = value
        self.need_update = True
