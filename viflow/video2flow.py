"""
Main application for the conversion of videos to optical flow.
"""

import sys

import datetime
import cv2

import viflow

import numpy as np
import os.path as osp

from glob import glob
from collections import namedtuple
from nutsflow import (nut_processor, nut_function, Consume, Window,
                      PrintProgress, GroupBySorted, Timer, PrintType)

from viflow.utils import logger, log, load_config, to_filename

Frame = namedtuple('Frame', 'filepath, img')


def video_info(cap, filename):
    fnum = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frate = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    log('%s, video: width=%d, height=%d, #fnum=%d, #frate=%d' %
        (filename, width, height, fnum, frate))
    return fnum, frate


def video_frames(cap, filepath, cfg):
    count = -1
    while True:
        count += 1
        if cfg.framerate > 0:
            cap.set(cv2.CAP_PROP_POS_MSEC, int(count * 1000.0 / cfg.framerate))
        success, image = cap.read()
        if not success:
            break
        yield Frame(filepath, image)


def read_numpy(filepath, cfg):
    filename = to_filename(filepath)
    images = np.load(filepath)
    log('%s, input: shape=%s, dtype=%s' %
        (filename, str(images.shape), str(images.dtype)))
    n = images.shape[0]
    for image in iter(images) >> PrintProgress(n, filename):
        yield Frame(filepath, image)


def read_video(filepath, cfg):
    filename = to_filename(filepath)
    cap = cv2.VideoCapture(filepath)
    if not cap.isOpened():
        logger.error('Could not open file:' + filepath)
        return

    fnum, frate = video_info(cap, filename)
    factor = frate if cfg.framerate <= 0 else cfg.framerate
    n = int(fnum / float(frate) * factor)

    yield from video_frames(cap, filepath, cfg) >> PrintProgress(n, filename)
    cap.release()


@nut_processor
def ReadInputs(filepaths, cfg):
    filepaths = list(filepaths)
    n_files = len(filepaths)
    log('processing %d files' % n_files)

    is_numpy = cfg.videoext == "*.npy"
    reader = read_numpy if is_numpy else read_video

    for i, filepath in enumerate(filepaths):
        filename = to_filename(filepath)
        print('Processing %d of %d ' % (i + 1, n_files))
        t = Timer(fmt="%H:%M:%S")
        yield from reader(filepath, cfg)
        log('%s took %s' % (filename, str(t)))


@nut_processor
def CalcOpticalFlow(frames):
    flow_f = cv2.cv2.optflow.createOptFlow_DualTVL1()
    by_video = lambda f: f.filepath
    for filepath, group in frames >> GroupBySorted(by_video):
        flows = []
        for prev_frame, frame in group >> Window(2):
            flow = flow_f.calc(prev_frame.img, frame.img, None)
            flows.append(flow)
        log('%s, #flows=%d' % (to_filename(filepath), len(flows)))
        yield filepath, np.stack(flows)


@nut_function
def CropCenter(frame, cfg):
    img = frame.img
    w, h = cfg.crop_width, cfg.crop_height
    iw, ih = img.shape[1], img.shape[0]
    dw, dh = iw - w, ih - h
    if dw < 0 or dh < 0:
        raise ValueError('Image too small for crop %dx%d' % (iw, ih))
    img = img[dh // 2:dh // 2 + h, dw // 2:dw // 2 + w]
    return frame._replace(img=img)


@nut_function
def ToGrayScale(frame):
    img = frame.img
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return frame._replace(img=img)


@nut_function
def Resize(frame, cfg):
    if cfg.downsample <= 1:
        return frame
    img = frame.img
    c = max(1, cfg.downsample)
    w = int(img.shape[1] / c)
    h = int(img.shape[0] / c)
    img = cv2.resize(img, (w, h), interpolation=cv2.INTER_AREA)
    return frame._replace(img=img)


@nut_function
def WriteOpticalFlow(data, cfg):
    filepath, stack = data
    filename = to_filename(filepath)
    outpath = osp.join(cfg.outdir, filename + '.npz')
    stack = stack.astype(np.float16)
    np.savez_compressed(outpath, stack)
    log('%s, flow: shape=%s, dtype=%s' %
        (filename, str(stack.shape), str(stack.dtype)))
    return data


def process(cfg):
    inpath = osp.join(cfg.videodir, cfg.videoext)
    (glob(inpath) >>
     ReadInputs(cfg) >>
     CropCenter(cfg) >>
     Resize(cfg) >>
     ToGrayScale() >>
     CalcOpticalFlow() >>
     WriteOpticalFlow(cfg) >>
     Consume())


def main(cfg_filepath):
    now = datetime.datetime.now()
    log("running viflow version %s" % viflow.__version__)
    log("running Python version %s" % str(sys.version_info))
    log('processing started at ' + now.strftime("%Y-%m-%d %H:%M"))

    try:
        t = Timer(fmt="%H:%M:%S")
        cfg = load_config(cfg_filepath)
        process(cfg)
        log('processing all took ' + str(t))
        print('finished.')
    except Exception as e:
        logger.error(str(e))
        print(e)


if __name__ == '__main__':
    args = sys.argv
    for arg in args:
        log('arg %s' % str(arg))
    cfg_filepath = '../config.json' if len(args) == 1 else args[1]
    main(cfg_filepath)
