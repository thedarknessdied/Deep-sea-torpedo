import string
import random


class ProduceRandomValue(object):
    UPPER_LETTERS = string.ascii_uppercase
    LOWER_LETTERS = string.ascii_lowercase
    NUMBERS = string.digits
    WHITESPACE = string.whitespace
    PUNCTUATION = string.punctuation

    def __init__(self, MIN_VARIABLE_CNT: int = 1, MAX_VARIABLE_CNT: int = 10,
                 MIN_VARIABLE_LENGTH: int = 1, MAX_VARIABLE_LENGTH: int = 10, empty: bool = False):
        if MIN_VARIABLE_CNT is None or MIN_VARIABLE_CNT < 0:
            if empty:
                self.__MIN_VARIABLE_CNT = 0
            else:
                self.__MIN_VARIABLE_CNT = 1
        else:
            self.__MIN_VARIABLE_CNT = MIN_VARIABLE_CNT
        self.__MAX_VARIABLE_CNT = self.__MIN_VARIABLE_CNT if MAX_VARIABLE_CNT is None or MAX_VARIABLE_CNT < self.__MIN_VARIABLE_CNT else MAX_VARIABLE_CNT

        if MIN_VARIABLE_LENGTH is None or MIN_VARIABLE_LENGTH < 0:
            if empty:
                self.__MIN_VARIABLE_LENGTH = 0
            else:
                self.__MIN_VARIABLE_LENGTH = 1
        else:
            self.__MIN_VARIABLE_LENGTH = MIN_VARIABLE_LENGTH
        self.__MAX_VARIABLE_LENGTH = self.__MIN_VARIABLE_LENGTH if MAX_VARIABLE_LENGTH is None or MAX_VARIABLE_LENGTH < self.__MIN_VARIABLE_LENGTH else MAX_VARIABLE_LENGTH

    def set_variable_length(self, min_length: int = None, max_length: int = None):
        if min_length is not None and min_length >= 0:
            self.__MIN_VARIABLE_LENGTH = min_length
        if max_length is not None and max_length >= self.__MIN_VARIABLE_LENGTH:
            self.__MAX_VARIABLE_LENGTH = max_length

    @classmethod
    def _create_random_value(cls, length: int, letter: str, exclude_symbols: str = "") -> str:
        index = 0
        res = list()
        while index < length:
            cur = random.choice(letter)
            if cur in exclude_symbols:
                continue
            res.append(cur)
            index = index + 1
        return ''.join(res)

    def create_random_variable_name(self, length: int, is_value: bool = False, mode: str = "mixed",
                                    need_special_symbols: bool = False, special_symbols: str = "",
                                    exclude_symbols: str = "") -> (str, int):
        _start = 0 if is_value else 1

        if length < self.__MIN_VARIABLE_LENGTH or length > self.__MAX_VARIABLE_LENGTH:
            if is_value:
                length = 1
            else:
                length = 2

        if mode.lower() == "mixed":
            letters = self.LOWER_LETTERS + self.UPPER_LETTERS
        elif mode.lower() == "upper":
            letters = self.UPPER_LETTERS
        elif mode.lower() == 'lower':
            letters = self.LOWER_LETTERS
        else:
            letters = self.LOWER_LETTERS + self.UPPER_LETTERS

        _prefix = self._create_random_value(_start, letters, exclude_symbols)

        remain = letters + self.NUMBERS
        if need_special_symbols:
            remain = remain + self.PUNCTUATION
        if special_symbols is not None and not special_symbols:
            remain = remain + special_symbols

        _suffix = self._create_random_value(length - _start, remain, exclude_symbols)
        o = _prefix + _suffix
        return o, length

    def create_random_variable_length(self) -> int:
        return random.randint(self.__MIN_VARIABLE_CNT, self.__MAX_VARIABLE_CNT)


o = BaseUtils()
print(o.create_random_variable_name(o.create_random_variable_length(), special_symbols="@"))