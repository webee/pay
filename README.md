# 自游通

## 功能
为其它应该提供`支付`和`退款`接口。
提供`支付`, `退款`, `提现`, `充值`, `余额查看`和`订单查询`等功能。

## 账户设计

我们采用 _借贷记账法(一种复式计账法)_ 的原理来设计账户:
> 资产 = 负债 + 所有者权益
>> 有借必有贷，借贷必相等

自游通作为一个系统，我们从此系统的角度来考虑账户

### 外部资产
按照目前的设计，自游通的资产来自用户的支付, 充值, 在实现中是通过第三方支付(连连，微信，支付宝，银行卡等)方式进行资金流入

+ lvye-lianlian

    此为绿野在连连的商户账号, 所有通过连连接口的交易资金都是从这里中转。

以上账户金额增加记在`借方`，减少记在`贷方`, 正常余额在`借方`。

### 资产
资金在外部资产账户中进入和离开，最终都要体现在本系统中

+ lianlian(连连账户资产表)

    这是我们在连连系统中的账户在自游通中的流水记录表，也是自游通资产账户的分账户, 用于和连连账户对账。
+ asset(自由通资产账户)

    这是自游通资产总账户，记录了各资金来源的记账，事实上此由于目前我们只对接连连，所以结果跟lianlian账户是一样的。
    此账户作为第三方支付和自游通账户的连接，既把各种第三方账户连接起来，也使系统内部账户与第三方支付隔离开。

以上账户金额增加记在`借方`，减少记在`贷方`, 正常余额在`借方`。

### 负债
自游通的资产来自用户资金的流入，所以用户资金作为系统的负债

+ cash(现金账户)

    表明用户可用余额
+ frozen(冻结账户)

    用于提现和退款时的资金冻结
+ business(商户交易结算账户)

    用于商户交易的结算
+ secured(交易担保账户)

    用户交易时的资金担保

以上账户金额增加记在`贷方`，减少记在`借方`, 正常余额在`贷方`。

### 记账流程演示
订单状态的改变产生事件，事件驱动记账

#### 术语说明
```
# 账户相关缩写
借(d): debit
贷(c): credit
C: cash account
F: frozen account
B: business account
S: secured account
A: asset account
L: lianlian account
LYL: lvye-lianlian account

# 订单类型
PAY: 支付
SETTLE: 结算
REFUND: 退款
WITHDRAW: 提现
PREPAID: 充值
TRANSFER: 转账

# 订单过程状态
SECURED: 担保
EXPIRED: 到期
FROZEN: 冻结
SUCCESS: 成功

# 其它
summary: 汇总
balance: 余额
```

#### 账单记录
|event                   |[C/d-  |C/c+]  |[F/d-  |F/c+]  |[B/d-  |B/c+]  |[S/d-  |S/c+]  |/  |[A/d+  |A/c-]  |[L/d+  |L/c-]  |/  |[*LYL*/d+|*LYL*/c-]|
|:-----------------------|------:|------:|------:|------:|------:|------:|------:|------:|---|------:|------:|------:|------:|---|--------:|--------:|
|PAY SECURED 100         |       |       |       |       |       |       |       |    100|/  |    100|       |    100|       |/  |      100|         |
|PAY SECURED 50          |       |       |       |       |       |       |       |     50|/  |     50|       |     50|       |/  |       50|         |
|PAY EXPIRED 100         |       |       |       |       |       |    100|    100|       |/  |       |       |       |       |/  |         |         |
|PAY FROZEN 60           |       |       |       |       |       |       |       |     60|/  |     60|       |     60|       |/  |       60|         |
|PAY EXPIRE 50           |       |       |       |       |       |     50|     50|       |/  |       |       |       |       |/  |         |         |
|SETTLE SUCCESS 150      |       |    150|       |       |    150|       |       |       |/  |       |       |       |       |/  |         |         |
|REFUND FROZEN 60        |       |       |       |     60|       |       |     60|       |/  |       |       |       |       |/  |         |         |
|REFUND SUCCESS 60       |       |       |     60|       |       |       |       |       |/  |       |     60|       |     60|/  |         |       60|
|WITHDRAW FROZEN 120     |    120|       |       |    120|       |       |       |       |/  |       |       |       |       |/  |         |         |
|WITHDRAW SUCCESS 120    |       |       |    120|       |       |       |       |       |/  |       |    120|       |    120|/  |         |      120|
|PREPAID SUCCESS 30      |       |     30|       |       |       |       |       |       |/  |     30|       |     30|       |/  |       30|         |
|TRANSFER FROZEN 70      |     70|       |       |     70|       |       |       |       |/  |       |       |       |       |/  |         |         |
|TRANSFER SUCCESS 70     |       |     70|     70|       |       |       |       |       |/  |       |       |       |       |/  |         |         |
|XXXXX XXXX 000          |       |       |       |       |       |       |       |       |/  |       |       |       |       |/  |         |         |
|summary                 |    190|    250|    250|    250|    150|    150|    210|    210|/  |    240|    180|    240|    180|/  |      240|      180|
|balance                 |       |     60|       |      0|       |      0|       |      0|/  |     60|       |     60|       |/  |       60|         ||

