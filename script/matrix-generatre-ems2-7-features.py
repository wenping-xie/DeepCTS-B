import os  # 导入与操作系统交互的库
import numpy as np  # 导入用于数值计算的库
import pandas as pd  # 导入用于数据处理的库
import argparse  # 用于命令行参数解析
import random  # 导入用于随机数生成的库
import multiprocessing
import torch  # PyTorch深度学习库
import esm  # 导入ESM模块（蛋白质语言模型）

# 创建命令行参数解析器
parser = argparse.ArgumentParser()

# 添加解析的参数，--seq_dir指定序列的目录，--type指定模式（predict、training或testing），--dir指定输出目录，--thread指定线程数，--subtype指定亚型
parser.add_argument('--seq_dir', required=True)
parser.add_argument('--type', required=True, metavar='predict or training or testing')
parser.add_argument('--dir', required=True, metavar='file')
parser.add_argument('--thread', required=True)
parser.add_argument('--subtype', required=True)
args = parser.parse_args()  # 解析传入的命令行参数

# 提取ESM嵌入特征函数
def extract_esm(filename, subtype):
    # ESM嵌入文件路径
    EMB_PATH = '/home/xie_wenping/influenza_B/antigenic_transformer/BV/1-matrix-generate/esm2' + '/esm_seq'
    EMB_LAYER = 6  # 指定第6层的表示作为嵌入特征
    fn = EMB_PATH + '/' + filename + '.pt'  # 加载.pt文件
    embs = torch.load(fn)  # 加载嵌入文件
    Xs = (embs['representations'][EMB_LAYER])  # 获取指定层的表示
    Xs = Xs.numpy()  # 转换为NumPy数组
    return Xs  # 返回嵌入特征

