


import torch
import hamiltorch
import matplotlib.pyplot as plt

import torch.nn as nn
import torch.nn.functional as F

hamiltorch.set_random_seed(123)
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

from google.colab import drive
drive.mount('/content/drive')

!unzip '/content/drive/My Drive/data_bnn.zip'

!unzip '/content/drive/My Drive/100.zip'

from PIL import Image
from torchvision.transforms import ToTensor
from PIL import ImageEnhance
from PIL import ImageFilter
import torch
from os import listdir
from os.path import isfile, join
import matplotlib.pyplot as plt


#base_path = '/content/drive/My Drive/xray_dataset_covid19/'
base_path = '/content/data'

train_path = base_path +'/training'
test_path = base_path + '/test'
valid_path = base_path + '/validation'

#img_size = (180, 180) # net 3
img_size = (28, 28) # For net 1 and 2

def DataSetGenerator(path, img_size=img_size):
  normal_path = path + '/NORMAL'
  viral_path = path + '/VIRAL'
  norm_files = listdir(normal_path)
  viral_files = listdir(viral_path)
  labels = []
  img = []
  for file in norm_files:
    img_path = normal_path + '/' + file
    image = Image.open(img_path).convert('LA')   
    image = image.resize(img_size, Image.ANTIALIAS)

    image = ToTensor()(image)
    #image = torch.mean(image, dim=0).unsqueeze(0)
    img.append(image)
    labels.append(torch.FloatTensor([0]))

  for file in viral_files:
    img_path = viral_path + '/' + file
    image = Image.open(img_path).convert('LA')

    image = image.resize(img_size, Image.ANTIALIAS)
    image = ToTensor()(image)
    #image = torch.mean(image, dim=0).unsqueeze(0)
    img.append(image)
    labels.append(torch.FloatTensor([1]))
  return torch.stack(img,dim=0), torch.stack(labels,dim=0)

x_train, y_train = DataSetGenerator(train_path)
x_train = x_train.to(device)
y_train = y_train.to(device)
x_valid, y_valid = DataSetGenerator(valid_path)
x_valid = x_valid.to(device)
y_valid = y_valid.to(device)
x_test, y_test = DataSetGenerator(test_path)
x_test = x_test.to(device)
y_test = y_test.to(device)

class Net_1(nn.Module):
    
    def __init__(self): #input (28,28)
        super(Net_1, self).__init__()
        self.fc1 = nn.Linear(28*28*2, 1024)
        self.out = nn.Linear(1024, 2)
        
    def forward(self, x):
        output = x.view(-1, 28*28*2)
        output = self.fc1(output)
        output = F.relu(output)
        output = self.out(output)
        return F.log_softmax(output, dim=1)



class Net_2(nn.Module):  #input (28, 28)
    """ConvNet -> Max_Pool -> RELU -> ConvNet -> Max_Pool -> RELU -> FC -> RELU -> FC -> SOFTMAX"""
    def __init__(self):
        super(Net_2, self).__init__()
        self.conv1 = nn.Conv2d(2, 20, 5, 1)
        self.conv2 = nn.Conv2d(20, 50, 5, 1)
        self.fc1 = nn.Linear(4*4*50, 500)
        self.fc2 = nn.Linear(500, 2)

    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = F.max_pool2d(x, 2, 2)
        x = F.relu(self.conv2(x))
        x = F.max_pool2d(x, 2, 2)
        x = x.view(-1, 4*4*50)
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
#         return x#torch.softmax(x)
        return F.log_softmax(x, dim=1)

class Net_3(nn.Module):  #input (292, 292)
    """ConvNet -> Max_Pool -> RELU -> ConvNet -> Max_Pool -> RELU -> FC -> RELU -> FC -> SOFTMAX"""
    def __init__(self):
        super(Net_3, self).__init__()
        self.conv1 = nn.Conv2d(2, 20, 5 , 1)
        self.conv11 = nn.Conv2d(20, 20, 5 , 1)
        self.conv2 = nn.Conv2d(20, 50, 5 , 1)
        self.fc1 = nn.Linear(4*4*50, 200)
        self.fc2 = nn.Linear(200, 2)

    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = F.max_pool2d(x, 4, 4)
        x = F.relu(self.conv11(x))
        x = F.max_pool2d(x, 2, 2)
        x = F.relu(self.conv2(x))
        x = F.max_pool2d(x, 4, 4)
        x = x.view(-1, 4*4*50)
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
#         return x#torch.softmax(x)
        return F.log_softmax(x, dim=1)

pip install memory_profiler

# Commented out IPython magic to ensure Python compatibility.
# %load_ext memory_profiler
import numpy as np

"""# numero iterazioni alto """

#del params_hmc,pred_list
torch.cuda.empty_cache()
net = Net_1()
cnt=0
tau_list = []
tau = 1/5#./100. # 1/50
for w in net.parameters():
  cnt+=1
#     print(w.nelement())
#     tau_list.append(tau/w.nelement())
  tau_list.append(tau)
    
tau_list = torch.tensor(tau_list).to(device)

hamiltorch.set_random_seed(123)

params_init = hamiltorch.util.flatten(net).to(device).clone()
print(params_init.shape)


a = 0.0001#0.01# 0.003#0.002
num_samples = 6000 # 2000
L = 2 #3
tau_out = 1.
normalizing_const = 148
burn =4000#GPU: 2000
acc_mean=[]
step_size=0.0085

# Commented out IPython magic to ensure Python compatibility.
# %%time
# %memit params_hmc = hamiltorch.sample_model(net, x_train, y_train, params_init=params_init, model_loss='multi_class_log_softmax_output', num_samples=num_samples, burn = burn, step_size=step_size, num_steps_per_sample=L,tau_out=tau_out, tau_list=tau_list, normalizing_const=normalizing_const)
#     
# 
#

