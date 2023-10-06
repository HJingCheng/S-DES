# SDES加密算法

## 简介

本项目实现了SDES(简化数据加密标准)对称密钥块加密算法，并提供一个图形用户界面。

## 功能

- 支持SDES算法的加解密
- 提供图形用户界面进行交互
- 支持对ASCII字符串进行加解密
- 实现暴力破解给定的明密文对
- 分析明密文对是否存在多个可行密钥

## 算法详情

SDES算法规范如下:

- 加密方程: $C = IP^{-1}(f_{k2}(SW(f_{k1}(IP(P)))))$

- 解密方程: $P = IP^{-1}(f_{k1}(SW(f_{k2}(IP(C)))))$

- 密钥生成: $ki = P8(Shifti(P10(K))), i=1,2$

- 各置换盒和S盒详见`SDES.py`文件

## 开始使用

### 依赖

- Flask
- Bootstrap

### 安装

```bash
pip install -r requirements.txt
```

### 使用

``` bash
python app.py
```

图形界面将启动，可通过 http://localhost:5000 访问

具体使用请参考`UserGuide.pdf`

进一步开发，请参考`DevelopmentManual.pdf`

## 项目结构

    .
    ├── app.py       # Flask应用启动脚本
    ├── templates   
    │   └── index.html # 前端页面
    ├── static
    │   ├── css   
    │   ├── js
    ├── SDES.py      # SDES算法实现
    ├── README.md    
    ├── requirements.txt   # 项目所需库
    ├── 接口文档.pdf   # 用户指南
    ├── 用户指南.pdf   # 开发手册
