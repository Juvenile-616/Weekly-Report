# 11.1-11.7 周报

    Author: 彭日骏
    Edit Time: 2025/11/01-2025/11/07

---
## Plan

- [x] LSTM

---
## Summary

尝试不依靠Gemini完全自主的编写了stock prices prediction project, 使用的是lstm的架构。全程非常顺利，因为有过RNN编写时间预测的一个经历，数据预处理也很简单，比起音频处理简单得多，所以很快就成功了。加深了一些工程上的对lstm的理解，关注到了很多以前没有理解的细节：

比如：

batch_first=True是为了适应便于工程习惯的(batch_size, tw, features)的数据格式

reshape(-1, 1)是为了数据降维以计算loss

总的来说时间序列数据Pytorch上实现lstm的难度不大

---

## Next Week Plan

- [ ] ResNet paper阅读
- [ ] Transformer架构完整理解
- [ ] Transformer架构深化学习和实践

由于临近期中，有些期中考试需要准备，课业压力大了些，请老师多担待，也麻烦老师指点迷津！