# Commented out IPython magic to ensure Python compatibility.
# %time pred_list, log_prob_list = hamiltorch.predict_model(net, x=x_test, y=y_test, samples=params_hmc, model_loss='multi_class_log_softmax_output', tau_out=1., tau_list=tau_list)
_, pred = torch.max(pred_list, 2)
acc_net2 = []
s=0
cnt=0
for i in range(pred.shape[0]):
  a = (pred[i].float() == y_test.flatten()).sum().float()/y_test.shape[0]
  acc_net2.append(a)
  if a>0.8:
    cnt+=1
    if cnt>40:
      s=i
    else: 
      cnt=0
it_2=s   

plt.plot(acc_net2)
acc_net2[989]

a=np.exp(pred_list[:,:,0].cpu())
b=np.exp(pred_list[:,:,1].cpu())
prob=[a/(a+b),b/(a+b)]
prob= (torch.stack(prob))
prob.size()

# Commented out IPython magic to ensure Python compatibility.
def waic_hmc(x_test,y_test):
#   %time pred_list, log_prob_list = hamiltorch.predict_model(net, x=x_test, y=y_test, samples=params_hmc, model_loss='multi_class_log_softmax_output', tau_out=1., tau_list=tau_list)
  a=np.exp(pred_list[:,:,0].cpu())
  b=np.exp(pred_list[:,:,1].cpu())
  prob=[a/(a+b),b/(a+b)]
  prob= (torch.stack(prob))


  num_samples=100
  N=1000
  lppd=0
  pwaic=0
  for i in range(len(y_test)):
    partial_lppd=0
    pvar=np.zeros_like(range(num_samples))
    for n in range(num_samples):
      partial_lppd+=prob[int(y_test[i]),1000-num_samples+n,i]
      pvar[n]=(np.log(prob[int(y_test[i]),1000-num_samples+n,i]+ np.finfo(float).eps))
    pwaic+=np.var(pvar)
    lppd+=np.log(partial_lppd/num_samples) 
  print(lppd)
  print(pwaic)
  return lppd-pwaic


waic_hmc(x_test,y_test)

# Commented out IPython magic to ensure Python compatibility.
# %time pred_list, log_prob_list = hamiltorch.predict_model(net, x = x_test, y = y_test, samples=params_hmc, model_loss='multi_class_log_softmax_output', tau_out=1., tau_list=tau_list)
_, pred = torch.max(pred_list, 2)
acc_e = torch.zeros( len(pred_list)-1)
nll_e = torch.zeros( len(pred_list)-1)
ensemble_proba = F.softmax(pred_list[0], dim=-1)
for s in range(1,len(pred_list)):
    _, pred = torch.max(pred_list[:s].mean(0), -1)
    acc_e[s-1] = (pred.float() == y_test.flatten()).sum().float()/y_test.shape[0]
    ensemble_proba += F.softmax(pred_list[s], dim=-1)
    nll_e[s-1] = F.nll_loss(torch.log(ensemble_proba.cpu()/(s+1)), y_test[:].long().cpu().flatten(), reduction='mean')

ensemble_proba=[]
for s in range(len(pred_list)):
    a = F.softmax(pred_list[s], dim=-1)
    ensemble_proba.append(a)
ensemble_proba[1].cpu().size()
p=[]
pp=[]
for j in range(len(pred_list)):
  a=ensemble_proba[j].cpu()
  p.append(a[3,0])
  b=ensemble_proba[j].cpu()
  pp.append(a[3,1])
plt.hist(p[1000:1500],40)
plt.hist(pp[1000:1500],40)

p1=[]
p2=[]
pred_list.size()
for j in range(1000):
  a=np.exp(pred_list[j,0,0].cpu())
  b=np.exp(pred_list[j,0,1].cpu())

  p1.append(a/(a+b))
  p2.append(b/(a+b))

plt.hist(p1,40)  
plt.hist(p2,40)  
pred_list[:,1,0].std(0).cpu().numpy().squeeze().T

burn = 10

plt.figure(figsize=(10,5))
plt.plot(x_test.cpu().numpy(),pred_list.cpu().numpy().squeeze().T, 'C0',alpha=0.051)
plt.plot(x_test.cpu().numpy(),pred_list.mean(0).cpu().numpy().squeeze().T, 'C1',alpha=0.9)
plt.plot(x_test.cpu().numpy(),pred_list.mean(0).cpu().numpy().squeeze().T +pred_list.std(0).cpu().numpy().squeeze().T, 'C1',alpha=0.8,linewidth=3)
plt.plot(x_test.cpu().numpy(),pred_list.mean(0).cpu().numpy().squeeze().T -pred_list.std(0).cpu().numpy().squeeze().T, 'C1',alpha=0.8,linewidth=3)

plt.plot(x_train.cpu().numpy(),y_train.cpu().numpy(),'.C3',markersize=30, label='x train',alpha=0.6)

plt.legend(fontsize=20)
plt.ylim([-5,5])
plt.show()

points_net2_5=[]
points_net2_1=[]

n4=196691
n1=196690

for i in range(1000):
  a=params_hmc[i][n4].cpu()

  b=params_hmc[i][n1].cpu()
  points_net2_5.append(np.exp(a))
  points_net2_1.append(np.exp(b))
plt.hist(points_net2_1)
plt.hist(points_net2_5)
plt.savefig('ole.jpeg')

m = pred_list[427572,:,:].mean(0).to('cpu')
s = pred_list[1500:,:,:].std(0).to('cpu')
s_al = (pred_list[1500:].var(0).to('cpu') + tau_out ** -1) ** 0.5
plt.hist(s_al)

plt.hist(points_net2_5)

"""# **Net** 2"""

net = Net_2()
cnt=0
tau_list = []
tau = 1/5#./100. # 1/50
for w in net.parameters():
  cnt+=1
#     print(w.nelement())
#     tau_list.append(tau/w.nelement())
  tau_list.append(tau)
    
