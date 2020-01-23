from eospy.keys import EOSKey


def sign(digest):
    k = EOSKey('cpupayer权限私钥') # 由原来的`active`修改为`cpupayer`私钥
    return k.sign(digest)
