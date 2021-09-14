

def replace_ubi_rl(self, col: str):
    largo = len(y := self[col])
    if largo == 5:
        return '0' + y
    elif largo == 4:
        return '00' + y
    elif largo == 3:
        return '000' + y
    elif largo == 2:
        return '0000' + y
    elif largo == 1:
        return '00000' + y
    else:
        return y

def replace_ubi_rr(self, col: str):
    largo = len(y := self[col])
    if largo == 5:
        return y + '0'
    elif largo == 4:
        return y + '00'
    elif largo == 3:
        return y + '000'
    elif largo == 2:
        return y + '0000'
    elif largo == 1:
        return y + '00000'
    else:
        return y