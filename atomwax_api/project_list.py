#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Longgeek <longgeek@gmail.com>

"""
初始化项目信息

在项目 runserver 时候会在 Redis 中写入所有项目信息，生成基本数据结构
"""

project_list = [
    {
        "name": "PIKA",
        "repo": "https://github.com/OpenAtomFoundation/pika",
        "id": 3,
        "image": "https://openatom.cn/uploads/getImg?uri=aW1hZ2VGaWxlLzNhd3ovbHE3Mi9waWthX2ljb25fMjAyMDEyMjUyMzI1MjIucG5n",
        "description": "PIKA 是 360 DBA 和基础架构组联合开发的类 Redis 存储系统",
        "join_time": "xxxx-xx-xx xx-xx-xx",
        "watch": 0,
        "star": 0,
        "fork": 0,
        "issue": 0,
        "commits": 0,
        "pull_requests": 0,
        "contributors": 0,
        "line_of_code": 0,
    },
    {
        "name": "XuperChain",
        "repo": "https://github.com/xuperchain/xuperchain",
        "id": 1,
        "image": "https://openatom.cn/uploads/getImg?uri=aW1hZ2VGaWxlL3h5YjAvNnc2YS94dXBlcmNoYWluX2ljb25fMjAyMDEyMjUyMzI1NDYucG5n",
        "description": "XuperChain 是百度公司自主研发的底层区块链技术, 支持平行链和侧链的区块链网络",
        "join_time": "xxxx-xx-xx xx-xx-xx",
        "watch": 0,
        "star": 0,
        "fork": 0,
        "issue": 0,
        "commits": 0,
        "pull_requests": 0,
        "contributors": 0,
        "line_of_code": 0,
    },
    {
        "name": "OpenHarmony",
        "org": "https://gitee.com/openharmony",
        "repo": "",
        "id": 2,
        "image": "https://openatom.cn/uploads/getImg?uri=aW1hZ2VGaWxlL2prcGUvOGtjay9vcGVuaGFybW9ueV9pY29uXzIwMjAxMjI1MjMyNTMzLnBuZw==",
        "description": "OpenHarmony 的定位是一款面向全场景的开源分布式操作系统",
        "join_time": "xxxx-xx-xx xx-xx-xx",
        "watch": 0,
        "star": 0,
        "fork": 0,
        "issue": 0,
        "commits": 0,
        "pull_requests": 0,
        "contributors": 0,
        "line_of_code": 0,
    },
    {
        "name": "TKEStack",
        "repo": "https://github.com/tkestack/tke",
        "id": 4,
        "image": "https://openatom.cn/uploads/getImg?uri=aW1hZ2VGaWxlL3VocmwvMG1saS90a2VfaWNvbl8yMDIwMTIyNTIzMjQ0Mi5wbmc=",
        "description": "TKEStack 是腾讯开源的一款集强壮性和易用性于一身的企业级容器编排引擎",
        "join_time": "xxxx-xx-xx xx-xx-xx",
        "watch": 0,
        "star": 0,
        "fork": 0,
        "issue": 0,
        "commits": 0,
        "pull_requests": 0,
        "contributors": 0,
        "line_of_code": 0,
    },
    {
        "name": "UBML",
        "repo": "https://gitee.com/ubml/ubml-impl",
        "id": 5,
        "image": "https://openatom.cn/uploads/getImg?uri=aW1hZ2VGaWxlL3B6cjQvMTA0ci91Ym1sX2ljb25fMjAyMDEyMjUyMzI0MTYucG5n",
        "description": "UBML 建模开发体系是浪潮开源的面向企业软件的低代码开发平台核心基础",
        "join_time": "xxxx-xx-xx xx-xx-xx",
        "watch": 0,
        "star": 0,
        "fork": 0,
        "issue": 0,
        "commits": 0,
        "pull_requests": 0,
        "contributors": 0,
        "line_of_code": 0,
    },
    {
        "name": "TencentOS Tiny",
        "repo": "https://github.com/Tencent/TencentOS-tiny",
        "id": 6,
        "image": "https://openatom.cn/uploads/getImg?uri=aW1hZ2VGaWxlLzljeWIvd3FyMi90aW55XzIwMjAxMjI1MjMxNjAyLnBuZw==",
        "description": "TencentOS Tiny 是腾讯公司孵化的一款低功耗、低资源占用物联网的终端操作系统",
        "join_time": "xxxx-xx-xx xx-xx-xx",
        "watch": 0,
        "star": 0,
        "fork": 0,
        "issue": 0,
        "commits": 0,
        "pull_requests": 0,
        "contributors": 0,
        "line_of_code": 0,
    },
    {
        "name": "AliOS Things",
        "repo": "https://github.com/alibaba/AliOS-Things",
        "id": 7,
        "image": "https://openatom.cn/uploads/getImg?uri=aW1hZ2VGaWxlL2prbG8vanJxdy90aGluZ3NfaWNvbl8yMDIwMTIyNTIzMDUzNS5wbmc=",
        "description": "AliOS Things 是面向 IoT 领域的轻量级物联网嵌入式操作系统",
        "join_time": "xxxx-xx-xx xx-xx-xx",
        "watch": 0,
        "star": 0,
        "fork": 0,
        "issue": 0,
        "commits": 0,
        "pull_requests": 0,
        "contributors": 0,
        "line_of_code": 0,
    },
    {
        "name": "ZNBase",
        "repo": "https://github.com/ZNBase/ZNBase",
        "id": 8,
        "image": "https://openatom.cn/uploads/getImg?uri=aW1hZ2VGaWxlL2prbG8vanJxdy90aGluZ3NfaWNvbl8yMDIwMTIyNTIzMDUzNS5wbmc=",
        "description": "ZNBase是新一代分布式数据库，采用去中心设计架构，每个节点都参与运算和存储，拥有事务强一致性、无限横向扩展、多中心数据同步、多副本高可用、国产化安全可靠等特性，并且提供数据库自动部署、自动备份、自动容灾、数据恢复、监控等能力。",
        "join_time": "xxxx-xx-xx xx-xx-xx",
        "watch": 0,
        "star": 0,
        "fork": 0,
        "issue": 0,
        "commits": 0,
        "pull_requests": 0,
        "contributors": 0,
        "line_of_code": 0,
    }
]