tau_list = torch.tensor(tau_list).to(device)

hamiltorch.set_random_seed(123)

params_init = hamiltorch.util.flatten(net).to(device).clone()
#print(params_init.shape)


num_samples = 4500 # 2000
L = 2 #3
tau_out = 1.
normalizing_const = 1.
burn =2000#GPU: 2500
acc_mean=[]
step_size=0.0055

# Commented out IPython magic to ensure Python compatibility.
# %%time
# %memit params_hmc = hamiltorch.sample_model(net, x_train, y_train, params_init=params_init, model_loss='multi_class_log_softmax_output', num_samples=num_samples, burn = burn, step_size=step_size, num_steps_per_sample=L,tau_out=tau_out, tau_list=tau_list, normalizing_const=normalizing_const)
# 
# 
#

torch.pred

# Commented out IPython magic to ensure Python compatibility.
# %time pred_list, log_prob_list = hamiltorch.predict_model(net, x=x_valid, y=y_valid, samples=params_hmc, model_loss='multi_class_log_softmax_output', tau_out=1., tau_list=tau_list)
_, pred = torch.max(pred_list, 2)
acc_net2 = []
s=0
cnt=0
for i in range(pred.shape[0]):
  a = (pred[i].float() == y_valid.flatten()).sum().float()/y_valid.shape[0]
  acc_net2.append(a)
  if a>0.8:
    cnt+=1
    if cnt>40:
      s=i
    else: 
      cnt=0

plt.figure(figsize=(12,8))
plt.plot(acc_net2)
plt.xlabel('Samples')
plt.ylabel('Accuracy')

print(len(acc_net2))
plt.savefig('Acc_net_2.png')

# Commented out IPython magic to ensure Python compatibility.
# #### ROC curve construction
# #### We have in prob the probabilities, extracted via softmax, of the two classe, look how sensitivity and specificity changes as we chane the threshold
# %%time 
# pred_list, log_prob_list = hamiltorch.predict_model(net, x=x_valid, y=y_valid, samples=params_hmc, model_loss='multi_class_log_softmax_output', tau_out=1., tau_list=tau_list)
# a=np.exp(pred_list[:,:,0].cpu())
# b=np.exp(pred_list[:,:,1].cpu())
# prob=[a/(a+b),b/(a+b)]
# num_it=200
# 
# prob= (torch.stack(prob))
# TP=np.zeros_like(range(num_it+1))
# FP=np.zeros_like(range(num_it+1))
# num_samples=300
# for p in range(num_it+1):
#   cnt=0
#   for im in range(len(y_valid)):
#     mean=0
#     for j in range(num_samples):
#       mean+=prob[0,2500-num_samples+j,im]
#     mean=mean/num_samples  
#     if (p/num_it)>mean:
#       pred=1
#     else:
#       pred=0
#     if pred==y_valid[im]:
#       if pred==1:
#         TP[p]+=1
#     if pred!=y_valid[im]:
#       if pred==1:
#         FP[p]+=1
#         
# 
#       
# TP=TP/100
# FP=FP/100
# FP[num_it]=1 # just for the plot if not it stops earlier
# TP[num_it]=1
# plt.plot([0,1],[0,1])
# plt.plot(FP,TP)
# plt.title('ROC curve', fontsize=8)
# plt.ylabel('Sensitivity')
# plt.xlabel('Specificity')
# 
# plt.savefig('ROC_net_2.png')

# Commented out IPython magic to ensure Python compatibility.
def waic_hmc(x_test,y_test):
#   %time pred_list, log_prob_list = hamiltorch.predict_model(net, x=x_test, y=y_test, samples=params_hmc, model_loss='multi_class_log_softmax_output', tau_out=1., tau_list=tau_list)
  a=np.exp(pred_list[:,:,0].cpu())
  b=np.exp(pred_list[:,:,1].cpu())
  prob=[a/(a+b),b/(a+b)]
  prob= (torch.stack(prob))


  num_samples=200
  N=1000
  lppd=0
  pwaic=0
  for i in range(len(y_test)):
    partial_lppd=0
    pvar=np.zeros_like(range(num_samples))
    for n in range(num_samples):
      partial_lppd+=prob[int(y_test[i]),2500-num_samples+n,i]
      pvar[n]=(np.log(prob[int(y_test[i]),2500-num_samples+n,i]+ np.finfo(float).eps))
    pwaic+=np.var(pvar)
    lppd+=np.log(partial_lppd/num_samples+np.finfo(float).eps) 
  print(lppd)
  print(pwaic)
  return lppd-pwaic

waic_hmc(x_test,y_test)

### Hist of predictive samples
# one image for covid one for healthy
healthy=np.random.randint(0,99,size=1)
covid=np.random.randint(100,199,size=1)
num_samples=100
plt.hist(prob[0,(2500-num_samples):2499,healthy],bins=15)
plt.title('Histogram of the predictive distribution')
plt.savefig('hist_net_2_h.png')

plt.hist(prob[0,(2500-num_samples):2499,covid],bins=30)
plt.title('Histogram of the predictive distribution')
plt.savefig('hist_net_2_c.png')

####Mean uncertainty

del params_hmc,pred,pred_list
torch.cuda.empty_cache()

x_test[0,1,:,:]

"""# Net 1"""

net = Net_1()
cnt=0
tau_list = []
tau = 1/3#./100. # 1/50
for w in net.parameters():
  cnt+=1
#     print(w.nelement())
#     tau_list.append(tau/w.nelement())
  tau_list.append(tau)
    
tau_list = torch.tensor(tau_list).to(device)

hamiltorch.set_random_seed(123)

params_init = hamiltorch.util.flatten(net).to(device).clone()
print(params_init.shape)


