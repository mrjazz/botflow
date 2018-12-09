import re


def equals(s):
    return lambda x: x == s


def regexp(pattern, params=re.MULTILINE | re.DOTALL | re.IGNORECASE):
    p = re.compile(pattern, params)
    return lambda x: p.match(x)


if __name__ == '__main__':
    print(equals("ok")("ok1"))
