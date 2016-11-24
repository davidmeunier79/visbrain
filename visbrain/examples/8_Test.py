"""This example demonstrate how to display deep sources using MNI
coordinates
"""
from visbrain.vbrain.vbrain_file import vbrain_func
import numpy as np

from neuropype_graph.utils_net import read_Pajek_corres_nodes_and_sparse_matrix
import Tkinter
import tkFileDialog
#import os, os.path

root = Tkinter.Tk()
coord_file0 = tkFileDialog.askopenfile(title='Choisissez un fichier pour les coordonnees',initialdir='./data/',parent=root)
try:
    coord_file  = coord_file0.name
except:
    coord_file = "data/MEG/label_coords.txt"

net_file0 = tkFileDialog.askopenfile(title='Choisissez un fichier pour les connexions' ,initialdir='./data/',parent=root)
try:
    net_file  = net_file0.name
except:
    net_file = "data/MEG/graph_den_pipe1_den_0_05/_freq_band_name_alpha_permut_-1/prep_rada/Z_List.net"

label_file0 = tkFileDialog.askopenfile(title='Choisissez un fichier pour les labels'     ,initialdir='./data/',parent=root)
try:
    label_file  = label_file0.name
except:
    label_file = "data/MEG/label_names.txt"

node_corres,sparse_matrix = read_Pajek_corres_nodes_and_sparse_matrix(net_file)

print sparse_matrix

print node_corres

print "coord_file: ",
print coord_file

coords = np.loadtxt(coord_file)
newCoords = 1000*coords[node_corres,:]

#data = np.load('RealDataExample.npz')

#s_data = data['beta']
#s_xyz = data['xyz']

umin = 180.0

umax = 800.0

c_connect = np.array(sparse_matrix.todense(),dtype = 'float64')

c_connect = np.ma.masked_array(c_connect, mask=True)
c_connect.mask[np.where((c_connect > umin) & (c_connect < umax))] = False

#c_connect[c_connect != 0] = 0.9

#,dtype = 'float64')
                      
#c_connect = (np.array(sparse_matrix.todense(),dtype = 'float64')/1000.0 + 1.0)/2.0


print c_connect

#print np.min(c_connect),np.max(c_connect)

#c_connect = c_connect - np.min(
#print np.unique(c_connect.astype('float'))


# Colormap properties (for connectivity) :
c_cmap = 'autumn'				# Matplotlib colormap
cmap_vmin, cmap_vmax =  400,500

cmap_under, cmap_over = 'gray', 'white'



vb = vbrain_func(s_xyz=newCoords,  c_cmap_vmin=cmap_vmin, c_cmap_vmax=cmap_vmax, c_cmap=c_cmap,c_cmap_under=cmap_under, c_cmap_over= cmap_over,c_connect = c_connect)
vb.show()