a = 0.0001#0.01# 0.003#0.002
num_samples = 8500 # 2000
L = 2 #3
tau_out = 1.
normalizing_const = 1.
burn =6000#GPU: 2000
acc_mean=[]
step_size=0.017

# Commented out IPython magic to ensure Python compatibility.
# %%time
# %memit params_hmc = hamiltorch.sample_model(net, x_train, y_train, params_init=params_init, model_loss='multi_class_log_softmax_output', num_samples=num_samples, burn = burn, step_size=step_size, num_steps_per_sample=L,tau_out=tau_out, tau_list=tau_list, normalizing_const=normalizing_const)
#     
# 
#

# Commented out IPython magic to ensure Python compatibility.
# %time pred_list, log_prob_list = hamiltorch.predict_model(net, x=x_valid, y=y_valid, samples=params_hmc, model_loss='multi_class_log_softmax_output', tau_out=1., tau_list=tau_list)
_, pred = torch.max(pred_list, 2)
acc_net2 = []
s=0
cnt=0
for i in range(pred.shape[0]):
  a = (pred[i].float() == y_valid.flatten()).sum().float()/y_valid.shape[0]
  acc_net2.append(a)
  if a>0.8:
    cnt+=1
    if cnt>40:
      s=i
    else: 
      cnt=0

plt.figure(figsize=(12,8))
plt.plot(acc_net2)
plt.xlabel('Samples')
plt.ylabel('Accuracy')

print(len(acc_net2))
plt.savefig('Acc_net_2.png')

# Commented out IPython magic to ensure Python compatibility.
# #### ROC curve construction
# #### We have in prob the probabilities, extracted via softmax, of the two classe, look how sensitivity and specificity changes as we chane the threshold
# %%time 
# pred_list, log_prob_list = hamiltorch.predict_model(net, x=x_test, y=y_test, samples=params_hmc, model_loss='multi_class_log_softmax_output', tau_out=1., tau_list=tau_list)
# a=np.exp(pred_list[:,:,0].cpu())
# b=np.exp(pred_list[:,:,1].cpu())
# prob=[a/(a+b),b/(a+b)]
# num_it=100
# 
# prob= (torch.stack(prob))
# TP=np.zeros_like(range(num_it+1))
# FP=np.zeros_like(range(num_it+1))
# num_samples=50
# for p in range(num_it+1):
#   cnt=0
#   print(p/num_it)
#   for im in range(len(y_test)):
#     mean=0
#     for j in range(num_samples):
#       mean+=prob[0,2500-num_samples+j,im]
#     mean=mean/num_samples  
#     if (p/num_it)>=mean:
#       pred=1
#     else:
#       pred=0
#     if pred==y_test[im]:
#       if pred==1:
#         TP[p]+=1
#     if pred!=y_test[im]:
#       if pred==1:
#         FP[p]+=1
#         
# 
# 
# TP=TP/60
# FP=FP/60
# TP[0]=0.
# FP[0]=0.
# area=0
# for j in range(100):
#   area +=(TP[j+1])*(FP[j+1]-FP[j])
# 
# TP[num_it]=1
# FP[num_it]=1
# plt.plot([0,1],[0,1])
# plt.plot(FP,TP)
# plt.title('ROC curve', fontsize=8)
# plt.ylabel('Sensitivity')
# plt.xlabel('1-Specificity')
#

TP[49]
FP[49]*60

##noise
x_train[0].size()
img = x_train[0] #original img
 
n_rand = 100#number of noisy imgs
img_size = (28,28)
images_random = torch.rand(100,img_size[0], img_size[1]) #noise
images_random = images_random.to(device) #??
new_rand = []
for i in range(n_rand):
  a=img + ((images_random[i,:,:])-0.5)*0.25
  a-=torch.min(a)
  a=a/torch.max(a)
  new_rand.append(a)
new_rand = torch.stack(new_rand)
labels = [0]*n_rand
labels = torch.Tensor(labels)
pred_list, log_prob_list = hamiltorch.predict_model(net, x=new_rand, y=labels, samples=params_hmc, model_loss='multi_class_log_softmax_output', tau_out=1., tau_list=tau_list)
sf = nn.Softmax(dim=2)
s = sf(pred_list[2000:2499,:,:])
s = torch.mean(s, dim=0)
plt.xlim((0,1))
plt.hist(s[:,0].cpu().numpy(), bins=20, alpha=0.5, label='x')
#plt.hist(s[:,1].cpu().numpy(),  alpha=0.5, label='y')
torch.var(s[:,0].cpu())


plt.savefig('noisy_hist_HMC.png')

0.25/12

from PIL import Image
images_random.cpu().size()

a=Image.fromarray(np.uint8(np.array(new_rand[0,0,:,:].cpu())*255.))
a=a.resize(size=(512,512))
a

# Commented out IPython magic to ensure Python compatibility.
def waic_hmc(x_test,y_test):
#   %time pred_list, log_prob_list = hamiltorch.predict_model(net, x=x_test, y=y_test, samples=params_hmc, model_loss='multi_class_log_softmax_output', tau_out=1., tau_list=tau_list)
  a=np.exp(pred_list[:,:,0].cpu())
  b=np.exp(pred_list[:,:,1].cpu())
  prob=[a/(a+b),b/(a+b)]
  prob= (torch.stack(prob))


  num_samples=200
  N=1000
  lppd=0
  pwaic=0
  for i in range(len(y_test)):
    partial_lppd=0
    pvar=np.zeros_like(range(num_samples))
    for n in range(num_samples):
      partial_lppd+=prob[int(y_test[i]),1500-num_samples+n,i]
      pvar[n]=(np.log(prob[int(y_test[i]),1500-num_samples+n,i]+ np.finfo(float).eps))
    pwaic+=np.var(pvar)
    lppd+=np.log(partial_lppd/num_samples+np.finfo(float).eps) 
  print(lppd)
  print(pwaic)
  return lppd-pwaic

