import vispy.visuals.transforms as vist
from vispy.scene import Node

from .AtlasBase import AtlasBase
from .SourcesBase import SourcesBase
from .ConnectivityBase import ConnectivityBase
from .CmapBase import CmapBase
from .AreaBase import AreaBase
from .transformations import transformations

class elements(CmapBase, transformations):

    """docstring for elements
    """

    def __init__(self, canvas, progressbar, **kwargs):

        # ---------- Initialize elements ----------
        # Initialize transformation with Null:
        self.transform = vist.ChainTransform([vist.NullTransform()])
        self.progressbar = progressbar

        # Initialize brain, sources and connectivity elements :
        self.atlas = AtlasBase(a_transform=self.transform, **kwargs)
        self.sources = SourcesBase(s_transform=self.atlas.transform, **kwargs)
        self.connect = ConnectivityBase(c_transform=self.atlas.transform, c_xyz=self.sources.xyz, **kwargs)
        self.area = AreaBase(scale_factor=self.atlas._scaleMax, name='NoneArea', select=[4, 6],
                             transform=self.atlas.transform, color='#ab4642')

        # Initialize colorbar elements  (by default, with sources elements):
        self.cb = CmapBase(self.view.cbwc, **self.sources._cb)

        # Add transformations :
        transformations.__init__(self, **kwargs)

        # ---------- Panel management ----------
        # Sources panel:
        if self.sources.mesh.name is 'NoneSources':
            self.q_SOURCES.setEnabled(False)
            self.menuTransform.setEnabled(False)
            self.q_TRANS.setEnabled(False)
            self.q_CONNECT.setEnabled(False)
            self.o_Sources.setEnabled(False)
            self.o_Text.setEnabled(False)

        # Text panel:
        if self.sources.stextmesh.name == 'NoneText':
            self.o_Text.setEnabled(False)
            self.grpText.setEnabled(False)
            self.cmapSources.setEnabled(False)

        # Connectivity panel:
        if self.connect.mesh.name == 'NoneConnect':
            self.q_CONNECT.setEnabled(False)
            self.o_Connect.setEnabled(False)
            self.cmapConnect.setEnabled(False)
        self._lw = kwargs.get('c_linewidth', 4.)

        # ---------- Put everything in a root node ----------
        self._vbNode = Node(name='visbrain')
        self.atlas.mesh.parent = self._vbNode
        self.sources.mesh.parent = self._vbNode
        self.connect.mesh.parent = self._vbNode
        self.sources.stextmesh.parent = self._vbNode

