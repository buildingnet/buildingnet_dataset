import json
import logging
import os
import errno
import time

import numpy as np
import torch


def checkpoint(model, optimizer, epoch, iteration, config, best_val_part_iou=None, best_val_part_iou_iter=None,
               best_val_shape_iou=None, best_val_shape_iou_iter=None, best_val_loss=None, best_val_loss_iter=None,
               best_val_acc=None, best_val_acc_iter=None, postfix=None):
    os.makedirs(config.log_dir, exist_ok=True)
    if config.overwrite_weights:
        if postfix is not None:
            filename = f"checkpoint_{config.model}{postfix}.pth"
        else:
            filename = f"checkpoint_{config.model}.pth"
    else:
        filename = f"checkpoint_{config.model}_iter_{iteration}.pth"
    checkpoint_file = os.path.join(config.log_dir, filename)
    state = {
        'iteration': iteration,
        'epoch': epoch,
        'arch': config.model,
        'state_dict': model.state_dict(),
        'optimizer': optimizer.state_dict()
    }
    if best_val_part_iou is not None:
        state['best_val_part_iou'] = best_val_part_iou
        state['best_val_part_iou_iter'] = best_val_part_iou_iter
    if best_val_shape_iou is not None:
        state['best_val_shape_iou'] = best_val_shape_iou
        state['best_val_shape_iou_iter'] = best_val_shape_iou_iter
    if best_val_loss is not None:
        state['best_val_loss'] = best_val_loss
        state['best_val_loss_iter'] = best_val_loss_iter
    if best_val_acc is not None:
        state['best_val_acc'] = best_val_acc
        state['best_val_acc_iter'] = best_val_acc_iter
    json.dump(vars(config), open(config.log_dir + '/config.json', 'w'), indent=4)
    torch.save(state, checkpoint_file)
    logging.info(f"Checkpoint saved to {checkpoint_file}")

    if postfix is None:
        # Delete symlink if it exists
        if os.path.exists(f'{config.log_dir}/weights.pth'):
            os.remove(f'{config.log_dir}/weights.pth')
        # Create symlink
        os.system(f'cd {config.log_dir}; ln -s {filename} weights.pth')


class WithTimer(object):
    """Timer for with statement."""

    def __init__(self, name=None):
        self.name = name

    def __enter__(self):
        self.tstart = time.time()

    def __exit__(self, type, value, traceback):
        out_str = 'Elapsed: %s' % (time.time() - self.tstart)
        if self.name:
            logging.info('[{self.name}]')
        logging.info(out_str)


class Timer(object):
    """A simple timer."""

    def __init__(self):
        self.total_time = 0.
        self.calls = 0
        self.start_time = 0.
        self.diff = 0.
        self.average_time = 0.

    def reset(self):
        self.total_time = 0
        self.calls = 0
        self.start_time = 0
        self.diff = 0
        self.averate_time = 0

    def tic(self):
        # using time.time instead of time.clock because time time.clock
        # does not normalize for multithreading
        self.start_time = time.time()

    def toc(self, average=True):
        self.diff = time.time() - self.start_time
        self.total_time += self.diff
        self.calls += 1
        self.average_time = self.total_time / self.calls
        if average:
            return self.average_time
        else:
            return self.diff


class ExpTimer(Timer):
    """ Exponential Moving Average Timer """

    def __init__(self, alpha=0.5):
        super(ExpTimer, self).__init__()
        self.alpha = alpha

    def toc(self):
        self.diff = time.time() - self.start_time
        self.average_time = self.alpha * self.diff + \
                            (1 - self.alpha) * self.average_time
        return self.average_time


class AverageMeter(object):
    """Computes and stores the average and current value"""

    def __init__(self):
        self.reset()

    def reset(self):
        self.val = 0
        self.avg = 0
        self.sum = 0
        self.count = 0

    def update(self, val, n=1):
        self.val = val
        self.sum += val * n
        self.count += n
        self.avg = self.sum / self.count


def read_txt(path):
    """Read txt file into lines.
    """
    with open(path) as f:
        lines = f.readlines()
    lines = [x.strip() for x in lines]
    return lines


def debug_on():
    import sys
    import pdb
    import functools
    import traceback

    def decorator(f):

        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except Exception:
                info = sys.exc_info()
                traceback.print_exception(*info)
                pdb.post_mortem(info[2])

        return wrapper

    return decorator


def get_prediction(dataset, output, target):
    return output.max(1)[1]


def count_parameters(model):
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


def get_torch_device(is_cuda):
    return torch.device('cuda' if is_cuda else 'cpu')


class HashTimeBatch(object):

    def __init__(self, prime=5279):
        self.prime = prime

    def __call__(self, time, batch):
        return self.hash(time, batch)

    def hash(self, time, batch):
        return self.prime * batch + time

    def dehash(self, key):
        time = key % self.prime
        batch = key / self.prime
        return time, batch
