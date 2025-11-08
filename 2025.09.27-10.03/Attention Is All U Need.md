## *Attention Is All You Need* 论文阅读汇报
### *单词扫盲*
    dominant 主流的
    sequence transduction models 序列转换模型
    sequential 顺序的
    convolutional 卷积的
    mechanism 机制
    architecture 架构
    recurrence 循环
    parallel 并行
    fraction 部分
    evaluate 评估
    *self-attention 自注意力
    implement 实施
    parameter 参数；范围
    tun 调试
    model variant 模型变体
    codebase 代码库
    inference 推理
    visualization 可视化
    state of the art approaches 最先进的方法
    align 对齐
    constraint 限制
    conjunction 结合
    eschew 避开
    constant 恒定的
    albeit 尽管
    counteract 抵消
### *Abstract* 关键词
        1. attention mechanism（注意力机制）
        2. scaled dot-product attention
        3. multi-head attention
        4. parameter-free position representation
### *Introduction* 关键词
        1. 旧时处理transduction problem: Recurrent neutral networks 循环神经网络
            --- long short-term memory 长短期记忆网络（LSTM）[13]
                [13] Sepp Hochreiter and Jürgen Schmidhuber. Long short-term memory. Neural computation,9(8):1735–1780, 1997.
            --- gated recurrent neutral networks 门控循环神经网络（GRU）[7]
                [7]
            --- conditional computation 条件计算作优化计算效率和模型性能都有提高
            --- fundamental constraint of sequential computation 仍旧存在
            --- usually be used in conjunction with attention mechanisms
            --- 我结合了知乎 https://zhuanlan.zhihu.com/p/123211148 与论文内容进行了解
            --- 得到解释 什么是
        2. Transformer 模型
            --- 完全依赖一个 attention mechanism（注意力机制） 排除掉recurrence 对输入输出的全局依赖关系进行建模的一个模型
            --- 并行化更好、效率更高、且translation的质量也更高了
### *Background* 关键词
        1. Extended Neural GPU, ByteNet, ConvS2S
            --- 都使用 CNN(convolutional neural networks) as basic block, 并行计算所有输入输出的隐藏表示的位置？？
            --- 是为了更好解决transduction problem而进行的过往的模型改进
            --- 减少sequential computation本来也是这些改进算法的目标
            --- 共性问题：将任意的两个输入输出信号的位置关联起来的并行计算的操作数，会随其位置之间的距离而快速增长（在ConvS2S模型中会线性增长，在ByteNet中会对数增长），使得模型更难学习两个较远信号之间的依赖关系
            --- 相较于上述模型，Transformer采用average attention-weighted positions(?), 使得操作数减少到一个恒定数量，但 effective resolution（有效分辨率）降低了
            --- Transformer又通过 Multi-Head Attention（多头注意力） 抵消这种影响
            --- 结合了知乎文章 https://zhuanlan.zhihu.com/p/635438713 了解了CNN（？回看论文部分）
            --- 
        2. Self-attention（自注意力）
            --- 又称 intra-attention（内部注意力）
            --- 将单个序列中不同位置关联起来以计算序列表示的注意力机制
            --- 已具有广泛的应用场景：reading comprehension, abstractive summarization,  textual entailment, learning task-independent sentence representations(??)
        3. End-to-end memory networks（端到端记忆网络）
            --- based on  recurrent attention machanism（循环注意力机制），而非 sequence-aligned recurrence（序列对齐循环）
            --- 应用于简单的语言问题回答
        4. Transformer
            --- 完全依赖 self-attention 计算输入输出表示而不需要使用 sequence-aligned RNNs（序列对齐的循环神经网络）或卷积
            --- 接下来详细介绍 Transformer 相较于其他的模型的优势在哪里

### *网页文献参考*
    1.https://zhuanlan.zhihu.com/p/1934725539521857231
    2.https://www.zhihu.com/question/302392659 你真的懂Transformer吗的评论区
    3.https://zhuanlan.zhihu.com/p/123211148 https://zhuanlan.zhihu.com/p/32085405 看完主要0基础入门后可以看这个回顾RNN\LSTM
    4.https://zhuanlan.zhihu.com/p/30844905 回顾RNN
    5.https://zybuluo.com/hanbingtao/note/541458 主战场，写得超级好，公式推导非常详细。

    6.https://zhuanlan.zhihu.com/p/635438713 CNN入门，写的也超级nice
    7.https://www.bilibili.com/video/BV1696PY9Ex6?spm_id_from=333.788.videopod.episodes&vd_source=c75344f94911e33a4d034c368d4d951d&p=13 主战场，3h完全弄懂RNN\LSTM\GRU
    8.https://www.bilibili.com/video/BV18P4y1j7uH?vd_source=c75344f94911e33a4d034c368d4d951d&spm_id_from=333.788.videopod.sections 可对模型进行简单直观理解，然后再次基础上对模型理解进行补充