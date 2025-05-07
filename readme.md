# YaTC

本代码库包含以下论文的实现代码：
<br>
***Yet Another Traffic Classifier: A Masked Autoencoder Based Traffic Transformer with Multi-Level Flow Representation***
<br>
发表于第三十七届 AAAI 人工智能会议 (AAAI 2023)。

## 概述

<img src="YaTC.png">

YaTC 的训练策略分为两个阶段：预训练阶段和微调阶段。

## 预训练模型

```
路径：./output_dir/pretrained-model.pth
```

预训练模型[下载链接](https://drive.google.com/file/d/1wWmZN87NgwujSd2-o5nm3HaQUIzWlv16/view?usp=drive_link)

## 数据集信息

```
路径：./data
```
数据集[下载链接](https://drive.google.com/file/d/1znKQpZ704Bh4EkaHUBJwztYgflFXPnHI/view?usp=sharing)

### 类别数量

- ISCXVPN2016_MFR：7类
- ISCXTor2016_MFR：8类
- USTC-TFC2016_MFR：20类
- CICIoT2022_MFR：10类

## 环境依赖
```shell
conda create -n yatc python=3.9
conda activate yatc
conda install pytorch torchvision torchaudio pytorch-cuda=11.8 -c pytorch -c nvidia
pip install tensorboard==2.19.0 timm==1.0.15 scikit-image==0.18.1 numpy==1.24.4 scikit-learn==0.24.2

python -c "import torch; print(torch.__version__)"
```

## 代码说明

- data_process.py：将流量 pcap 文件处理为 MFR 矩阵
- models_YaTC：分类器模型的代码
- pre-train.py：预训练阶段的代码
- fine-tune.py：微调阶段的代码

## 预训练

```
python pre-train.py --batch_size 128 --blr 1e-3 --steps 150000 --mask_ratio 0.9
```

## 微调

```
python fine-tune.py --blr 2e-3 --epochs 200 --data_path ./YaTC_datasets/ISCXVPN2016_MFR --nb_classes 7
```

## 联系方式

实验室链接：[SJTU-NSSL](https://github.com/NSSL-SJTU "SJTU-NSSL")

[赵瑞杰](https://github.com/iZRJ)
<br>
邮箱：ruijiezhao@sjtu.edu.cn

[詹明伟](https://github.com/zmw1216)
<br>
邮箱：mw.zhan@sjtu.edu.cn

## 引用

R. Zhao, M. Zhan, X. Deng, Y. Wang, Y. Wang, G. Gui, and Z. Xue, ``Yet Another Traffic Classifier: A Masked Autoencoder Based Traffic Transformer with Multi-Level Flow Representation,'' in AAAI Conference on Artificial Intelligence (AAAI'23), Washington, United States, Feb. 7--14, 2023, pp. 1--8.
