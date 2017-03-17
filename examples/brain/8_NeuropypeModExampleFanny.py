"""This example demonstrate how to display deep sources using MNI
coordinates
"""
from visbrain import Brain
import numpy as np

import os

from neuropype_graph.utils_net import read_Pajek_corres_nodes_and_sparse_matrix

from neuropype_graph.utils_net import read_lol_file

########## coords
coord_file = os.path.abspath("data/MEG/label_coords.txt")

print "coord_file: ",
print coord_file

coords = 1000*np.loadtxt(coord_file)

########## labels 
label_file = os.path.abspath("data/MEG/label_names.txt")


labels = [line.strip() for line in open(label_file)]
npLabels = np.array(labels)
print npLabels

##########  net file
net_file = os.path.abspath("data/MEG/Z_List.net")

node_corres,sparse_matrix = read_Pajek_corres_nodes_and_sparse_matrix(net_file)

print sparse_matrix

print node_corres

############# lol file
lol_file = os.path.abspath("data/MEG/Z_List.lol")

print lol_file

community_vect = read_lol_file(lol_file)

print community_vect

def compute_modular_network(sparse_matrix,community_vect):
    
    mod_mat = np.empty(sparse_matrix.todense().shape) 
    
    mod_mat[:] = np.NAN
    
    for u,v,w in zip(sparse_matrix.row,sparse_matrix.col,sparse_matrix.data):
        
        if (community_vect[u] == community_vect[v]):
            
            mod_mat[u,v] = community_vect[u] 
        else:
            
            mod_mat[u,v] = -1
            
    return mod_mat
          
mod_mat = compute_modular_network(sparse_matrix,community_vect)
print mod_mat.shape

#data = np.load('RealDataExample.npz')

#s_data = data['beta']
#s_xyz = data['xyz']

umin = 0.0

umax = 500.0

c_connect = np.array(mod_mat,dtype = 'float64')+2

c_connect = np.ma.masked_array(c_connect, mask=True)
c_connect.mask[np.where((c_connect > umin) & (c_connect < umax))] = False

print c_connect

# Colormap properties (for connectivity) :
c_cmap = 'jet'		# Matplotlib colormap

corres_coords = coords[node_corres,:]
newLabels = npLabels[node_corres]

vb = Brain(s_xyz=corres_coords,  s_text=newLabels, s_textsize = 2,s_textcolor="white", c_map=c_cmap, c_connect = c_connect)
vb.show()
