"""
Common utility functions.
"""

import json
import logging

import os.path as osp
import numpy as np

logging.basicConfig(filename='viflow.log',
                    filemode='w',
                    format='%(levelname)s : %(message)s',
                    level=logging.INFO)
logger = logging.getLogger('viflow')


def log(msg):
    logger.info(msg)


def load_config(filepath):
    class Config(dict):
        def __init__(self, cfg):
            super(Config, self).__init__(cfg)
            self.__dict__ = self

    with open(filepath) as f:
        cfg = Config(json.load(f))
    for k, v in cfg.items():
        log('cfg: %s=%s' % (k, str(v)))
    return cfg


def load_optical_flow(filepath):
    return np.load(filepath)['arr_0']


def to_filename(filepath):
    base = osp.basename(filepath)
    return osp.splitext(base)[0]