waic_hmc(x_test,y_test)

del params_hmc,pred,pred_list
torch.cuda.empty_cache()

# Commented out IPython magic to ensure Python compatibility.
# %time pred_list, log_prob_list = hamiltorch.predict_model(net, x=x_test, y=y_test, samples=params_hmc, model_loss='multi_class_log_softmax_output', tau_out=1., tau_list=tau_list)
_, pred = torch.max(pred_list, 2)
acc_net1 = []
s=0
cnt=0
for i in range(pred.shape[0]):
  a = (pred[i].float() == y_test.flatten()).sum().float()/y_test.shape[0]
  acc_net1.append(a)
  if a>0.8:
    cnt+=1
    if cnt>40:
      s=i
    else: 
      cnt=0

it_1=s    
print(it_1)

points_net1_1=[]
points_net1_2=[]
points_net1_3=[]
points_net1_4=[]
points_net1_5=[]

n1=np.random.randint(805890,size=1)
n2=np.random.randint(805890,size=1)
n3=np.random.randint(805890,size=1)
n4=np.random.randint(805890,size=1)
n5=np.random.randint(805890,size=1)



for i in range(500,4000):
  a=params_hmc[i][n1].cpu()
  points_net1_1.append(a)
  a=params_hmc[i][n2].cpu()
  points_net1_2.append(a)
  a=params_hmc[i][n3].cpu()
  points_net1_3.append(a)
  a=params_hmc[i][n4].cpu()
  points_net1_4.append(a)
  a=params_hmc[i][n5].cpu()
  points_net1_5.append(a)

del x_train, y_train
torch.cuda.empty_cache()

"""# Net 3"""

from PIL import Image
from torchvision.transforms import ToTensor
from PIL import ImageEnhance
from PIL import ImageFilter
import torch
from os import listdir
from os.path import isfile, join

#base_path = '/content/drive/My Drive/xray_dataset_covid19/'
base_path = '/content/drive/My Drive/progetto/'

train_path = base_path + 'train'
test_path = base_path + 'test'

img_size = (180, 180)
#img_size = (28, 28)

def DataSetGenerator(path, img_size=img_size):
  normal_path = path + '/NORMAL'
  pneu_path = path + '/PNEUMONIA'

  norm_files = listdir(normal_path)
  pneu_files = listdir(pneu_path)

  labels = []
  img = []
  for file in norm_files:
    img_path = normal_path + '/' + file
    image = Image.open(img_path)   
    image = image.resize(img_size, Image.ANTIALIAS)
    image = ToTensor()(image)
    image = torch.mean(image, dim=0).unsqueeze(0)
    img.append(image)
    labels.append(torch.FloatTensor([0]))

  for file in pneu_files:
    img_path = pneu_path + '/' + file
    image = Image.open(img_path)
    image = image.resize(img_size, Image.ANTIALIAS)
    image = ToTensor()(image)
    image = torch.mean(image, dim=0).unsqueeze(0)
    img.append(image)
    labels.append(torch.FloatTensor([1]))

  return torch.stack(img,dim=0), torch.stack(labels,dim=0)

x_train, y_train = DataSetGenerator(train_path)

x_test, y_test = DataSetGenerator(test_path) 

x_train = x_train.to(device)
y_train = y_train.to(device)
x_test = x_test.to(device)
y_test = y_test.to(device)
x_train.size()

del params_hmc,pred,pred_list
torch.cuda.empty_cache()

net = Net_3()
cnt=0
tau_list = []
tau = 1/6#./100. # 1/50
for w in net.parameters():
  cnt+=1
#     print(w.nelement())
#     tau_list.append(tau/w.nelement())
  tau_list.append(tau)
    
tau_list = torch.tensor(tau_list).to(device)

hamiltorch.set_random_seed(123)

params_init = hamiltorch.util.flatten(net).to(device).clone()
print(params_init.shape)


a = 0.0001#0.01# 0.003#0.002
num_samples = 4000 # 2000
L = 2 #3
tau_out = 1.
normalizing_const = 1.
burn =0#GPU: 2000
acc_mean=[]
step_size=0.005

# Commented out IPython magic to ensure Python compatibility.
# %%time
# %memit params_hmc = hamiltorch.sample_model(net, x_train, y_train, params_init=params_init, model_loss='multi_class_log_softmax_output', num_samples=num_samples, burn = burn, step_size=step_size, num_steps_per_sample=L,tau_out=tau_out, tau_list=tau_list, normalizing_const=normalizing_const)
#     
# 
#



# Commented out IPython magic to ensure Python compatibility.
# %time pred_list, log_prob_list = hamiltorch.predict_model(net, x=x_test, y=y_test, samples=params_hmc, model_loss='multi_class_log_softmax_output', tau_out=1., tau_list=tau_list)
_, pred = torch.max(pred_list, 2)
acc_net3 = []
s=0
cnt=0
for i in range(pred.shape[0]):
  a = (pred[i].float() == y_test.flatten()).sum().float()/y_test.shape[0]
  acc_net3.append(a)
  if a>0.8:
    cnt+=1
    if cnt>40:
      s=i
    else: 
      cnt=0

it_3=s     
print(it_3)

points_net3_1=[]
points_net3_2=[]
points_net3_3=[]
points_net3_4=[]
points_net3_5=[]

n1=np.random.randint(196192,size=1)
n2=np.random.randint(196192,size=1)
n3=np.random.randint(196192,size=1)
n4=np.random.randint(196192,size=1)
n5=np.random.randint(196192,size=1)

for i in range(500,4000):
  a=params_hmc[i][n1].cpu()
  points_net3_1.append(a)
  a=params_hmc[i][n2].cpu()
  points_net3_2.append(a)
  a=params_hmc[i][n3].cpu()
  points_net3_3.append(a)
  a=params_hmc[i][n4].cpu()
  points_net3_4.append(a)
  a=params_hmc[i][n5].cpu()
  points_net3_5.append(a)