# 定义将氨基酸序列转换为数值表示的类
class str_to_num():
    def __init__(self):
        self.seq1 = []  # 保存序列1
        self.seq2 = []  # 保存序列2
        self.name1 = []  # 保存序列1的名称
        self.name2 = []  # 保存序列2的名称
        self.label = []
        self.all_data = []  # 保存所有数据

    # 从CSV读取数据
    def read_from_csv(self, csv_data, type='predict'):
        print("starting read data....")
        self.seq1 = csv_data['seq_1']  # 从CSV获取序列1
        self.seq2 = csv_data['seq_2']  # 从CSV获取序列2
        self.name1 = csv_data['new_name_1']  # 获取名称1
        self.name2 = csv_data['new_name_2']  # 获取名称2
        if type == 'predict':
            pass  # 如果是预测模式，不需要标签
        else:
            self.label = csv_data['label']  # 获取标签
            assert (len(self.seq1) == len(self.label))  # 确保序列和标签数量相同
        assert (len(self.seq1) == len(self.seq2))  # 确保两个序列数量一致
        print("read data done")
        
    def generate_seq_test(self, seq1, seq2, name1, name2, matchfile, subtype):
        # 读取信息文件，包含序列的映射信息
        info = pd.read_csv('/home/xie_wenping/influenza_B/antigenic_transformer/BV/1-matrix-generate/esm2-and-7-features' + '/' + subtype + '_HA1_forhi-v1.csv')
        # 定义氨基酸字母表和一些特定氨基酸组
        lista = ['A', 'R', 'N', 'D', 'C', 'Q', 'E', 'G', 'H', 'I', 'L', 'K', 'M', 'F', 'P', 'S', 'T', 'W', 'Y', 'V']
        listb = ['D', 'N']
        listz = ['E', 'Q']
        listj = ['L', 'I']
        
        strains = []
        one_char_1 = np.zeros((len(seq1), len(seq1[0]),7))
        one_char_2 = np.zeros((len(seq2), len(seq2[0]),7))
        for i in range(len(seq1)):  # 遍历每个序列对

            for j in range(len(seq1[i])):  # 遍历每个氨基酸位置
                seq1_aa = seq1[i][j]  # 获取序列1的氨基酸
                seq2_aa = seq2[i][j]  # 获取序列2的氨基酸
                # 对特殊氨基酸字符进行随机替换
                if seq1[i][j] == 'X':
                    seq1_aa = random.choice(lista)
                elif seq1[i][j] == 'B':
                    seq1_aa = random.choice(listb)
                elif seq1[i][j] == 'Z':
                    seq1_aa = random.choice(listz)
                elif seq1[i][j] == 'J':
                    seq1_aa = random.choice(listj)
                if seq2[i][j] == 'X':
                    seq2_aa = random.choice(lista)
                elif seq2[i][j] == 'B':
                    seq2_aa = random.choice(listb)
                elif seq2[i][j] == 'Z':
                    seq2_aa = random.choice(listz)
                elif seq2[i][j] == 'J':
                    seq2_aa = random.choice(listj)
                    
                one_char_1[i][j][0] = aj_dic[seq1_aa]['number']
                one_char_1[i][j][1] = aj_dic[seq1_aa]['access']
                one_char_1[i][j][2] = aj_dic[seq1_aa]['charge']
                one_char_1[i][j][3] = aj_dic[seq1_aa]['hydro']
                one_char_1[i][j][4] = aj_dic[seq1_aa]['hyindex']
                one_char_1[i][j][5] = aj_dic[seq1_aa]['polar']
                one_char_1[i][j][6] = aj_dic[seq1_aa]['volume']
                
                one_char_2[i][j][0] = aj_dic[seq2_aa]['number']
                one_char_2[i][j][1] = aj_dic[seq2_aa]['access']
                one_char_2[i][j][2] = aj_dic[seq2_aa]['charge']
                one_char_2[i][j][3] = aj_dic[seq2_aa]['hydro']
                one_char_2[i][j][4] = aj_dic[seq2_aa]['hyindex']
                one_char_2[i][j][5] = aj_dic[seq2_aa]['polar']
                one_char_2[i][j][6] = aj_dic[seq2_aa]['volume']
                


            # 提取序列对应的ESM嵌入
            ar1 = extract_esm(info['seqid'][info['Isolate_Id'] == name1[i]].iloc[0], subtype)
            ar2 = extract_esm(info['seqid'][info['Isolate_Id'] == name2[i]].iloc[0], subtype)
            # 将两条序列及其ESM嵌入连接起来
            strain = np.concatenate((ar1, one_char_1[i], ar2, one_char_2[i]), axis=1)
            strains.append(strain)
        mychar = np.array(strains).astype(np.float64)  # 将生成的特征序列转换为NumPy数组
        return mychar  # 返回特征数组

    def generate_seq(self, seq1, seq2, name1, name2, aj_dic, subtype, label):
        print('begin')
        info = pd.read_csv('/home/xie_wenping/influenza_B/antigenic_transformer/BV/1-matrix-generate/esm2-and-7-features' + '/' + subtype + '_HA1_forhi-v1.csv')
        lista = ['A', 'R', 'N', 'D', 'C', 'Q', 'E', 'G', 'H', 'I', 'L', 'K', 'M', 'F', 'P', 'S', 'T', 'W', 'Y', 'V']
        listb = ['D', 'N']
        listz = ['E', 'Q']
        listj = ['L', 'I']

        strains = []
        one_char_1 = np.zeros((len(seq1), len(seq1[0]),7))
        one_char_2 = np.zeros((len(seq2), len(seq2[0]),7))

        for i in range(len(seq1)):
            strain1 = []
            strain2 = []
            labels = []
            for j in range(len(seq1[i])):
                seq1_aa = seq1[i][j]
                seq2_aa = seq2[i][j]

                if seq1[i][j] == 'X':
                    seq1_aa = random.choice(lista)
                elif seq1[i][j] == 'B':
                    seq1_aa = random.choice(listb)
                elif seq1[i][j] == 'Z':
                     seq1_aa = random.choice(listz)
                elif seq1[i][j] == 'J':
                     seq1_aa = random.choice(listj)
                else:
                    pass
                if seq2[i][j] == 'X':
                   seq2_aa = random.choice(lista)
                elif seq2[i][j] == 'B':
                     seq2_aa = random.choice(listb)
                elif seq2[i][j] == 'Z':
                     seq2_aa = random.choice(listz)
                elif seq2[i][j] == 'J':
                     seq2_aa = random.choice(listj)
                else:
                    pass
            #strain1.append(matchfile[seq1_aa].tolist())
            #strain2.append(matchfile[seq2_aa].tolist())

            # 填充one_char数组
                one_char_1[i][j][0] = aj_dic[seq1_aa]['number']
                one_char_1[i][j][1] = aj_dic[seq1_aa]['access']
                one_char_1[i][j][2] = aj_dic[seq1_aa]['charge']
                one_char_1[i][j][3] = aj_dic[seq1_aa]['hydro']
                one_char_1[i][j][4] = aj_dic[seq1_aa]['hyindex']
                one_char_1[i][j][5] = aj_dic[seq1_aa]['polar']
                one_char_1[i][j][6] = aj_dic[seq1_aa]['volume']
                
                one_char_2[i][j][0] = aj_dic[seq2_aa]['number']
                one_char_2[i][j][1] = aj_dic[seq2_aa]['access']
                one_char_2[i][j][2] = aj_dic[seq2_aa]['charge']
                one_char_2[i][j][3] = aj_dic[seq2_aa]['hydro']
                one_char_2[i][j][4] = aj_dic[seq2_aa]['hyindex']
                one_char_2[i][j][5] = aj_dic[seq2_aa]['polar']
                one_char_2[i][j][6] = aj_dic[seq2_aa]['volume']
                
                #strain1.append(matchfile[seq1_aa].tolist())  # 匹配并转换序列1的氨基酸
                #strain2.append(matchfile[seq2_aa].tolist())  # 匹配并转换序列2的氨基酸
                labels.append([label[i]])
                
            ar1 = extract_esm(info['seqid'][info['Isolate_Id'] == name1[i]].iloc[0], subtype)
            ar2 = extract_esm(info['seqid'][info['Isolate_Id'] == name2[i]].iloc[0], subtype)
            print(info['seqid'][info['Isolate_Id'] == name1[i]].iloc[0])
            print(ar1.shape)
            # 确保 labels 的形状正确
            #labels = np.array(labels).reshape(-1, 1)  # 转换为列向量

            # 将 labels 重复以匹配其他数组的行数
            #labels = np.tile(labels, (one_char_1[i].shape[0], 1))
            # 拼接
            strain = np.concatenate((ar1, one_char_1[i], ar2, one_char_2[i], labels), axis=1)
            # 合并特征，最终输出654维
            #strain = np.concatenate((ar1,one_char_1[i],ar2,one_char_2[i], labels),axis=1) #strain1, strain2), axis=1)
            strains.append(strain)

        mychar = np.array(strains).astype(np.float64)
        return mychar
    
    # 根据type生成特征
    def do_generate(self, type, matchfile, subtype):
        print('start generating seq....')
        if type == 'predict':
            self.all_data = self.generate_seq_test(self.seq1, self.seq2, self.name1, self.name2, matchfile, subtype)
        else:
            self.all_data = self.generate_seq(self.seq1, self.seq2, self.name1, self.name2, matchfile, subtype, self.label)
        print('generate seq done')

    # 保存生成的特征数据为.npy格式
    def save_to_npy(self, dir, filename):
        arr = np.array(self.all_data)  # 转换为NumPy数组
        np.save(dir + '/' + filename + '.npy', arr)  # 保存为.npy文件


    
    
    
