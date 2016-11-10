"""This example demonstrate how to display deep sources using MNI
coordinates
"""
from visbrain.vbrain.vbrain_file import vbrain_func
import numpy as np

from neuropype_graph.utils_net import read_Pajek_corres_nodes_and_sparse_matrix

coord_file = "data/IRM/Coord_NetworkAll_OK.txt"

net_file = "data/IRM/Z_List.net"

label_file = "data/IRM/Labels_NetworkAll_OK2.txt"

node_corres,sparse_matrix = read_Pajek_corres_nodes_and_sparse_matrix(net_file)

print sparse_matrix

print node_corres

print "coord_file: ",
print coord_file

coords = np.loadtxt(coord_file)
newCoords = coords[node_corres,:]

#data = np.load('RealDataExample.npz')

#s_data = data['beta']
#s_xyz = data['xyz']

umin = 0.0

umax = 500.0

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
cmap_vmin, cmap_vmax = 0.0,500.0

cmap_under, cmap_over = 'gray', "white"


vb = vbrain_func(s_xyz=newCoords,  c_cmap_vmin=cmap_vmin, c_cmap_vmax=cmap_vmax, c_cmap=c_cmap,cmap_under=cmap_under, cmap_over= cmap_over,c_connect = c_connect)
vb.show()
