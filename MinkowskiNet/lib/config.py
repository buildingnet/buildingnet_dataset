import argparse


def str2opt(arg):
    assert arg in ['SGD', 'Adam']
    return arg


def str2scheduler(arg):
    assert arg in ['StepLR', 'PolyLR', 'ExpLR', 'SquaredLR', 'ReduceLROnPlateau', 'MultiStepLR', 'CosineAnnealingLR']
    return arg


def str2bool(v):
    return v.lower() in ('true', '1')


def str2list(l):
    return [int(i) for i in l.split(',')]


def add_argument_group(name):
    arg = parser.add_argument_group(name)
    arg_lists.append(arg)
    return arg


def required_length(nmin, nmax):
    class RequiredLength(argparse.Action):
        def __call__(self, parser, args, values, option_string=None):
            if not nmin <= len(values) <= nmax:
                msg = 'argument "{f}" requires between {nmin} and {nmax} arguments'.format(
                    f=self.dest, nmin=nmin, nmax=nmax)
                raise argparse.ArgumentTypeError(msg)
            setattr(args, self.dest, values)

    return RequiredLength


arg_lists = []
parser = argparse.ArgumentParser()

# Network
net_arg = add_argument_group('Network')
net_arg.add_argument('--model', type=str, default=None, help='Model name')
net_arg.add_argument('--conv1_kernel_size', type=int, default=5, help='First layer conv kernel size')
net_arg.add_argument('--weights', type=str, default='None', help='Saved weights to load')

# Optimizer arguments
opt_arg = add_argument_group('Optimizer')
opt_arg.add_argument('--optimizer', type=str, default='SGD')
opt_arg.add_argument('--lr', type=float, default=1e-2)
opt_arg.add_argument('--sgd_momentum', type=float, default=0.9)
opt_arg.add_argument('--sgd_dampening', type=float, default=0.1)
opt_arg.add_argument('--adam_beta1', type=float, default=0.9)
opt_arg.add_argument('--adam_beta2', type=float, default=0.999)
opt_arg.add_argument('--weight_decay', type=float, default=1e-4)
opt_arg.add_argument('--param_histogram_freq', type=int, default=5)
opt_arg.add_argument('--save_param_histogram', type=str2bool, default=False)
opt_arg.add_argument('--iter_size', type=int, default=1, help='accumulate gradient')
opt_arg.add_argument('--bn_momentum', type=float, default=0.02)

# Scheduler
opt_arg.add_argument('--scheduler', type=str2scheduler, default='StepLR')
opt_arg.add_argument('--max_iter', type=int, default=6e4)
opt_arg.add_argument('--max_epoch', type=int, default=200)
opt_arg.add_argument('--step_size', type=int, default=10000)
opt_arg.add_argument('--step_gamma', type=float, default=0.5)
opt_arg.add_argument('--poly_power', type=float, default=0.9)
opt_arg.add_argument('--exp_gamma', type=float, default=0.99)
opt_arg.add_argument('--exp_step_size', type=int, default=445)

# Directories
dir_arg = add_argument_group('Directories')
dir_arg.add_argument('--log_dir', type=str, default='outputs/default')

# Data
data_arg = add_argument_group('Data')
data_arg.add_argument('--dataset', type=str, default='ScannetVoxelization2cmDataset')
data_arg.add_argument('--batch_size', type=int, default=16)
data_arg.add_argument('--val_batch_size', type=int, default=1)
data_arg.add_argument('--test_batch_size', type=int, default=1)
data_arg.add_argument('--num_workers', type=int, default=0, help='num workers for train/test dataloader')
data_arg.add_argument('--num_val_workers', type=int, default=0, help='num workers for val dataloader')
data_arg.add_argument('--ignore_label', type=int, default=255)
data_arg.add_argument('--return_transformation', type=str2bool, default=False)
data_arg.add_argument('--prefetch_data', type=str2bool, default=False)
data_arg.add_argument('--train_limit_numpoints', type=int, default=0)