del params_hmc, pred,pred_list
torch.cuda.empty_cache()

import numpy as np

acc1=np.array(acc_net1)
acc2=np.array(acc_net2)
acc3=np.array(acc_net3)
fig,axs = plt.subplots(3,1,constrained_layout=True,figsize=(25,15))

fig.suptitle('Accuracy of each net',fontsize=60)

axs[0].plot(acc1, alpha=0.8)
axs[0].set_title('Net 1: acceptance rate 0.75',fontsize=20)
axs[1].plot(acc2, alpha=0.8)
axs[1].set_title('Net 2: acceptance rate 0.67',fontsize=20)
axs[2].plot(acc3, alpha=0.8)
axs[2].set_title('Net 3: acceptance rate 0.65',fontsize=20)

plt.savefig('acc_nets_f.jpg')
fig,axs = plt.subplots(3,1,constrained_layout=True,figsize=(15,15))
fig.suptitle('Exploration of parameters space',fontsize=60)
axs[0].plot(points_net1_1, alpha=0.8)
axs[0].plot(points_net1_2, alpha=0.8)
axs[0].plot(points_net1_3, alpha=0.8)
axs[0].plot(points_net1_4, alpha=0.8)
axs[0].plot(points_net1_5, alpha=0.8)
axs[0].set_title('Net 1',fontsize=20)
axs[1].plot(points_net2_1, alpha=0.8)
axs[1].plot(points_net2_2, alpha=0.8)
axs[1].plot(points_net2_3, alpha=0.8)
axs[1].plot(points_net2_4, alpha=0.8)
axs[1].plot(points_net2_5, alpha=0.8)
axs[1].set_title('Net 2',fontsize=20)
axs[2].plot(points_net3_1, alpha=0.8)
axs[2].plot(points_net3_2, alpha=0.8)
axs[2].plot(points_net3_3, alpha=0.8)
axs[2].plot(points_net3_4, alpha=0.8)
axs[2].plot(points_net3_5, alpha=0.8)
axs[2].set_title('Net 3',fontsize=20)

plt.savefig('para_f.jpg')
points_net1_1=torch.Tensor(points_net1_1).cpu()
points_net2_1=torch.Tensor(points_net2_1).cpu()
points_net3_1=torch.Tensor(points_net3_1).cpu()
points_net2_3=torch.Tensor(points_net2_3).cpu()
points_net2_4=torch.Tensor(points_net2_4).cpu()
points_net2_5=torch.Tensor(points_net2_5).cpu()


fig,axs = plt.subplots(3,1,constrained_layout=True,figsize=(20,15))
fig.suptitle('Posteriors',fontsize=60)
axs[0].hist(points_net1_3[1000:3500],20,alpha=0.5)
axs[0].set_title('Net 1',fontsize=20)
axs[1].hist(points_net2_5[1000:3500],20, alpha=0.5)
axs[1].set_title('Net 2',fontsize=20)
axs[2].hist(points_net3_4[500:3000],20, alpha=0.5)
axs[2].set_title('Net 3',fontsize=20)

plt.savefig('post_f.jpg')

found=0
s1=0
cnt=0
for i in range(len(acc_net1)):
  if found==0:
    a = acc_net1[i]
    if a>0.8:
      cnt+=1
      if cnt>60:
        s1=i
        found=1
    else:
      cnt=0  
found=0
s2=0
cnt=0
for i in range(len(acc_net2)):
  if found==0:
    a = acc_net2[i]
    if a>0.8:
      cnt+=1
      if cnt>60:
        s2=i
        found=1
    else:
      cnt=0  
found=0
s=0
cnt=0
for i in range(len(acc_net3)):
  if found==0:
    a = acc_net3[i]
    if a>0.8:
      cnt+=1
      if cnt>60:
        s=i
        found=1
    else:
      cnt=0  
print(s1*57/4000,s2*125/4000,s*(14.75*60)/4000)
print(s1/400,s2/400,s/400)

"""# Step size selection"""

##### NO RUN ######
net = Net_2()
cnt=0
tau_list = []
tau = 1/5 #./100. # 1/50
for w in net.parameters():
  cnt+=1
#     print(w.nelement())
#     tau_list.append(tau/w.nelement())
  tau_list.append(tau)
    
tau_list = torch.tensor(tau_list).to(device)

hamiltorch.set_random_seed(123)

params_init = hamiltorch.util.flatten(net).to(device).clone()
print(params_init.shape)
#step_size = 0.0001*j# 0.000001-0.01
x_val = x_train[0:15,:,:,:]
x_val1=x_train[133:147,:,:,:]
a = x_train[16:132,:,:,:]
xtrain1 = a
x_val = torch.cat([x_val,x_val1],0)
y_val = y_train[0:15,]
y_val1=y_train[133:147,]
y_val = torch.cat([y_val,y_val1],0)

a = y_train[16:132,]
#y_train1 = torch.cat([a,b],0)

ytrain1=a  

a = 0.0001#0.01# 0.003#0.002
num_samples = 2000 # 2000
L = 2 #3
tau_out = 1.
normalizing_const = 1.
burn =000 #GPU: 2000
#del params_hmc
torch.cuda.empty_cache()

# Commented out IPython magic to ensure Python compatibility.
step_size = 0.001*0.1 # 0.0001 #0.001 #0.01 #0.15 #1 
# %time params_hmc_1 = hamiltorch.sample_model(net, xtrain1, ytrain1, params_init=params_init, model_loss='multi_class_log_softmax_output', num_samples=num_samples, burn = burn, step_size=step_size, num_steps_per_sample=L,tau_out=tau_out, tau_list=tau_list, normalizing_const=normalizing_const)

