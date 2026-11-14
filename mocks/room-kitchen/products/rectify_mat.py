# Rectify the dish mat print out of the listing photo (homography from its four corners), 1000 x 800 = 50 x 40 cm.
import bpy, sys, os, numpy as np
src, dst, corners = sys.argv[sys.argv.index('--') + 1:]
C = np.array([float(v) for v in corners.split(',')]).reshape(4, 2)       # photo px (top-down): back-left, back-right, front-right, front-left
im = bpy.data.images.load(src); W, H = im.size
px = np.empty(W * H * 4, np.float32); im.pixels.foreach_get(px); px = px.reshape(H, W, 4)[::-1]
OW, OH = 1000, 800
D = np.array([[0, 0], [OW, 0], [OW, OH], [0, OH]], float)
A = []
for (x, y), (u, v) in zip(D, C):
    A += [[x, y, 1, 0, 0, 0, -u * x, -u * y, -u], [0, 0, 0, x, y, 1, -v * x, -v * y, -v]]
Hm = np.linalg.svd(np.array(A))[2][-1].reshape(3, 3)
yy, xx = np.mgrid[0:OH, 0:OW] + 0.5
P = Hm @ np.stack([xx.ravel(), yy.ravel(), np.ones(xx.size)])
u, v = P[0] / P[2], P[1] / P[2]
u0, v0 = np.clip(np.floor(u).astype(int), 0, W - 2), np.clip(np.floor(v).astype(int), 0, H - 2); fu, fv = (u - u0)[:, None], (v - v0)[:, None]
out = (px[v0, u0] * (1 - fu) * (1 - fv) + px[v0, u0 + 1] * fu * (1 - fv) + px[v0 + 1, u0] * (1 - fu) * fv + px[v0 + 1, u0 + 1] * fu * fv).reshape(OH, OW, 4)
o = bpy.data.images.new('r', OW, OH); o.pixels.foreach_set(out[::-1].astype(np.float32).ravel()); o.filepath_raw = dst; o.file_format = 'PNG'; o.save()
