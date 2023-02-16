class Suit(object):
    """
    Warning:
        - don't change the 'base' attr for suit
        - the 'value' attr should be in range(100)
        * MjMath class calculations depend on this rules
    """
    Suit = {
        '万': {
            'base': 100,
            'eng': 'character',
            'text': '万',
        },
        '饼': {
            'base': 200,
            'eng': 'dot',
            'text': '饼',
        },
        '条': {
            'base': 300,
            'eng': 'bamboo',
            'text': '条',
        },
        '字': {
            'base': 400,
            'eng': 'dragon',
            'text': '字',
        },
        '风': {
            'base': 500,
            'eng': 'wind',
            'text': '风',
        },
    }

    Wind = {
        '东': {
            'value': 10,
            'eng': 'east',
            'text': '东',
        },
        '南': {
            'value': 20,
            'eng': 'south',
            'text': '南',
        },
        '西': {
            'value': 30,
            'eng': 'west',
            'text': '西',
        },
        '北': {
            'value': 40,
            'eng': 'north',
            'text': '北',
        },
    }

    Dragon = {
        '白': {
            'value': 10,
            'eng': 'white',
            'text': '白',
        },
        '发': {
            'value': 20,
            'eng': 'green',
            'text': '发',
        },
        '中': {
            'value': 30,
            'eng': 'red',
            'text': '中',
        },
    }

    @classmethod
    def getWindByIndex(cls, idx) -> str:
        idx = idx % 4
        keys = [key for key in cls.Wind]
        if idx < 0 or idx >= len(keys):
            raise ValueError(f"idx {idx} out of range of Wind")
        res = keys[idx]
        return res

    @classmethod
    def getNextWind(cls, wind):
        if not wind:
            wind = '东'
        if wind not in cls.Wind:
            raise ValueError(f"{wind} not in Wind Enum")
        p = 0
        for idx, w in enumerate(cls.Wind):
            if w == wind:
                p = idx
                break
        return cls.getWindByIndex((idx + 1) % 4)

    @classmethod
    def getBeforeWind(cls, wind):
        if not wind:
            wind = '东'
        if wind not in cls.Wind:
            raise ValueError(f"{wind} not in Wind Enum")
        p = 0
        for idx, w in enumerate(cls.Wind):
            if w == wind:
                p = idx
                break
        return cls.getWindByIndex((idx - 1 + 4) % 4)

    @classmethod
    def getOppositionWind(cls, wind:str):
        return cls.getNextWind(cls.getNextWind(wind))

def main():
    print(Suit.getBeforeWind('东'))

if __name__ == '__main__':
    main()