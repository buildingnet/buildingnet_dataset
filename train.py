import argparse
import os
from GNN.Buildnet.train_model import train_model
import math

parser = argparse.ArgumentParser()

parser.add_argument("-test", "--test", action="store_true", help="Activate test mode")

# training process setting
parser.add_argument('--epoch', type=int, default=1000, help='Number of epochs to train for')
parser.add_argument('--freq_accuracy_test', type=int, default=100, help='when to check for validation accuracy - the nth iteration')
parser.add_argument('--num_building_load', type=int, default=1, help='Number of building to collate and load')
parser.add_argument('--lr', type=float, default=1e-4, help='learning rate')
parser.add_argument('--reg_lr', type=int, default=1e-5, help='weight decay')
parser.add_argument('--num_class',type=int,default=32, help='number of classes')
parser.add_argument('--batch_size',type=int,default=1, help='batchsize')
parser.add_argument('--num_node_features',type=int, default=23, help='number of input features per node')

parser.add_argument('--modeltype',type=str, default='Edge',help='type of model to run: Node - node features only, Edge- Edge features, EdgeLaplacian - Laplacian matrix')
parser.add_argument('--edgetype',type=str, default='similar',help='type of edge attribute: adjacency, similar, containment, all')
parser.add_argument('--optimizer',type=str, default='SGD', help='type of optimizer - Adam or SGD')
parser.add_argument('--normalization',type=str, default='GN', help='batch or group normalization')
parser.add_argument('--nodetype',type=str, default='node', help='pretrained node features')
parser.add_argument('--pretrainedtype',type=str, default='fc3_avg', help='pretrained type')

parser.add_argument('--lrscheduler',type=str, default='ReduceLROnPlateau', help='learning rate scheduler')
parser.add_argument('--lrmode',type=str, default='max', help='learning rate for loss = min for acc = max')
parser.add_argument('--morenodes',type=int, default=0, help='more nodes to use in hidden layers')
parser.add_argument('--reduction',type=str, default='mean', help='mean loss or sum loss')
parser.add_argument('--currepoch',type=int, default=0, help='curr epoch')
parser.add_argument('--curr_loss',type=float, default=math.inf, help='curr loss')
parser.add_argument('--curr_accuracy',type=float, default=0, help='curr accuracy')


# Dataset arguments
parser.add_argument('--datadir', default="data", type=str,help="root folder for storing data")
parser.add_argument('--IOUdir', default="IOU", type=str,help="root folder for saving IOU")
# loading pretrained model

parser.add_argument('--load_model_name',type=str, default='', help='dir of pretrained model')
parser.add_argument('--log_dir', type=str, default='logs', help='dir of logs')
parser.add_argument('--ckpt_dir', type=str, default='checkpoint',help='path to save checkpoints')
parser.add_argument('--loadfromckpt', type=int, default=0,help='restart checkpoints')
parser.add_argument('--IOU_checkpoint', type=int, default=1,help='run IOU every IOU checkpoint epoch')
parser.add_argument('--loadby', type=str, default='accuracy', help='load by best accuracy or best loss')

parser.add_argument('--write',default=True,type=bool)
parser.add_argument('--outputdir',default='.', type=str)
parser.add_argument('--testfile',default='test.txt', type=str)

##########################
opt_parser = parser.parse_args()

if(opt_parser.load_model_name != ''):
    opt_parser.ckpt = os.path.join(ckpt_dir, opt_parser.load_model_name)
else:
    opt_parser.ckpt = ''

M = train_model(args = opt_parser)

if opt_parser.test: 
    M.test(0)
else:
    for epoch in range(1,opt_parser.epoch+1):
        M.train(epoch)