# Point Cloud Dataset
data_arg.add_argument('--buildingnet_path', type=str, default='',
                      help='BuildingNet online voxelization dataset root dir')

# Training / test parameters
train_arg = add_argument_group('Training')
train_arg.add_argument('--is_train', type=str2bool, default=True)
train_arg.add_argument('--stat_freq', type=int, default=40, help='print frequency')
train_arg.add_argument('--test_stat_freq', type=int, default=100, help='print frequency')
train_arg.add_argument('--save_freq', type=int, default=1000, help='save frequency')
train_arg.add_argument('--val_freq', type=int, default=1000, help='validation frequency')
train_arg.add_argument('--empty_cache_freq', type=int, default=1, help='Clear pytorch cache frequency')
train_arg.add_argument('--train_phase', type=str, default='train', help='Dataset for training')
train_arg.add_argument('--val_phase', type=str, default='val', help='Dataset for validation')
train_arg.add_argument('--overwrite_weights', type=str2bool, default=True, help='Overwrite checkpoint during training')
train_arg.add_argument('--resume', default=None, type=str, help='path to latest checkpoint (default: none)')
train_arg.add_argument('--resume_optimizer', default=True, type=str2bool,
                       help='Use checkpoint optimizer states when resume training')
train_arg.add_argument('--weighted_cross_entropy', type=str2bool, default=False, help='Use weighted cross entropy')
train_arg.add_argument('--weighted_focal_loss', type=str2bool, default=False, help='Use weighted focal loss')
train_arg.add_argument('--input_feat', type=str, default='rgb', help='Input features')

# Data augmentation
data_aug_arg = add_argument_group('DataAugmentation')
data_aug_arg.add_argument('--shift', type=str2bool, default=False)
data_aug_arg.add_argument('--rot_aug', type=str2bool, default=False)

# Test
test_arg = add_argument_group('Test')
test_arg.add_argument('--test_phase', type=str, default='test', help='Dataset for test')
test_arg.add_argument('--evaluate', type=str2bool, default=False, help='Evaluate model on the validation split')
test_arg.add_argument('--export_predictions', type=str2bool, default=False,
                      help='Export predictions for the validation and test splits')
test_arg.add_argument('--export_features', type=str2bool, default=False, help='Export features for the whole dataset')


# Misc
misc_arg = add_argument_group('Misc')
misc_arg.add_argument('--is_cuda', type=str2bool, default=True)
misc_arg.add_argument('--load_path', type=str, default='')
misc_arg.add_argument('--log_step', type=int, default=50)
misc_arg.add_argument('--log_level', type=str, default='INFO', choices=['INFO', 'DEBUG', 'WARN'])
misc_arg.add_argument('--seed', type=int, default=123)
misc_arg.add_argument('--quantize_labels', type=str2bool, default=True, help='Coordinates quantization using labels')
misc_arg.add_argument('--avg_feat', type=str2bool, default=False,
                      help='Average all features within a quantization block equally')
misc_arg.add_argument('--opt_speed', type=str2bool, default=False,
                      help='Run faster at the cost of more memory')


def get_config():
    config = parser.parse_args()

    import MinkowskiEngine as ME
    mink_settings = {}
    # Quantization mode
    if config.avg_feat:
        mink_settings["q_mode"] = ME.SparseTensorQuantizationMode.UNWEIGHTED_AVERAGE
    else:
        mink_settings["q_mode"] = ME.SparseTensorQuantizationMode.RANDOM_SUBSAMPLE

    # Minkowski algorithm
    if config.opt_speed:
        mink_settings["mink_algo"] = ME.MinkowskiAlgorithm.SPEED_OPTIMIZED
    else:
        mink_settings["mink_algo"] = ME.MinkowskiAlgorithm.MEMORY_EFFICIENT

    return config, mink_settings  # Training settings
