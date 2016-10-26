"""This is the most basic example to illustrate how to start a visbrain instance
and visualize a basic standard MNI brain.
"""
from visbrain.vbrain.vbrain_file import vbrain_func


# ********************************************************************
# 0 - Create a visbrain instance without any customization
# ********************************************************************
vb = vbrain_func(a_template='B3')
vb.show()

