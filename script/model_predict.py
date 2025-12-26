import tensorflow.compat.v1 as tf
tf.compat.v1.disable_eager_execution( )#add
import numpy as np
import pandas as pd#add
import os
import glob
import argparse
from sklearn.utils import class_weight
import time
import pandas
from sklearn.metrics import matthews_corrcoef,f1_score
from sklearn.metrics import confusion_matrix
from tensorflow.keras.utils import to_categorical#加
#import tensorflow_addons as tfa#加
#import matplotlib.pyplot as plt
#from sklearn.metrics import recall_score,balanced_accuracy_score 
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"#加
import os 
os.environ["CUDA_VISIBLE_DEVICES"] = "0"#指定在第0块GPU上跑
#Encoder of TransSSVs
from sklearn import model_selection
import numpy as np
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.metrics import roc_curve, auc, roc_auc_score
import numpy as np
#import matplotlib.pyplot as plt
import collections
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import os,argparse
def early_stopping(info,monitor,patience):
    df = info
    df['epoch']=df.index+1
    max_PRC_dev = 0.0  
    last_improve = -1  


    for epoch, PRC_dev in df[['epoch', monitor]].itertuples(index=False):
        if PRC_dev > max_PRC_dev:
            last_improve = epoch
            max_PRC_dev = PRC_dev  

        if epoch - last_improve >= patience:
            break
    return last_improve
def plot_attention(filename,dflabel,dfpredict,label,outdir_0,fold):
    data=pd.DataFrame()
    data['real']=list(dflabel)
    data['predict']=list(dfpredict)
    data['label']=0
    data.loc[data['real'] == data['predict'], 'label'] = 1
    print(data['label'].value_counts())
    if label == 'all':
        length_index = np.array(data.index)
    elif label == '1':
        length_index = np.array(data[data.label == 1].index)
    elif label == '0':
        length_index = np.array(data[data.label == 0].index)
    testa=filename#np.load(filename)
    print(testa.shape)
    testa=testa[length_index,:,:,:]
    print(testa.shape)
    testn=testa.sum(axis=(0,1,2))
    testnn=testa.sum(axis=(0,1))
    print(testn.shape)
    N = len(testn)
    index = range(1,N+1)
    width = 0.35

    df=''
    df=pd.DataFrame(testn)
    df['position']=''
    df['position']=list(index)
    df.to_csv(outdir_0+'/'+str(fold)+'attention_bar_label_'+str(label)+'.csv')


    p2 = plt.bar(index, testn, width, label="rainfall", color="#87CEFA")
    plt.savefig(outdir_0+'/'+str(fold)+'attention_bar_label_'+str(label)+'.jpg', dpi = 300)
    plt.ylabel('Attention score')
    plt.xlabel('Position')
    plt.clf()
    #plt.show()

    sns.heatmap(testnn, cmap = 'YlGn',cbar = True, square = True)
    plt.xlabel('Position')
    plt.savefig(outdir_0+'/'+str(fold)+'attention_map_label_'+str(label)+'.jpg', bbox_inches = 'tight', dpi = 300)
    plt.clf()
    #plt.show()
    
class Encoder(tf.keras.layers.Layer):
  def __init__(self, num_layers, d_model, num_heads, dff, rate=0.5):
    super(Encoder, self).__init__()
    self.d_model = d_model
    self.num_layers = num_layers    
    self.pos_encoding = positional_encoding(1000, self.d_model)# 
    self.enc_layers = [EncoderLayer(d_model, num_heads, dff, rate) for _ in range(num_layers)]
    self.dropout = tf.keras.layers.Dropout(rate)
        
  def call(self, x, training=True, mask=None):
    seq_len = tf.shape(x)[1]
    x += self.pos_encoding[:, :seq_len, :]
    x = self.dropout(x, training=training)
    enc_self_attns=[]
    for i in range(self.num_layers):
      x,attn_weights = self.enc_layers[i](x, training, mask)
      enc_self_attns.append(attn_weights)
    return x ,enc_self_attns#



