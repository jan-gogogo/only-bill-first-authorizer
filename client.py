import json

import eospy
from eospy.cleos import Cleos
from eospy.keys import EOSKey
from eospy.types import EOSEncoder, Transaction
from eospy.utils import sig_digest
import server as SERVER

# 麒麟测试节点
ce = eospy.cleos.Cleos(url='https://api-kylin.eosasia.one')

# 构造交易数据（图1-1 步骤1）
# args是需要调用的`action`的入参，这里是转账所以入参分别是：from、to、quantity和memo
args = {
    "from": "sweetsummer1",         # 发起交易的账号
    "to": "kingofighter",           # 接收者账号
    "quantity": '100.0000 SJ',      # 接收金额
    "memo": "action:imrich,us:9b414076514a,ush:48e7f2371a4e9f9171f3ee0485b05eec19e2728bf31498bc0b2358d30b7bb523,et:1579786171,sig:SIG_K1_K7yTP8qvJDDWbaHJkJpFGL8bRxLXKGkVjqEBscyQLDEXF4QuaYqUcBg39WRCkx8BQ3GHKD4mUpeso6mqFDX5LQXvxXq7Ei"
}

payload = [
    {
        "account": "kofgametoken",
        "name": "transfer",
        "authorization": [{
            "actor": "kingofighter",
            "permission": "cpupayer",   # 由原来的`active`修改为`cpupayer`
        }, {
            "actor": "sweetsummer1",
            "permission": "active",
        }],
    }
]

# 调用区块链，将交易数据转换成16进行字符串（图1-1 步骤2）
# 入参：account、name、args
data = ce.abi_json_to_bin(payload[0]['account'], payload[0]['name'], args)

# 将返回的`data`加入到`payload`
payload[0]['data'] = data['binargs']

# 构造`trx`（图1-1 步骤3）
# 这时的`payload`有：data、account、name和authorization
trx = {"actions": [payload[0]]}

# 对`trx`进行哈希计算（图1-1 步骤4）
chain_info, lib_info = ce.get_chain_lib_info()
trx_chain = Transaction(trx, chain_info, lib_info)
hash_trx = sig_digest(trx_chain.encode(), chain_info['chain_id'])

# 请求服务端 对`trx`哈希进行签名（图1-1 步骤5）
server_sign = SERVER.sign(hash_trx)

# 玩家自己也需要对相同数据进行签名（图1-1 步骤6）
k = EOSKey('玩家私钥')  # 玩家私钥
player_sign = k.sign(hash_trx)

# 组合签名，顺序要和`payload.authorization`的顺序一致
signatures = []
signatures.append(server_sign)  # 服务端签名放在第一个位置
signatures.append(player_sign)  # 玩家签名跟在后面

final_trx = {
    'compression': 'none',
    'transaction': trx_chain.__dict__,
    'signatures': signatures
}
data = json.dumps(final_trx, cls=EOSEncoder)

timeout = 30
# 调用区块链`push_transaction`提交交易请求
res = ce.post('chain.push_transaction', params=None, data=data, timeout=timeout)
print(res)