# 用于生成矩阵特征的函数
def matrix_generate(record):
    seq_file, aj_dic, dir, type, filename, matchfile, subtype = record
    seq_all_0 = pd.read_csv(seq_file, sep=',')#, index_col=0)  # 读取序列文件
    seq_all = seq_all_0.reset_index(drop=True)  # 重置索引
    s = str_to_num()  # 创建str_to_num对象
    s.read_from_csv(seq_all, type)  # 读取CSV数据
    s.do_generate(type, aj_dic, subtype)  # 生成特征
    s.save_to_npy(dir, filename)  # 保存生成的特征为.npy文件
    print('done')


if __name__ == '__main__':
    import time  # 用于记录运行时间
    start_time = time.time()  # 记录开始时间

    # 读取aaindex文件（氨基酸索引特征文件）
    aaindex=pd.read_csv("/home/xie_wenping/influenza_B/predict/BY/train_validate/aaindex_feature_BY.txt",sep='\t',index_col=0)
    #aaindex = pd.read_csv('/home/xie_wenping/predac-CNN/predacCNN_allcode/predacCNN_allcode/PREDAV-CNN-main/aaindex_feature_H1N1.txt', sep='\t', index_col=0)
    aaindex1 = aaindex[['number']]  # 只保留'number'列

    matchfile = aaindex1.T  # 转置文件，方便后续查找
    dir = args.dir  # 输出目录
    seq_dir = args.seq_dir  # 序列文件所在目录
    all_dict = aaindex.T.to_dict()  # 转换为字典形式
    aj_dic = all_dict  # 赋值给aj_dic
    type = args.type  # 获取type参数
    subtype = args.subtype  # 获取subtype参数
    thread = int(args.thread)  # 获取线程数

    # 获取序列目录中的文件列表
    seq_file_list = os.listdir(seq_dir)
    print(seq_file_list)

    # 多进程处理序列文件
    for seqfile in seq_file_list:
        filelist = [seqfile]  # 将单个文件放入列表
        pool = multiprocessing.Pool(processes=thread)  # 创建进程池
        for i in filelist:  # 遍历文件列表
            map_args = (seq_dir + '/' + i, aj_dic, dir, type, i,matchfile, subtype)  # 构建参数
            pool.apply_async(matrix_generate, (map_args,))  # 异步调用matrix_generate函数
        pool.close()  # 关闭进程池
        pool.join()  # 等待所有进程完成
    # matrix_generate(map_args)  # 如果不用多进程，可以直接调用

    print("time is %s" % (time.time() - start_time))  # 输出程序运行时间
###多线程代码的修改，如下：：：
#for seqfile in seq_file_list:
#    filelist=[seqfile]  
#    for i in filelist:#seg file list:
#         seq_file, aj_dic, dir, type, filename, matchfile, subtype =seq_dir+'/'+i,aj_dic,dir,type,i,matchfile,subtype
#         seq_all_0 = pd.read_csv(seq_file, sep='\t')#,index_col=0)  # 读取序列文件
#         seq_all = seq_all_0.reset_index(drop=True)  # 重置索引
#         s = str_to_num()  # 创建str_to_num对象
#         s.read_from_csv(seq_all, type)  # 读取CSV数据
#         s.do_generate(type, aj_dic, subtype)  # 生成特征
#         s.save_to_npy(dir, filename)  # 保存生成的特征为.npy文件
#         print('done')
 	