def get_angles(pos, i, d_model):
  angle_rates = 1 / np.power(10000, (2 * (i//2)) / np.float32(d_model))
  return pos * angle_rates

def positional_encoding(position, d_model):
  angle_rads = get_angles(np.arange(position)[:, np.newaxis],np.arange(d_model)[np.newaxis, :],d_model)
  angle_rads[:, 0::2] = np.sin(angle_rads[:, 0::2])
  angle_rads[:, 1::2] = np.cos(angle_rads[:, 1::2])
  pos_encoding = angle_rads[np.newaxis, ...]
  return tf.cast(pos_encoding, dtype=tf.float32)

class EncoderLayer(tf.keras.layers.Layer):
  def __init__(self, d_model, num_heads, dff, rate=0.5):
    super(EncoderLayer, self).__init__()
    self.mha = MultiHeadAttention(d_model, num_heads)
    self.ffn = point_wise_feed_forward_network(d_model, dff)
    self.layernorm1 = tf.keras.layers.LayerNormalization(epsilon=1e-6)
    self.layernorm2 = tf.keras.layers.LayerNormalization(epsilon=1e-6) 
    self.dropout1 = tf.keras.layers.Dropout(rate)
    self.dropout2 = tf.keras.layers.Dropout(rate)
    
  def call(self, x, training=True, mask=None):
    attn_output, attn_weights = self.mha(x, x, x, mask)  
    attn_output = self.dropout1(attn_output, training=training)
    out1 = self.layernorm1(x + attn_output)  
    ffn_output = self.ffn(out1) 
    ffn_output = self.dropout2(ffn_output, training=training)
    out2 = self.layernorm2(out1 + ffn_output)  
    return out2,attn_weights

def point_wise_feed_forward_network(d_model, dff):
  return tf.keras.Sequential([
      tf.keras.layers.Dense(dff, activation='relu'),  
      tf.keras.layers.Dense(d_model)  
  ])


#multi-head attention
class MultiHeadAttention(tf.keras.layers.Layer):
  def __init__(self, d_model, num_heads):
    super(MultiHeadAttention, self).__init__()
    self.num_heads = num_heads
    self.d_model = d_model
    assert d_model % self.num_heads == 0
    self.depth = d_model // self.num_heads
    self.wq = tf.keras.layers.Dense(d_model)
    self.wk = tf.keras.layers.Dense(d_model)
    self.wv = tf.keras.layers.Dense(d_model)
    self.dense = tf.keras.layers.Dense(d_model)
        
  def split_heads(self, x, batch_size):
    x = tf.reshape(x, (batch_size, -1, self.num_heads, self.depth))
    return tf.transpose(x, perm=[0, 2, 1, 3])
    
  def call(self, v, k, q, mask=None):
    batch_size = tf.shape(q)[0]
    q = self.wq(q)  
    k = self.wk(k)  
    v = self.wv(v) 
    
    q = self.split_heads(q, batch_size) 
    k = self.split_heads(k, batch_size)  
    v = self.split_heads(v, batch_size)  
    
    scaled_attention, attention_weights = scaled_dot_product_attention(q, k, v, mask)
    scaled_attention = tf.transpose(scaled_attention, perm=[0, 2, 1, 3])  
    concat_attention = tf.reshape(scaled_attention, (batch_size, -1, self.d_model))  
    output = self.dense(concat_attention)  
    return output, attention_weights

def scaled_dot_product_attention(q, k, v, mask=None):
  matmul_qk = tf.matmul(q, k, transpose_b=True)  
  dk = tf.cast(tf.shape(k)[-1], tf.float32)
  scaled_attention_logits = matmul_qk / tf.math.sqrt(dk)
  if mask is not None:
    scaled_attention_logits += (mask * -1e9)  
  attention_weights = tf.nn.softmax(scaled_attention_logits, axis=-1)  
  output = tf.matmul(attention_weights, v)  
  return output, attention_weights


def binary_focal_loss(gamma=2, alpha=0.25):
    alpha = tf.constant(alpha, dtype=tf.float32)
    gamma = tf.constant(gamma, dtype=tf.float32)
    def binary_focal_loss_fixed(y_true, y_pred):
        y_true = tf.cast(y_true, tf.float32)
        alpha_t = y_true*alpha + (tf.ones_like(y_true)-y_true)*(1-alpha)
        p_t = y_true*y_pred + (tf.ones_like(y_true)-y_true)*(tf.ones_like(y_true)-y_pred) + tf.keras.backend.epsilon()
        focal_loss = - alpha_t * tf.pow((tf.ones_like(y_true)-p_t),gamma) * tf.math.log(p_t)
        return tf.reduce_mean(focal_loss)
    return binary_focal_loss_fixed

from keras import backend as K

def recall_m(y_true, y_pred):
    true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
    possible_positives = K.sum(K.round(K.clip(y_true, 0, 1)))
    recall = true_positives / (possible_positives + K.epsilon())
    return recall

def precision_m(y_true, y_pred):
    true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
    predicted_positives = K.sum(K.round(K.clip(y_pred, 0, 1)))
    precision = true_positives / (predicted_positives + K.epsilon())
    return precision

def f1_m(y_true, y_pred):
    precision = precision_m(y_true, y_pred)
    recall = recall_m(y_true, y_pred)
    return 2*((precision*recall)/(precision+recall+K.epsilon()))

def get_confusion_matrix(y_true, y_pred):
    TP, FP, TN, FN = 0, 0, 0, 0
    for i in range(y_pred.shape[0]):
        if y_pred[i,1] >= 0.5:
            y_pred[i,1]=1
            y_pred[i,0]=0
        else:
            y_pred[i,1]=0
            y_pred[i,0]=1

    TP=sum(y_true[:,1] * y_pred[:,1])
    TN=sum(y_true[:,0] * y_pred[:,0])
    FP=sum(y_true[:,0] * y_pred[:,1])
    FN=sum(y_true[:,1] * y_pred[:,0])

    return TP, FP, TN, FN

def get_TransSSVs_model(shape_0,shape_1):
    inputESM=tf.keras.layers.Input(shape=(shape_0,shape_1)) #shape=(329,14)

    sequence=tf.keras.layers.Dense(16)(inputESM)
    #sequence=tf.keras.layers.Dense(16)(sequence)
    sequence=tf.keras.layers.Dense(8)(sequence)
    sequence,enc_self_attns  = Encoder(2, 8, 2, 32, rate=0.1)(sequence)
    sequence=tf.keras.layers.Flatten(input_shape=(shape_0,32))(sequence)
    feature=tf.keras.layers.Dense(512,activation='relu')(sequence)
    feature=tf.keras.layers.Dense(256,activation='relu')(feature)
    feature=tf.keras.layers.Dense(128,activation='relu')(feature)
    feature=tf.keras.layers.Dropout(0.1)(feature)#0.1
    #y=tf.keras.layers.Dense(1,activation='sigmoid')(feature)
    y=tf.keras.layers.Dense(2, activation='softmax')(feature)
    TransSSVs_model=tf.keras.models.Model(inputs=inputESM,outputs=[y,enc_self_attns])#change4
    adam=tf.keras.optimizers.Adam(learning_rate=1e-3, beta_1=0.9, beta_2=0.999, epsilon=1e-08,clipnorm=1.0,clipvalue=0.5,decay=1e-8)
    #TransSSVs_model.compile(loss=[binary_focal_loss(alpha=0.25, gamma=2)],optimizer=adam,metrics=['accuracy',f1_m])
    #TransSSVs_model.compile(loss='binary_crossentropy',optimizer=adam,metrics=['accuracy',f1_m])
    TransSSVs_model.compile(loss='categorical_crossentropy',optimizer=adam,metrics=['accuracy',f1_m])
    #model.compile(loss='binary_crossentropy', optimizer='adam')
    #https://cloud.tencent.com/developer/article/1773836   
    TransSSVs_model.summary()
    return TransSSVs_model



if __name__ == "__main__":
    # setting the hyper parameters
    import argparse

    parser = argparse.ArgumentParser(description='train',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--indicator',default='training', metavar='training or fine_tune')
    parser.add_argument('--batch_size', default=128, type=int)
    parser.add_argument('--model_dir', default=None)
    parser.add_argument('--save_dir', default='results')
    parser.add_argument('--shape_0',default=15,type=int)
    parser.add_argument('--shape_1',default=52,type=int)
    parser.add_argument('--input_dir', required=True)
    parser.add_argument('--filename', required=True)
    parser.add_argument('--epoch', default=50,required=False,type=int)
    parser.add_argument('--outdir',default=None)
    parser.add_argument('--fold',type=int)
    #parser.add_argument('--encoder_layer',default=2,type=int)
    parser.add_argument('--number_columns', default=14,required=True,type=int)
    args = parser.parse_args()
    print(args)

    # load dataset

    filename=args.filename

    number_columns=args.number_columns

    model_dir=args.model_dir
    outdir_0=args.outdir
    fold=args.fold

    seed=100
    data=np.load(args.input_dir+'/'+filename)

    train_and_test, valid = model_selection.train_test_split(data, test_size=0.1, random_state=seed, stratify=data[:, 0, number_columns])
    sss = StratifiedShuffleSplit(n_splits=5, test_size=1/8, random_state=seed)
    y = train_and_test[:, 0, number_columns]
    test_data=valid
    print(test_data.shape)
    #print(test_index)



    test_x=test_data[:,:,:number_columns]
    test_y_0=test_data[:,0,number_columns]

    test_y=np.zeros((test_x.shape[0],2))


    for i in range(test_x.shape[0]):
        test_y[i,0]=1-test_y_0[i]
        test_y[i,1]=test_y_0[i]



    TransSSVs_model=get_TransSSVs_model(args.shape_0,args.shape_1)

    

    
    info=pd.read_csv(model_dir+'/'+str(fold)+'/results/log.csv',index_col=0)
    info['epoch']=info.index+1
    dfmax=info#s.iloc[:100]#add
    dfmax=dfmax[dfmax['epoch']==early_stopping(dfmax,'AUC',patience=30)].index[0]#
    if len(str(dfmax))==1:
        dfmax='0'+str(dfmax)

    model_path=model_dir+'/'+str(fold)+'/results/model_'+str(dfmax)
    print(model_path)
    TransSSVs_model.load_weights(model_path)

    print(TransSSVs_model.predict(test_x))
    pred_y,enc_self_attns1=TransSSVs_model.predict(test_x)#
    print(fold)
    print(pred_y[:,0])
    print(pred_y[:,1])

    

    pred_y_0=pred_y[:,1]
    print(pred_y_0)  
    pred_y_0_np=np.array(pred_y_0)
    #print(pred_y_0_np)  
    true_y_np=np.array(test_y_0)
    all_np=np.array(list(zip(true_y_np,pred_y_0_np)))
    np.save(outdir_0+'/'+str(fold)+'_pred.npy',all_np)
    Y_Pred=pred_y
    Y_Pred_new=[]
    for value in Y_Pred[:,1]:
        if value<0.5:
            Y_Pred_new.append(0)
        else:
            Y_Pred_new.append(1)
    Y_Pred_new=np.array(Y_Pred_new)
    np.save(outdir_0+'/'+str(fold)+'_attention_label.npy', Y_Pred_new)#add

    idx_layer=1
    for enc_self_attns in [enc_self_attns1]:#,enc_self_attns2]:  
        print(enc_self_attns.shape)
        if not os.path.exists(outdir_0+'/layer'+str(idx_layer)):
            os.makedirs(outdir_0+'/layer'+str(idx_layer))
        np.save(outdir_0+'/layer'+str(idx_layer)+'/'+str(fold)+'_attention_weight.npy', enc_self_attns)#add args.save_dir +'/'+
        print(test_y_0)
        print(Y_Pred_new)#check
        plot_attention(enc_self_attns,test_y_0,Y_Pred_new,'1',outdir_0+'/layer'+str(idx_layer),fold)  
        idx_layer=idx_layer+1
    
    TP, FP, TN, FN=get_confusion_matrix(test_y, pred_y)

    print(get_confusion_matrix(test_y, pred_y))
    ps_dict={}
    ps_dict={'TP':TP,'FP':FP,'TN':TN,'FN':FN}
    ps=pd.DataFrame.from_dict(ps_dict,orient='index').T
    ps['fold']=fold

    ps['AUC']=roc_auc_score(all_np[:,0], all_np[:,1])
    ps.to_csv(outdir_0+'/'+'5fold_prediction_log.csv',mode='a+',index=False)
    
 
 