# %time pred_list, log_prob_list = hamiltorch.predict_model(net, x=x_val, y=y_val, samples=params_hmc_1, model_loss='multi_class_log_softmax_output', tau_out=1., tau_list=tau_list)
_, pred = torch.max(pred_list, 2)
acc1 = []
for i in range(pred.shape[0]):
    a = (pred[i].float() == y_val.flatten()).sum().float()/y_val.shape[0]
    acc1.append(a)
               
points_1a=[]
for ii in range(500,2000):
  a=params_hmc_1[ii][5000].cpu()
  points_1a.append(a)
points_1b=[]
for ii in range(500,2000):
  a=params_hmc_1[ii][100000].cpu()
  points_1b.append(a)

del params_hmc_1
torch.cuda.empty_cache()

# Commented out IPython magic to ensure Python compatibility.

step_size = 0.001*5 # 0.0001 #0.001 #0.01 #0.15 #1 
# %time params_hmc_8 = hamiltorch.sample_model(net, xtrain1, ytrain1, params_init=params_init, model_loss='multi_class_log_softmax_output', num_samples=num_samples, burn = burn, step_size=step_size, num_steps_per_sample=L,tau_out=tau_out, tau_list=tau_list, normalizing_const=normalizing_const)

# %time pred_list, log_prob_list = hamiltorch.predict_model(net, x=x_val, y=y_val, samples=params_hmc_8, model_loss='multi_class_log_softmax_output', tau_out=1., tau_list=tau_list)
_, pred = torch.max(pred_list, 2)
acc8 = []
for i in range(pred.shape[0]):
    a = (pred[i].float() == y_val.flatten()).sum().float()/y_val.shape[0]
    acc8.append(a)
                 

points_8a=[]
for ii in range(500,2000):
  a=params_hmc_8[ii][5000].cpu()
  points_8a.append(a)
points_8b=[]
for ii in range(500,2000):
  a=params_hmc_8[ii][100000].cpu()
  points_8b.append(a)
del params_hmc_8
torch.cuda.empty_cache()

# Commented out IPython magic to ensure Python compatibility.

step_size = 0.001*9 # 0.0001 #0.001 #0.01 #0.15 #1 
# %time params_hmc_10 = hamiltorch.sample_model(net, xtrain1, ytrain1, params_init=params_init, model_loss='multi_class_log_softmax_output', num_samples=num_samples, burn = burn, step_size=step_size, num_steps_per_sample=L,tau_out=tau_out, tau_list=tau_list, normalizing_const=normalizing_const)


# %time pred_list, log_prob_list = hamiltorch.predict_model(net, x=x_val, y=y_val, samples=params_hmc_10, model_loss='multi_class_log_softmax_output', tau_out=1., tau_list=tau_list)
_, pred = torch.max(pred_list, 2)
acc10 = []
for i in range(pred.shape[0]):
    a = (pred[i].float() == y_val.flatten()).sum().float()/y_val.shape[0]
    acc10.append(a)
points_10a=[]
for ii in range(500,2000):
  a=params_hmc_10[ii][5000].cpu()
  points_10a.append(a)
points_10b=[]
for ii in range(500,2000):
  a=params_hmc_10[ii][100000].cpu()
  points_10b.append(a)
del params_hmc_10
torch.cuda.empty_cache()

# Commented out IPython magic to ensure Python compatibility.

step_size = 0.001*30 # 0.0001 #0.001 #0.01 #0.15 #1 
# %time params_hmc_18 = hamiltorch.sample_model(net, xtrain1, ytrain1, params_init=params_init, model_loss='multi_class_log_softmax_output', num_samples=num_samples, burn = burn, step_size=step_size, num_steps_per_sample=L,tau_out=tau_out, tau_list=tau_list, normalizing_const=normalizing_const)

# %time pred_list, log_prob_list = hamiltorch.predict_model(net, x=x_val, y=y_val, samples=params_hmc_18, model_loss='multi_class_log_softmax_output', tau_out=1., tau_list=tau_list)
_, pred = torch.max(pred_list, 2)
acc18 = []
for i in range(pred.shape[0]):
    a = (pred[i].float() == y_val.flatten()).sum().float()/y_val.shape[0]
    acc18.append(a)   
points_18a=[]
for ii in range(500,2000):
  a=params_hmc_18[ii][5000].cpu()
  points_18a.append(a)
points_18b=[]
for ii in range(500,2000):
  a=params_hmc_18[ii][100000].cpu()
  points_18b.append(a)    
del params_hmc_18
torch.cuda.empty_cache()

plt.figure(figsize=[15,15]) 
plt.title('Exploration of parameters space',fontsize=30)   
plt.subplot(2,2,1)
plt.title('0.001',fontsize=15) 
plt.scatter(points_1a,points_1b)

plt.subplot(2,2,2)
plt.title('0.008',fontsize=15) 
plt.scatter(points_8a,points_8b)

plt.subplot(2,2,3)
plt.title('0.010',fontsize=15) 
plt.scatter(points_10a,points_10b)

plt.subplot(2,2,4)
plt.title('0.018',fontsize=15) 
plt.scatter(points_18a,points_18b)

plt.savefig('pareter_space_'+'.jpg')
######################
plt.figure(figsize=[15,20])
plt.title('Accuracy',fontsize=30)
plt.subplot(2,2,1)
plt.title('0.001',fontsize=15)
plt.plot(acc1)
plt.subplot(2,2,2)
plt.title('0.008',fontsize=15)
plt.plot(acc8)
plt.subplot(2,2,3)
plt.title('0.010',fontsize=15)
plt.plot(acc10)
plt.subplot(2,2,4)
plt.title('0.018',fontsize=15)
plt.plot(acc18)
plt.savefig('accuracy_'+'.jpg')
###############
plt.figure(figsize=[15,20])

import matplotlib.pyplot as plt

