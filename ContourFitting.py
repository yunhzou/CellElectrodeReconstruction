import pyvista as pv
import numpy as np
import pandas as pd 
import cv2
import matplotlib.pyplot as plt

def add_alpha_channel(img):
    #b, g, r = cv2.split(img)
    
    #alpha = np.where((b==0) & (g==0) & (r==0), 0, 255)
    alpha = np.sum(img,axis =-1)>0
    alpha = np.uint8(alpha*255)
    #alpha = alpha.astype(np.uint8)
    res = np.dstack((img,alpha))
    #rgba_img = cv2.merge([r, g, b, alpha])
    return res

df = pd.read_csv("spiral.csv")
img = cv2.imread("simulation\electrode.png", cv2.IMREAD_UNCHANGED)
img = img[:, :, [2, 1, 0]]
w,h = (int(img.shape[1]/2),int(img.shape[0]/2 ))
img = cv2.resize(img,(w,h))
img = add_alpha_channel(img)
total_length = 3800
pixel2real = total_length/w #in milimeter
lengths = np.linspace(0,total_length,img.shape[1])
#Pixel position for mesh
x_interp = np.interp(lengths, df['total_length'], df['x'])/pixel2real
y_interp = np.interp(lengths, df['total_length'], df['y'])/pixel2real
z = np.linspace(0,h,h)

X, Z = np.meshgrid(x_interp, z)
Y, Z = np.meshgrid(y_interp, z)
u,v = np.meshgrid(np.linspace(0,h,h)/h,np.linspace(0,w,w)/w)
t_coords = np.vstack((v.flatten(),u.flatten())).T


grid = pv.StructuredGrid(X, Y, Z)
grid.active_t_coords = t_coords
texture = pv.Texture(img)
plotter = pv.Plotter()
plotter.add_mesh(grid,texture=texture,opacity=1)
plotter.show()