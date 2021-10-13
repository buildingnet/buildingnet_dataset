import torch
import torch.nn.parallel
import torch.optim as optim
import torch.utils.data
from GNN.utils.util import  mlp_channels as mlp_ch, accuracy, save_checkpoint, GNNmodelMeta, CosineAnnealingCustomWarmRestarts as coswarmlr
from GNN.utils.IOU import getComponentPartAndShapeIOUFromList

import time
import pickle
import numpy as np
import os
import math
from random import shuffle
from collections import Counter

from GNN.utils.modelutils import *

import torch.nn.functional as F
from torch.optim.lr_scheduler import CosineAnnealingLR,CosineAnnealingWarmRestarts
from torch.optim.lr_scheduler import ReduceLROnPlateau

from torch_geometric.data import DataLoader
from GNN.Dataset.buildnet_dataset import  BuildnetDataSet

from GNN.Buildnet.model import device
import GNN.Buildnet.model as model

from torch.utils.tensorboard import  SummaryWriter

class train_model():
    def __init__(self, args):
        self.args = args
        self.model = model
        self.outputdir = args.outputdir
        self.batch_size = args.batch_size
        self.modeltype = args.modeltype
        self.edgetype = args.edgetype
        self.normalization = args.normalization
        self.lr = args.lr
        self.epoch = args.epoch
        self.nodetype = args.nodetype
        self.ckpt_dir = args.ckpt_dir
        self.freq_accuracy_test = args.freq_accuracy_test
        self.pretrainedtype = args.pretrainedtype
        self.lrscheduler = args.lrscheduler
        self.lrmode = args.lrmode
        self.morenodes = args.morenodes
        self.reduction = args.reduction

        self.currepoch = args.currepoch

        self.enc_mlp_channels = []
        self.dec_mlp_channels = []

        lossweights = np.array([1+np.log10(1.0), 1+np.log10(9.3881), 1+np.log10(73.6198), 1+np.log10(2.0929), 1+np.log10(20.0007), 1+np.log10(52.7757), \
                   1+np.log10(15.2698), 1+np.log10(103.0988), 1+np.log10(3.4394), 1+np.log10(35.3573), 1+np.log10(78.6826), 1+np.log10(64.8203), \
                   1+np.log10(129.6508), 1+np.log10(7.1101), 1+np.log10(108.0506), 1+np.log10(17.0152), 1+np.log10(29.8406), 1+np.log10(30.1860), \
                   1+np.log10(29.7975), 1+np.log10(51.4241), 1+np.log10(155.6935), 1+np.log10(49.7403), 1+np.log10(22.5732), 1+np.log10(798.2427), \
                   1+np.log10(145.4640), 1+np.log10(146.3673), 1+np.log10(363.9013), 1+np.log10(5364.9608), 1+np.log10(288.8161), 1+np.log10(670.3790), \
                   1+np.log10(1363.5492)])

        minweight = min(lossweights)
        maxweight = max(lossweights)
        lossweights =  (lossweights - minweight)/(maxweight - minweight) + 1
        self.class_weights = torch.FloatTensor(lossweights).cuda()

        numedgefeatures, numnodefeatures, inputfeature_enc, inputfeature_dec = getInputFeatureSize(args.modeltype, self.edgetype, self.nodetype, self.pretrainedtype)

        print("input feature size {}".format(inputfeature_enc), flush=True)
        if args.modeltype == 'Edge':
            ################ ENCODER ###########################################           
            mlp_ch_edge = mlp_ch(numedgefeatures, 64, numnodefeatures, 1,0)
            mlp_ch1 = mlp_ch(inputfeature_enc, 256, 64, 1,0) 
            mlp_ch2 = mlp_ch(64*3, 128, 64, 3,0) 
            mlp_ch3 = mlp_ch(64*3, 128, 128, 5,0)
            self.enc_mlp_channels = [mlp_ch1, mlp_ch2, mlp_ch3]
            self.enc_edge_mlp_channels = [mlp_ch_edge]
            encmodelmeta_edge = GNNmodelMeta(self.enc_edge_mlp_channels, args.normalization)
            encmodelmeta = GNNmodelMeta(self.enc_mlp_channels, args.normalization)

            ################# DECODER ########################################
            mlp_ch_dec = mlp_ch(128, 64, args.num_class-1, 1) 
            #mlp_ch_dec = mlp_ch(1024, 512, args.num_class-1, 1) 
            self.dec_mlp_channels = [mlp_ch_dec]
            decmodelmeta = GNNmodelMeta(self.dec_mlp_channels, args.normalization)

            self.buildnet_enc = self.model.BuildnetEnc_Edge(modelmeta_edge = encmodelmeta_edge, modelmeta=encmodelmeta)
            self.buildnet_dec = self.model.BuildnetDec_Edge(modelmeta = decmodelmeta)

        elif args.modeltype == 'Node':
            mlp_ch1 = mlp_ch(inputfeature_enc, 256, 64, 1,0) 
            mlp_ch2 = mlp_ch(64, 128, 64, 3,0) 
            mlp_ch3 = mlp_ch(64, 128, 128, 5,0)
            self.enc_mlp_channels = [mlp_ch1, mlp_ch2, mlp_ch3]
            self.dec_mlp_channels = [mlp_ch(128,64,args.num_class-1,1)]

            encmodelmeta = GNNmodelMeta(self.enc_mlp_channels, args.normalization)
            decmodelmeta = GNNmodelMeta(self.dec_mlp_channels, args.normalization)
            self.buildnet_enc = self.model.BuildnetEnc_Node(modelmeta = encmodelmeta) 
            self.buildnet_dec = self.model.BuildnetDec_Node(modelmeta = decmodelmeta)

        if torch.cuda.device_count() > 1:
            print("Using {} GPUS".format(torch.cuda.device_count()), flush=True)


        self.buildnet_enc.to(device)
        self.buildnet_dec.to(device)

        ''' load valid buildings '''
        self.validation_data = DataLoader(BuildnetDataSet(root= args.datadir, typeofdata='val', typeofedge=self.edgetype, nodefeature=self.nodetype, pretrainedtype=self.pretrainedtype), batch_size=self.batch_size, shuffle=False, num_workers=0)
        self.training_data = DataLoader(BuildnetDataSet(root = args.datadir, typeofdata='train', typeofedge=self.edgetype, nodefeature=self.nodetype, pretrainedtype=self.pretrainedtype), batch_size=self.batch_size, shuffle=True, num_workers=0)
        self.test_data = DataLoader(BuildnetDataSet(root = args.datadir, typeofdata='test', typeofedge=self.edgetype, nodefeature=self.nodetype, pretrainedtype=self.pretrainedtype), batch_size=self.batch_size, shuffle=False, num_workers=0)

        self.iters = len(self.training_data)

        ''' Setup Optimizer '''
        self.opt = {'buildnet_enc':None, 'buildnet_dec':None}
        if args.optimizer == 'adam':
            self.opt['buildnet_enc'] = optim.Adam(self.buildnet_enc.parameters(), lr=args.lr, weight_decay=args.reg_lr)
            self.opt['buildnet_dec'] = optim.Adam(self.buildnet_dec.parameters(), lr=args.lr, weight_decay=args.reg_lr)
        elif args.optimizer == 'SGD':
            self.opt['buildnet_enc'] = optim.SGD(self.buildnet_enc.parameters(), lr=args.lr, weight_decay=args.reg_lr, momentum=0.9)
            self.opt['buildnet_dec'] = optim.SGD(self.buildnet_dec.parameters(), lr=args.lr, weight_decay=args.reg_lr, momentum=0.9)
        self.opt['buildnet_enc'].zero_grad()
        self.opt['buildnet_dec'].zero_grad()

        ''' scheduler for learning rate '''
        self.scheduler = {}
        self.scheduler['buildnet_enc'] = ReduceLROnPlateau(optimizer=self.opt['buildnet_enc'],factor=0.1,patience=10,mode=self.lrmode, threshold=1e-4)
        self.scheduler['buildnet_dec'] = ReduceLROnPlateau(optimizer=self.opt['buildnet_dec'],factor=0.1,patience=10,mode=self.lrmode, threshold=1e-4)
        #self.scheduler['buildnet_enc'] = ReduceLROnPlateau(optimizer=self.opt['buildnet_enc'],factor=0.5,patience=3,mode=self.lrmode, threshold=1e-2, min_lr=1e-05)
        #self.scheduler['buildnet_dec'] = ReduceLROnPlateau(optimizer=self.opt['buildnet_dec'],factor=0.1,patience=3,mode=self.lrmode, threshold=1e-2, min_lr=1e-06)
        if self.lrscheduler == 'cosine':
            self.scheduler['buildnet_enc'] = coswarmlr(self.opt['buildnet_enc'], T_0=self.T_0*self.iters, T_mult=self.T_mul)
            self.scheduler['buildnet_dec'] = coswarmlr(self.opt['buildnet_dec'], T_0=self.T_0*self.iters, T_mult=self.T_mul)

        ''' Load pre-trained model '''
        self.pretrained_epoch = 0
        self.best_loss = self.args.curr_loss # math.inf
        self.best_acc = self.args.curr_accuracy # 0
        if args.loadfromckpt:
            checkpointpath = os.path.join(self.args.ckpt_dir, self.args.modeltype, self.args.edgetype, str(self.args.lr),str(self.args.nodetype))
            path = os.path.join(checkpointpath, 'checkpoint.pth.tar')
            if os.path.exists(path):
                checkpoint = torch.load(path)
                self.buildnet_enc.load_state_dict(checkpoint['buildnet_enc'])
                self.buildnet_dec.load_state_dict(checkpoint['buildnet_dec'])
                self.opt['buildnet_enc'].load_state_dict(checkpoint['optimizer_enc'])
                self.opt['buildnet_dec'].load_state_dict(checkpoint['optimizer_dec'])
                self.scheduler['buildnet_enc'].load_state_dict(checkpoint['scheduler_enc'])
                self.scheduler['buildnet_dec'].load_state_dict(checkpoint['scheduler_dec'])
                self.pretrained_epoch = checkpoint['epoch']
                self.best_loss = checkpoint['best_loss']
                self.best_acc = checkpoint['best_acc']
                print(self.pretrained_epoch, flush=True)
                print(self.best_loss, flush=True)
                print(self.best_acc, flush=True)
            

        ''' Loss function '''
        self.LOSS_CLS = torch.nn.CrossEntropyLoss(reduction=args.reduction, ignore_index=-1, weight=self.class_weights)

        ''' Output Summary in tensorboard '''
        if args.write:
            logdir=os.path.join(args.log_dir, args.modeltype, args.edgetype, str(args.lr), str(args.nodetype)) 
            if not os.path.exists(logdir):
                os.makedirs(logdir)
            suffix=""
            self.writer = SummaryWriter(log_dir=logdir, filename_suffix=suffix)



    def epoch_pass(self, epoch, building_data, istraining, isTest=False, npypath=None, testfilename=None):
        epoch += self.pretrained_epoch

        epoch_loss = 0
        epoch_acc = 0
        if istraining:
            self.buildnet_enc.train()
            self.buildnet_dec.train()
            #self.currepoch += 1

            for param_group in self.opt['buildnet_enc'].param_groups:
                print("LR_enc::{}".format(param_group['lr']))
            for param_group in self.opt['buildnet_dec'].param_groups:
                print("LR_dec::{}".format(param_group['lr']))
        else:
            self.buildnet_enc.eval()
            self.buildnet_dec.eval()


        epoch_data_count = 0
        epoch_acc_data_count = 0
        buildingcount = 0
        for index,building in enumerate(building_data):
            data = building.to(device)
            numnodes = data.numnodes
            indexreduced_y = data.y - 1
            #print(numnodes.shape, flush=True)
            
            self.opt['buildnet_enc'].zero_grad() 
            self.opt['buildnet_dec'].zero_grad()

            if self.modeltype == "Node":
                with torch.set_grad_enabled(istraining):
                    enc_result = self.buildnet_enc((data.x).float())
                    dec_result = self.buildnet_dec(enc_result)

            elif self.modeltype == "Edge":
                numedges = data.numedges
                nodepair = data.nodepair
                #print(sum(numnodes), flush=True)
                #print(nodepair.shape, flush=True)
                #print(numedges, flush=True)
                #print(sum(numedges), flush=True)

                if (index % 50) == 0:
                    print("Building = {} ".format(index),flush=True)

                #print(nodepair.shape)
                   
                if self.batch_size > 1:
                    nodepair = reassignNodePairIndex(numnodes,numedges,nodepair)
                    #print(len(nodepair))

               # if istraining:
               #     if len(nodepair) > 100000:
               #         continue

                with torch.set_grad_enabled(istraining):
                    node_neighbour_index, nodepair, attribute = getNodeNeighbourRelation(nodepair, data.attribute)
                    #random.shuffle(nodepair)
                    enc_result_edge = self.buildnet_enc(data.x, nodepair, attribute, node_neighbour_index)
                    dec_result = self.buildnet_dec(enc_result_edge)

            batch_loss = (self.LOSS_CLS(dec_result, indexreduced_y.long())).mean()
            dec_softmax_result = F.softmax(dec_result, 1)

            _,preds = torch.max(dec_softmax_result, dim=-1)
            if istraining:
                batch_loss.backward()
                self.opt['buildnet_enc'].step()
                self.opt['buildnet_dec'].step()

            epoch_loss += batch_loss.item()
            epoch_data_count += self.batch_size

            batch_acc, acc_data_count = accuracy(preds, indexreduced_y)
            #print(batch_acc)
            epoch_acc  += float(batch_acc.item())
            epoch_acc_data_count += acc_data_count
        

            if isTest:
            #orig_y = indexreduced_y.cpu().numpy()
                building_preds = preds.cpu().numpy()
                with open(os.path.join(npypath,testfilename[index]+".npy"), "wb") as fwrite:
                    np.save(fwrite, building_preds)
            #test_result = {'orig':orig_y, 'pred':building_preds}
            #pickle.dump(test_result,open(os.path.join(picklepath,testfilename[buildingcount]+".pkl"), "wb"))

            if (index % self.freq_accuracy_test) == 0:
                if istraining:
                    print("Building {} : Train -> loss :: {} and accuracy :: {}".format(index, epoch_loss/epoch_data_count, epoch_acc/epoch_acc_data_count),flush=True)
                else:
                    if isTest:
                        print("Building {} : Test -> loss :: {} and accuracy :: {}".format(index, epoch_loss/epoch_data_count, epoch_acc/epoch_acc_data_count),flush=True)
                    else:
                        print("Building {} : Val -> loss :: {} and accuracy :: {}".format(index, epoch_loss/epoch_data_count, epoch_acc/epoch_acc_data_count),flush=True)
        #if buildingcount == 2:
        #    break

        epoch_loss_avg = epoch_loss/epoch_data_count
        epoch_acc_avg = epoch_acc/epoch_acc_data_count

        if istraining:
            if self.lrscheduler == 'ReduceLROnPlateau':
                if self.lrmode == 'min':
                    self.scheduler['buildnet_enc'].step(epoch_loss_avg)
                    self.scheduler['buildnet_dec'].step(epoch_loss_avg)
                    for param_group in self.opt['buildnet_enc'].param_groups:
                        print("LR_enc_step::{}".format(param_group['lr']), flush=True)
                    for param_group in self.opt['buildnet_dec'].param_groups:
                        print("LR_dec_step::{}".format(param_group['lr']), flush=True)
                elif self.lrmode == 'max':
                    self.scheduler['buildnet_enc'].step(epoch_acc_avg)
                    self.scheduler['buildnet_dec'].step(epoch_acc_avg)
                    for param_group in self.opt['buildnet_enc'].param_groups:
                        print("LR_enc_step::{}".format(param_group['lr']), flush=True)
                    for param_group in self.opt['buildnet_dec'].param_groups:
                        print("LR_dec_step::{}".format(param_group['lr']), flush=True)
            else:
                    #print("did not enter if")
                    self.scheduler['buildnet_enc'].step()
                    self.scheduler['buildnet_dec'].step()

        
        return epoch_loss_avg, epoch_acc_avg

    def train(self, epoch):
        reloadepoch = self.pretrained_epoch
        reloadepoch += epoch
        if reloadepoch >= self.epoch:
            print("epoch greater than max epoch")
            return
        start_time = time.time()
        train_loss, train_acc = self.epoch_pass(epoch, self.training_data, True)
        val_loss, val_acc = self.epoch_pass(epoch, self.validation_data, False)
        print('Epoch {:d} '.format(reloadepoch), flush=True)
        print('train_loss: {:.6f}'.format(train_loss), flush=True) 
        print('train_acc: {:.6f}'.format(train_acc), flush=True) 
        print('val_loss: {:.6f}'.format(val_loss), flush=True) 
        print('val_acc: {:.6f}'.format(val_acc), flush=True) 
        print('time usage {}'.format(time.time() - start_time), flush=True)

        checkpointpath = os.path.join(self.args.ckpt_dir, self.args.modeltype, self.args.edgetype, str(self.args.lr),str(self.args.nodetype))
        if not os.path.exists(checkpointpath):
            os.makedirs(checkpointpath)

        is_best_loss = val_loss <= self.best_loss
        self.best_loss = min(val_loss, self.best_loss)
        is_best_acc = val_acc >= self.best_acc
        self.best_acc = max(val_acc, self.best_acc)

        save_checkpoint({'epoch':reloadepoch+1, 'currepoch':epoch, 'best_loss':self.best_loss, 'best_acc':self.best_acc, 'buildnet_enc': self.buildnet_enc.state_dict(), \
                         'buildnet_dec':self.buildnet_dec.state_dict(),\
                         'optimizer_enc':self.opt['buildnet_enc'].state_dict(), \
                         'optimizer_dec':self.opt['buildnet_dec'].state_dict(), \
                         'scheduler_enc':self.scheduler['buildnet_enc'].state_dict(), \
                         'scheduler_dec': self.scheduler['buildnet_dec'].state_dict()}, path=checkpointpath,epoch=reloadepoch,is_best_loss=is_best_loss, is_best_acc=is_best_acc)

        if(self.args.write):
            self.writer.add_scalar('train/loss',train_loss, epoch+1)
            self.writer.add_scalar('train/acc',train_acc, epoch+1)
            self.writer.add_scalar('val/loss',val_loss, epoch+1)
            self.writer.add_scalar('val/acc',val_acc, epoch+1)
        if epoch % int(self.args.IOU_checkpoint) == 0:
            self.test(epoch)


    def test(self,epoch):
        start_time = time.time()
        checkpointpath = os.path.join(self.args.ckpt_dir, self.args.modeltype, self.args.edgetype, str(self.args.lr),str(self.args.nodetype)) 
        #if not os.path.exists(checkpointpath):
        #    os.makedirs(checkpointpath)
        testfilepath = open(os.path.join(self.args.datadir,self.args.testfile),'r')
        testfile = []
        for line in testfilepath:
            line = line.strip()
            testfile.append(line)
        testfilepath.close()
        
        ckpt_files = os.listdir(checkpointpath)
        for fname in ['checkpoint_best_acc','checkpoint_best_loss']: 
            print(fname, flush=True)
            path = os.path.join(checkpointpath, fname+'.pth.tar')
             
            checkpoint = torch.load(path)
            self.buildnet_enc.load_state_dict(checkpoint['buildnet_enc'])
            self.buildnet_dec.load_state_dict(checkpoint['buildnet_dec'])
            self.opt['buildnet_enc'].load_state_dict(checkpoint['optimizer_enc'])
            self.opt['buildnet_dec'].load_state_dict(checkpoint['optimizer_dec'])
            self.scheduler['buildnet_enc'].load_state_dict(checkpoint['scheduler_enc'])
            self.scheduler['buildnet_dec'].load_state_dict(checkpoint['scheduler_dec'])

            #picklepath = os.path.join(self.args.outputdir, self.args.modeltype, self.args.edgetype, str(self.args.lr),str(self.args.nodetype), str(self.args.loadby))
            npypath = os.path.join(self.args.outputdir, self.args.modeltype, self.args.edgetype, str(self.args.lr),str(self.args.nodetype), fname)
            IOUname = self.args.modeltype+"_"+self.args.edgetype+"_"+str(self.args.lr)+"_"+str(self.args.nodetype)+"_"+fname
            if not os.path.exists(npypath):
                 os.makedirs(npypath)
            if "train" in self.args.testfile:
                test_loss, test_acc = self.epoch_pass(epoch, self.training_data, istraining=False, isTest=True, npypath=npypath, testfilename=testfile)
            else:
                test_loss, test_acc = self.epoch_pass(epoch, self.test_data, istraining=False, isTest=True, npypath=npypath, testfilename=testfile)
            print('epoch {} test_loss: {:.6f}'.format(epoch, test_loss), flush=True) 
            print('epoch {} test_acc: {:.6f}'.format(epoch, test_acc), flush=True) 
            print('time usage: {}'.format(time.time() - start_time), flush=True)
            if not os.path.exists(self.args.IOUdir):
                os.makedirs(self.args.IOUdir)
            getComponentPartAndShapeIOUFromList(os.path.join(self.args.datadir,self.args.testfile), os.path.join(self.args.datadir, 'label'), os.path.join(self.args.datadir, 'surfacearea'), npypath, self.args.IOUdir, IOUname)  

