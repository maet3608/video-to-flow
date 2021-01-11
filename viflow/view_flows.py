"""
Viewer for optical flow data.
"""

import sys
import cv2
import keyboard

import numpy as np
import os.path as osp
import matplotlib.pyplot as plt

from glob import glob
from viflow.utils import load_config, to_filename, load_optical_flow


def flow2image(flow):
    flow = np.float32(flow)
    mag, ang = cv2.cartToPolar(flow[..., 0], flow[..., 1])
    h, w, _ = flow.shape
    hsv = np.zeros((h, w, 3), dtype=np.float32)
    hsv[..., 1] = 255
    hsv[..., 0] = ang * 180 / np.pi / 2
    hsv[..., 2] = cv2.normalize(mag, None, 0, 255, cv2.NORM_MINMAX)
    return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)


def view_optical_flow(filepath, cfg):
    flows = load_optical_flow(filepath)
    ds = cfg.view_downsample

    plt.ion()
    fig = plt.figure(figsize=(6, 8))
    ax = fig.add_subplot(111)
    ax.set_axis_off()
    ax.set_title(to_filename(filepath))
    fig.show()

    for i in range(flows.shape[0]):
        flow = flows[i][::ds, ::ds, :]
        r, c, _ = flow.shape
        X, Y = np.arange(0, c, 1), np.arange(r, 0, -1)
        U, V = flow[:, :, 0], flow[:, :, 1]

        if cfg.view_mode == 'arrow':
            plot = ax.quiver(X, Y, U, V, scale=100, color=(0, 0, 0, 0.5))
        else:
            plot = ax.imshow(flow2image(flow), alpha=1)

        plt.draw()
        plt.pause(cfg.view_pause)
        plot.remove()


        if keyboard.is_pressed('q'):
            return False

    return True


def main(cfg_filepath):
    cfg = load_config(cfg_filepath)
    inpath = osp.join(cfg.outdir, '*.npz')
    for filepath in glob(inpath):
        if not view_optical_flow(filepath, cfg):
            break


if __name__ == '__main__':
    args = sys.argv
    cfg_filepath = '../config.json' if len(args) == 1 else args[1]
    main(cfg_filepath)
