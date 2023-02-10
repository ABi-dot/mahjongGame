from itertools import combinations

class MjMath(object):
    concealed_count = [1, 4, 7, 10, 13]
    test = False

    def __init__(self):
        pass

    @classmethod
    def get_pair_keys(cls, arr):
        keys = dict()
        for x in arr:
            if x not in keys:
                keys[x] = 0
            keys[x] += 1
        pair_keys = [x for x in keys if keys[x] > 1]
        return pair_keys

    @classmethod
    def remove_pair_from_arr(cls, arr, key):
        result = []
        count = 0

        for x in arr:
            if x == key and count < 2:
                count += 1
            else:
                result.append(x)

        if count < 2:
            raise ValueError(f"{arr} 内 {key} 的数量不足 2")

        return result

    @classmethod
    # 刻子 is triplet
    def is_111(cls, arr):
        if len(arr) != 3:
            return False
        if arr[0] == arr[1] and arr[0] == arr[2]:
            return True
        return False

    @classmethod
    # 顺子 is sequence
    def is_123(cls, arr):
        if len(arr) != 3:
            return False
        if arr[0] + 1 == arr[1] and arr[0] + 2 == arr[2]:
            return True
        return False

    @classmethod
    # 从 list1 中减掉 list2，剩下了什么？ list1 - list2 = ?
    def list_sub(cls, list1, list2):
        arr = list1[:]
        for ix, x in enumerate(list2):
            for iy, y in enumerate(arr):
                if x == y:
                    arr.pop(iy)
                    break
        return arr

    @classmethod
    # 数组中，不是刻子，就是顺子 is well-meld arr
    def is_good_meld_arr(cls, arr):
        if cls.is_111(arr) or cls.is_123(arr):
            return True

        for x in combinations(arr, 3):
            if (not cls.is_111(x)) and (not cls.is_123(x)):
                continue
            remain = cls.list_sub(arr, x)
            if cls.is_good_meld_arr(remain):
                return True
            if cls.is_111(remain) or cls.is_123(remain):
                return True

        return False

    @classmethod
    # is well-meld arr + 1 pair of eyes
    def is_good_concealed(cls, arr):
        if not arr:
            cls.debug('not hand')
            return False

        count = len(arr)
        count -= 1
        if count not in cls.concealed_count:
            cls.debug('count error')
            return False

        pair_keys = cls.get_pair_keys(arr)
        for key in pair_keys:
            test = cls.remove_pair_from_arr(arr, key)
            if not test:
                # only have one pair
                return True
            if cls.is_good_meld_arr(test):
                return True
        return False

    @classmethod
    def is_131(cls, arr: list) -> bool:
        if len(arr) != 14:
            return False
        array = arr[:]
        keys = set(array)
        if len(keys) + 1 != 14:
            return False
        allowed = {101, 109, 201, 209, 301, 309, 410, 420, 430, 510, 520, 530, 540}
        if keys == allowed:
            return True
        return False

    @classmethod
    def is_7c(cls, arr: list) -> bool:
        if len(arr) != 14:
            return False
        array = arr[:]
        keys = list(set(array))
        for x in keys:
            if array.count(x) != 2:
                return False
        return True

    @classmethod
    def is_rong(cls, arr: list) -> bool:
        if cls.is_131(arr):
            print("is_131")
            return True
        if cls.is_7c(arr):
            print("is_7c")
            return True
        return cls.is_good_concealed(arr)

    @classmethod
    def get_chow_combins_from_arr(cls, arr: list, outer: int) -> list:
        if not outer:
            raise ValueError(f"need an outer:{outer}")
        candidates = []
        for x in arr:
            if outer - 2 <= x <= outer + 2:
                candidates.append(x)
        if not candidates:
            return []
        combins = []
        fails = []
        for combin in combinations(candidates, 2):
            test = list(combin)
            test.sort()
            chow = test[:]
            chow.append(outer)
            chow.sort()
            if test in combins or test in fails:
                continue
            if MjMath.is_123(chow):
                combins.append(test)
            else:
                fails.append(test)
        return combins