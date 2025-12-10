# 12.01-12.07 周报

    Author: 彭日骏
    Edit Time: 2025/12/01-2025/12/07

---
## Plan

- [x] 再吃一下剩下ResNet paper阅读 [ResNet]'https://arxiv.org/abs/1512.03385'

---
## Note

首先作者提出ResNet想要解决的问题的背景 **Degradation Problem** ：

1. 通过两张图展现了 depth 造成的 error 增加并非是 overfitting 带来的
2. 经典问题：depth 到底对模型而言是不是正增长呢？这个问题的探索一直被梯度爆炸无法收敛而阻拦。而作者认为深层的梯度爆炸的问题其实很大程度上已通过归一化初始化[normalized initialization]和中间归一化层[intermediate normalization layers--??]得到解决
3. 提出 residual net ，本质上如果一个解已经是几乎最优的了，更深层的时候我们应该做 identity mapping ，然而 relu(F(x)) 作为一个非线性的函数，在更深层进行拟合的时候，很难学习到 identity mapping 这个 linear 的映射。
4. 因此，用 residual net ，令 $H(\mathbf{x}) = F(\mathbf{x}) + \mathbf{x}, F(\mathbf{x}) = H(\mathbf{x}) - \mathbf{x}$，如果 identity mapping 已经是 optimal 的，那一堆 nonlinear layers 可以更好的学习到这一点，因为只需要把 $F(\mathbf{x})$ 往 0 mapping 去靠即可
5. 讨论发现， identity mapping 引入的一个x，不会影响SGD算法的梯度下降，并且没有额外引入更多的 parameters/computational complexity ，如果出现了维度变化可以：直接padding 0，做线性映射（事实上后面讨论出来是没有必要的）
6. 这样的模型在 ImageNet 跑完后发现，吃到了 depth 带来的优势，更深的模型成功学到了更多的特征，让其带来了明显的 accuracy-depth 收益
7. 然后接下来就在 CIFAR-10 dataset 上训练进行训练，已知 CIFAR-10 dataset[用于验证深度对训练的影响和退化问题的解决], 证明了其不只是对一个特定的数据集才能有效，证明其普适性[generic]
8. 后为严谨讨论，也讨论了 $\mathbf{y} = F (\mathbf{x}, \{W_{i}\}) + W_{s}\mathbf{x}$ 这种情况。实验表明，由于本文主要是解决 degradation problem 而这个问题已然能通过 identity mapping 也就 $\mathbf{x}$ 解决，就没有必要再使用 $W_{s}$ 来徒增成本了。
9. 为严谨控制实验变量， Network Architectures 中严格定义了 

    **Plain Network** [参考了 the philosopy of VGG Nets]

    **Residual Network**

    同时还给出了**Figure-3** 展示了 VGG-19 和 34-layer plain 以及 34-layer residual 的 flowgraph 给出明确且清晰的实验变量控制。这点很重要，同时给出计算的 output size 以及 每个 model 对应的 FLOPs 数量。
10. [3.4]中还详细给出了 Implementation 的过程，参考[21, 41]--(回头要看看)的过程训练 ImageNet 数据集，然后进行了一些个（好像是进行数据异常平滑处理）的过程，包括 scale augmentation[41], horizontal flip, with the per-pixel mean subtracted[21], The standard color augmentation in [21], batch normalization(BN)[16], initialize the weights as in [13].

    训练使用了 SGD with a mini-batch size of 256, Learning rate 为0.1（/10每error pateaus）, 60*10^4 iterations.

    Adam优化器, momentum of 0.9, weight decay of 0.0001, 引入正则化 dropout[14], practice in [16]
11. Testing环节，进行对比实验采用 Standard 10-crop testing[21], 使用 fully-convolutional form as in [41, 13]--(回头要看看)，然后average the scores at multiple scales.
12. Deeper Bottleneck Architectures 本质上是在相同时间复杂度下进行降维训练再升维的一个优化，可以有效减少计算量但不降低模型的性能
---
**以下为2025.12.1-12.7补充的 ResNet 论文阅读笔记**

13. 计算 Bottleneck 建立的 Building blocks [Table.1] 需要用到公式 $Output = \lfloor \frac{Input + 2P - K}{S} \rfloor + 1$
**注意**
    - ImageNet 中初始图片 pixel 为 $224\times224$ , 默认 padding = 3
    - conv2_x 中有 $7\times7, 64, stride$ $2$ , 其余为 $stride$ $1$，而 conv3_x 等其余的卷积层为 $stride$ $2$。
    - Bottleneck 设计规范中 扩张率为4。
14. 下个部分到了对 CIFAR-10 数据集的训练和分析，同样首先搭建 Architecture , CIFAR-10 的数据一般是 pixel 为 $32\times32$ 的，同样 $stride$ $2$ ，分析出对应的 layers & filters, 然后阐述训练的方法都分别有什么……就和 ImageNet 相同的那些东西。
**有意思的地方**
    - 用 $n$ 来计算层数的数量，以控制深度。也方便比较不同深度的模型的性能，以 $n$ 的数量为媒介
    - $n = 18$ 的 110-layer ResNet 被作者单拎出来说了一嘴，作为 further explore。里面很有意思的就是，发现 0.1 is slightly too large to start converging, 所以先调低到0.01去 warm up 到 training error < 80% (约400轮迭代)，再回到0.1进行训练。还有这种操作！
15. 讨论 over 1000 layers 的时候发现模型的 error 又开始回升了，认为可能是 overfitting 了，将这个问题留待讨论作为下一步的研究方向。

---

## 一些评判标准

通过测试了如下dataset对模型性能进行评判

| 数据集名称 | 全称 | 作用/用途 | 
| :-----: | :--------: | :------ |
| ImageNet | ImageNet 2012 Classification Dataset |  **主要的验证集，用于图像分类任务。** 包含 1000 个类别，约 128 万张训练图像和 5 万张验证图像。所有主要的性能对比和超深网络（ResNet-50/101/152）的 SOTA 结果均在此数据集上获得。 | 
| CIFAR | CIFAR-10 和 CIFAR-100 | **深度/退化验证集。** 用于验证深度对训练的影响和退化问题的解决。这两个数据集较小，但足以用于快速迭代和训练超深网络（如 1000 层的 ResNet）。 |
| PASCAL VOC | The Pascal Visual Object Classes (VOC) Challenge | **目标检测和分割。** 用于验证 ResNet 作为特征提取器在更复杂的视觉任务上的泛化能力。 | 
| MS COCO | Microsoft Common Objects in Context | **目标检测和分割。** 同样用于验证 ResNet 在更大数据集和更复杂任务（目标检测、语义分割）上的性能优势。 | 

## ResNet 参加的一些比赛，都拿了 top1

- VOC 07 test

- VOC 12 test

- PASCAL VOC 2007 and 2012 [The Pascal Visual Object Classes (VOC) Challenge]

- ILSVRC & COCO 2015 competitions [ImageNet detection, ImageNet localization, COCO detection, and COCO segmentation]

#### 一点点积累

**FLOPs** 指浮点运算

**SOTA** 指State-of-the-Art, 达到目前性能最优

---
## Summary

对经典论文的写作架构有了非常充分的认识！

接下来想继续啃一些论文，想把一些实践性的学习任务留作寒假的时候赶，时间更充分。

---

## Next Week Plan

- [ ] 论文阅读[SAM3]'https://arxiv.org/pdf/2511.16719'