plt.subplot(2,2,1)
plt.title('0.001')
plt.hist(points_1b,30)
plt.subplot(2,2,2)
plt.title('0.008')
plt.hist(points_8b,30)
plt.subplot(2,2,3)
plt.title('0.010')
plt.hist(points_10b,30)
plt.subplot(2,2,4)
plt.title('0.018')
plt.hist(points_18b,30)
plt.savefig('hist_'+'.jpg')

import numpy as np

acc1=np.array(acc1)
acc8=np.array(acc8)
acc10=np.array(acc10)
acc18=np.array(acc18)
fig,axs = plt.subplots(2,2,constrained_layout=True,figsize=(25,15))

fig.suptitle('Accuracy',fontsize=60)

axs[0,0].plot(acc1)
axs[0,0].set_title('0.0001',fontsize=20)
axs[0,1].plot(acc8)
axs[0,1].set_title('0.005',fontsize=20)
axs[1,0].plot(acc10)
axs[1,0].set_title('0.009',fontsize=20)
axs[1,1].plot(acc18)
axs[1,1].set_title('0.03',fontsize=20)
plt.savefig('acc.jpg')
fig,axs = plt.subplots(2,2,constrained_layout=True,figsize=(15,15))
fig.suptitle('Exploration of parameters space',fontsize=60)
axs[0,0].scatter(points_1a,points_1b)
axs[0,0].set_title('0.0001',fontsize=20)
axs[0,1].scatter(points_8a,points_8b)
axs[0,1].set_title('0.005',fontsize=20)
axs[1,0].scatter(points_10a,points_10b)
axs[1,0].set_title('0.009',fontsize=20)
axs[1,1].scatter(points_18a,points_18b)
axs[1,1].set_title('0.03',fontsize=20)
plt.savefig('para.jpg')

fig,axs = plt.subplots(2,2,constrained_layout=True,figsize=(20,15))
fig.suptitle('Posteriors',fontsize=60)
axs[0,0].hist(points_1b,30)
axs[0,0].set_title('0.0001',fontsize=20)
axs[0,1].hist(points_8b,30)
axs[0,1].set_title('0.005',fontsize=20)

axs[1,0].hist(points_10b,30)
axs[1,0].set_title('0.009',fontsize=20)
axs[1,1].hist(points_18b,30)
axs[1,1].set_title('0.03',fontsize=20)
plt.savefig('post.jpg')

del params_hmc
torch.cuda.empty_cache()

tempo=625
s=0
sample=0
cnt=0
for i in range(15,2000):
  a = (pred[i].float() == y_test.flatten()).sum().float()/y_test.shape[0]
  if a>0.8: 
    s+=1
    if s>40:
      if cnt==0:
        sample=i
        cnt=1
  else:
    s=0


tempo08=tempo/2000*sample
tempo08

# Commented out IPython magic to ensure Python compatibility.
# 
# %%time 
# %memit params_hmc = hamiltorch.sample_model(net, x_train, y_train, params_init=params_init, model_loss='multi_class_log_softmax_output', num_samples=100, burn = burn, step_size=step_size, num_steps_per_sample=L,tau_out=tau_out, tau_list=tau_list, normalizing_const=normalizing_const)
# 
#

# Commented out IPython magic to ensure Python compatibility.

# %time pred_list, log_prob_list = hamiltorch.predict_model(net, x=x_test, y=y_test, samples=params_hmc, model_loss='multi_class_log_softmax_output', tau_out=1., tau_list=tau_list)
_, pred = torch.max(pred_list, 2)
acc = []
for i in range(pred.shape[0]):
    a = (pred[i].float() == y_val.flatten()).sum().float()/y_val.shape[0]
    acc.append(a)
print('\nExpected Accuracy: {:.2f}'.format((torch.max(pred_list[:].mean(0), 1)[1].float() == y_test.flatten()).sum().float()/y_test.shape[0]))
print('\nExpected validation log probability: {:.2f}'.format(torch.stack(log_prob_list).mean()))

fs = 20
plt.figure(figsize=(10,5))
plt.plot(acc)
plt.grid()
# plt.xlim(0,2000)
plt.xlabel('Iteration number',fontsize=fs)
plt.ylabel('Sample accuracy',fontsize=fs)
plt.tick_params(labelsize=15)
plt.savefig('acc.png')
plt.show()

plt.figure(figsize=(10,5))
plt.plot(log_prob_list)#[1400:1500])

import numpy as np
import tensorflow as tf
import keras

points=[]
for i in range(1000):
  a=p[0][i][0].cpu()
  points.append(a)

plt.hist(points)

points=[]
for i in range(500,2000):
  a=params_hmc[i][3].cpu()
  points.append(a)

plt.plot(points)
plt.plot()

points1=[]
for i in range(500,2000):
  a=params_hmc[i][50000].cpu()
  points1.append(a)
plt.figure(figsize=[11,11])
plt.scatter(points,points1)

_, pred = torch.max(pred_list, 2)

torch.mean(torch.tensor(acc))

y_train

"""### Mean estimator"""

import numpy as np
import tensorflow as tf

x_train.size()
m=0
n=0
for i in range(100):
  a=np.matrix(x_train[i,0,:,:].cpu())
  b=np.matrix(x_train[i,1,:,:].cpu())
  m+=a.mean()
  n+=b.mean()
san=m/100

x_train.size()
m=0
n=0
for i in range(100):
  a=np.matrix(x_train[100+i,0,:,:].cpu())
  b=np.matrix(x_train[100+i,1,:,:].cpu())
  m+=a.mean()
  n+=b.mean()
mal=m/100

soglia=(san+mal)/2
s=0
pred=np.zeros_like(y_test.cpu())
for i in range(len(y_test)):
  a=np.matrix(x_test[i,0,:,:].cpu())
  val=a.mean()
  if val>=soglia:
    pred[i]=1.
  if pred[i]==float(y_test[i].cpu()):
    s+=1
pred.mean()
s/len(y_test)