#### 对账与试算平衡
对账
> 1. lianlian账户与lvye-lianlian账户的流水记录应该一致。
> 2. asset账户与lianlian等第三文账号的合计流水记录应该一致。


试算平衡
这里只需要考虑系统本身的账户(asset及其左边的账户)
*发生额试算平衡:*
> 全部账户借方发生额合计 = 全部账户贷方发生额合计
>> 190 + 250 + 150 + 210 + 240 = 1040 = 250 + 250 + 150 + 210 + 180

*余额额试算平衡:*
> 全部账户借方余额合计 = 全部账户贷方余额合计
>> 60 = 60 + 0 + 0 + 0

#### 其它
在实现上，目前各种订单是分别使用不同的表记录，各账户也是采用不同的表记录，事件是使用单一表。
对于冻结账户，目前是提现，退款和转账共用。
未来可能会将事件表和冻结账户分成功能单一的表。

## 可能的集成其它第三方支付
系统以 _连连支付_ 作为主要账户，作为资金中转账户。
假如我们增加了微信支付, 我们需要其完成 **支付**, **充值**, **退款** 等功能,
需要做如下事情:

```
+ 微信账户作为外部资金对账账户
+ 微信对应的business和secured账号
+ weixin-payment, weixin-prepaid, weixin-refund等表来记录相关功能, 或者在扩展原来的表
+ 添加微信支付，充值接口，支付微信退款
+ 增加WEIXIN-PAY, WEIXIN-REFUND, WEIXIN-PREPAID等event来源类型
```

下面讨论一下具体的操作流程

### 术语说明
```
# 账户相关缩写
W: weixin account
LYW: lvye-weixin account

# 订单类型
WEIXIN-PAY: 微信支付
WEIXIN-REFUND: 微信退款
WEIXIN-PREPAID: 微信充值
```

### 账单记录
在这里我们不考虑系统内部的过程，只看总资产和现金账户的变化。

|event                   |[C/d-  |C/c+]  |/  |[A/d+  |A/c-]  |[L/d+  |L/c-]  |[W/d+  |W/c-]  |/  |[*LYL*/d+|*LYL*/c-]|[*LYW*/d+|*LYW*/c-]|
|:-----------------------|------:|------:|---|------:|------:|------:|------:|------:|------:|---|--------:|--------:|--------:|--------:|
|PREPAID 10000           |       |  10000|/  |  10000|       |  10000|       |       |       |/  |    10000|         |         |         |
|PAY/PREPAID 200         |       |    200|/  |    200|       |    200|       |       |       |/  |      200|         |         |         |
|WEIXIN-PAY/PREPAID 100  |       |    100|/  |    100|       |       |       |    100|       |/  |         |         |      100|         |
|WITHDRAW 250            |    250|       |/  |       |    250|       |    250|       |       |/  |         |      250|         |         |
|WEIXIN-PAY/PREPAID 150  |       |    150|/  |    150|       |       |       |    150|       |/  |         |         |      150|         |
|WEIXIN-WITHDRAW 250     |    250|       |/  |       |    250|       |       |       |    250|/  |         |         |         |      250|
|PREPAID 250             |       |    250|/  |    250|       |    250|       |       |       |/  |      250|         |         |         |
|XXXXX XXXX 000          |       |       |/  |       |       |       |       |       |       |/  |         |         |         |         |
|summary                 |    500|  10700|/  |  10700|    500|  10450|    250|    250|    250|/  |    10450|      250|      250|      250|
|balance                 |       |  10200|/  |  10200|       |  10200|       |      0|       |/  |    10200|         |        0|         ||

对账和试算平衡可以参考上一节。

我们提现全部在连连账户进行，上面流程说明通过连连支付/充值了200，通过微信支付/充值了100, 一共是300元现金可提现，然后提现250,
由于此时连连账户只进行了200，不够提现，因此我们需要事先在连连账户中充值了10000元作为资金缓冲用。
之后对微信来源的资金结算之后，提现，充值到连连，就完成了整个资金的转移了。


Copyright (c) 2015 Copyright lvye.com All Rights Reserved.
