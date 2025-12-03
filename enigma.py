import string


class Enigma:
    def __init__(self, rotor_order, rotor_pos, ring_settings, reflector='B'):
        """
        rotor_order: порядок роторов
        rotor_positions: позиции роторов
        ring_settings: настройки колец
        reflector: рефлектор
        """
        self.alphabet = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"

        # Роторы
        self.rotors = {
            1: "БВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯА",  # р
            2: "ВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯАБ",  # е
            3: "ГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯАБВ",  # х
            4: "ДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯАБВГ",  # й
            5: "ЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯАБВГД"  # щ
        }

        # Рефлекторы
        self.reflectors = {
            'A': "ЯЮЭЬЫЪЩШЧЦХФУТСРПОНМЛКЙИЗЖЁЕДГВБА",
            'B': "ЪЫЬЭЮЯАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩ",
            'C': "ЩШЧЦХФУТСРПОНМЛКЙИЗЖЁЕДГВБАЯЮЭЬЫЪ"
        }

        # Позиции оборота
        self.turnover = {
            1: 'Р',
            2: 'Е',
            3: 'Х',
            4: 'Й',
            5: 'Щ'
        }

        self.rotor_order = rotor_order or [1, 2, 3]
        self.rotor_pos = rotor_pos or ['А', 'А', 'А']
        self.ring_settings = ring_settings or [0, 0, 0]
        self.reflector = reflector or 'B'

        self.current_pos = self.rotor_pos.copy()

    def _is_russian_letter(self, char):
        """Проверка, является ли символ русской буквой"""
        return char.upper() in self.alphabet

    def _get_letter_index(self, letter):
        """Безопасное получение индекса буквы в алфавите"""
        try:
            return self.alphabet.index(letter.upper())
        except ValueError:
            # Если буквы нет в алфавите, возвращаем 0 как значение по умолчанию
            return 0

    def _rotate_rotors(self):
        """Вращение роторов перед шифрованием каждого символа"""
        # Проверяем, является ли текущая позиция среднего ротора позицией оборота
        middle_double_step = (self.current_pos[1] == self.turnover[self.rotor_order[1]])

        # Вращаем правый ротор
        self.current_pos[2] = self._next_letter(self.current_pos[2])

        # Условие для вращения среднего ротора
        if (self.current_pos[2] == self.turnover[self.rotor_order[2]]) or middle_double_step:
            self.current_pos[1] = self._next_letter(self.current_pos[1])

            # Условие для вращения левого ротора
            if self.current_pos[1] == self.turnover[self.rotor_order[1]]:
                self.current_pos[0] = self._next_letter(self.current_pos[0])

    def _next_letter(self, letter):
        """Получить следующую букву в алфавите"""
        try:
            index = self.alphabet.index(letter.upper())
            return self.alphabet[(index + 1) % len(self.alphabet)]
        except ValueError:
            # Если буквы нет в алфавите, возвращаем первую букву
            return 'А'

    def _previous_letter(self, letter):
        """Получить предыдущую букву в алфавите"""
        try:
            index = self.alphabet.index(letter.upper())
            return self.alphabet[(index - 1) % len(self.alphabet)]
        except ValueError:
            # Если буквы нет в алфавите, возвращаем последнюю букву
            return 'Я'

    def _process_through_rotor(self, char, rotor_num, forward=True):
        """Прохождение символа через ротор"""
        if not self._is_russian_letter(char):
            return char

        rotor = self.rotors[self.rotor_order[rotor_num]]
        position = self.current_pos[rotor_num]
        ring_setting = self.ring_settings[rotor_num]

        # Безопасное получение индексов
        char_index = self._get_letter_index(char)
        position_index = self._get_letter_index(position)

        # Учитываем позицию ротора и настройку кольца
        effective_index = (char_index + position_index - ring_setting) % len(self.alphabet)

        if forward:
            # Прямое прохождение
            result_char = rotor[effective_index]
            # Компенсируем сдвиг
            result_index = (self._get_letter_index(result_char) - position_index + ring_setting) % len(self.alphabet)
        else:
            # Обратное прохождение
            try:
                rotor_index = rotor.index(char.upper())
            except ValueError:
                # Если символ не найден в роторе, возвращаем его без изменений
                return char

            effective_rotor_index = (rotor_index + position_index - ring_setting) % len(self.alphabet)
            result_char = self.alphabet[effective_rotor_index]
            # Компенсируем сдвиг
            result_index = (self._get_letter_index(result_char) - position_index + ring_setting) % len(self.alphabet)

        result = self.alphabet[result_index % len(self.alphabet)]

        # Сохраняем регистр
        return result if char.isupper() else result.lower()

    def encrypt_char(self, char):
        """Шифрование одного символа"""
        if not self._is_russian_letter(char):
            return char

        uppercase_char = char.upper()

        # Вращаем роторы
        self._rotate_rotors()

        current_char = uppercase_char

        # Прямой проход через роторы (правый → средний → левый)
        for i in [2, 1, 0]:
            current_char = self._process_through_rotor(current_char, i, forward=True)

        # Проход через рефлектор
        reflector_index = self._get_letter_index(current_char)
        current_char = self.reflectors[self.reflector][reflector_index]

        # Обратный проход через роторы (левый → средний → правый)
        for i in [0, 1, 2]:
            current_char = self._process_through_rotor(current_char, i, forward=False)

        result_char = current_char

        # Сохраняем регистр
        return result_char if char.isupper() else result_char.lower()

    def encrypt(self, text):
        """Шифрование текста"""
        result = []
        for char in text:
            result.append(self.encrypt_char(char))
        return ''.join(result)

    def decrypt(self, text):
        """Дешифрование текста (для Энигмы шифрование и дешифрование одинаковы)"""
        return self.encrypt(text)

    def reset(self):
        """Сброс позиций роторов к начальным"""
        self.current_pos = self.rotor_pos.copy()


# Функция для шифрования текста
def enigma_encrypt(text, rotor_order=[1, 2, 3], rotor_positions=['А', 'А', 'А'],
                   ring_settings=[0, 0, 0], reflector='B'):
    """
    Функция для шифрования текста алгоритмом Энигмы

    Args:
        text: текст для шифрования
        rotor_order: порядок роторов [левый, средний, правый]
        rotor_positions: начальные позиции роторов
        ring_settings: настройки колец
        reflector: рефлектор (A, B или C)

    Returns:
        Зашифрованный текст
    """
    if not text:
        return text

    rotor_order = rotor_order or [1, 2, 3]
    rotor_positions = rotor_positions or ['А', 'А', 'А']
    ring_settings = ring_settings or [0, 0, 0]
    reflector = reflector or 'B'

    alphabet = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
    for i in range(len(rotor_positions)):
        if rotor_positions[i].upper() not in alphabet:
            rotor_positions[i] = 'А'
        else:
            rotor_positions[i] = rotor_positions[i].upper()

    enigma = Enigma(rotor_order, rotor_positions, ring_settings, reflector)
    return enigma.encrypt(text)


# Функция для дешифрования текста
def enigma_decrypt(text, rotor_order=[1, 2, 3], rotor_positions=['А', 'А', 'А'],
                   ring_settings=[0, 0, 0], reflector='B'):
    """
    Функция для дешифрования текста алгоритмом Энигмы
    """
    return enigma_encrypt(text, rotor_order, rotor_positions, ring_settings, reflector)