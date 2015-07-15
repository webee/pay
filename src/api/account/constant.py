# coding=utf-8


class withdraw(object):
    # 提现订单结果
    ## 提现请求失败
    WITHDRAW_REQUEST_FAILURE = 'REQUEST_FAILURE'
    ## 提现冻结
    WITHDRAW_FROZEN = 'FROZEN'
    ## 提现成功
    WITHDRAW_SUCCESS = 'SUCCESS'
    ## 提现失败
    WITHDRAW_FAILURE = 'FAILURE'

    # 提现事件过程
    ## 提现冻结资金
    STEP_FROZEN = 'FROZEN'
    ## 提现失败资金解冻
    STEP_FAILED = 'FAILED'
    ## 提现成功资金解冻
    STEP_SUCCESS = 'SUCCESS'
