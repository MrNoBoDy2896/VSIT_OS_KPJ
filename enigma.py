import string


class Enigma:
    def __init__(self, rotor_order, rotor_pos, ring_settings):
        """
        rotor_order: порядок роторов
        rotor_positions: позиции роторов
        ring_settings: настройки колец
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
        self.reflector = 'B'

        self.current_pos = self.rotor_pos.copy()

    def _rotate_rotors(self):
        """Вращение роторов перед шифрованием каждого символа"""
        middle_double_step = (self.current_pos[1] == self.turnover[self.rotor_order[1]])

        self.current_pos[2] = self._next_letter(self.current_pos[2])

        if (self.current_pos[2] == self.turnover[self.rotor_order[2]]) or middle_double_step:
            self.current_pos[1] = self._next_letter(self.current_pos[1])

            if self.current_pos[1] == self.turnover[self.rotor_order[1]]:
                self.current_pos[0] = self._next_letter(self.current_pos[0])

    def _next_letter(self, letter):
        """Получить следующую букву в алфавите"""
        index = self.alphabet.index(letter)
        return self.alphabet[(index + 1) % len(self.alphabet)]

    def _previous_letter(self, letter):
        """Получить предыдущую букву в алфавите"""
        index = self.alphabet.index(letter)
        return self.alphabet[(index - 1) % len(self.alphabet)]

    def _process_through_rotor(self, char, rotor_num, forward=True):
        """Прохождение символа через ротор"""
        rotor = self.rotors[self.rotor_order[rotor_num]]
        position = self.current_pos[rotor_num]
        ring_setting = self.ring_settings[rotor_num]

        # Учитываем позицию ротора и настройку кольца
        char_index = self.alphabet.index(char)
        effective_index = (char_index + self.alphabet.index(position) - ring_setting) % len(self.alphabet)

        if forward:
            # Прямое прохождение
            result_char = rotor[effective_index]
            # Компенсируем сдвиг
            result_index = (self.alphabet.index(result_char) - self.alphabet.index(position) + ring_setting) % len(
                self.alphabet)
        else:
            # Обратное прохождение
            rotor_index = rotor.index(char)
            effective_rotor_index = (rotor_index + self.alphabet.index(position) - ring_setting) % len(self.alphabet)
            result_char = self.alphabet[effective_rotor_index]
            # Компенсируем сдвиг
            result_index = (self.alphabet.index(result_char) - self.alphabet.index(position) + ring_setting) % len(
                self.alphabet)

        return self.alphabet[result_index % len(self.alphabet)]

    def encrypt_char(self, char):
        """Шифрование одного символа"""
        if char.upper() not in self.alphabet:
            return char

        uppercase_char = char.upper()

        # Вращаем роторы
        self._rotate_rotors()

        current_char = uppercase_char

        # Прямой проход через роторы (правый → средний → левый)
        for i in [2, 1, 0]:
            current_char = self._process_through_rotor(current_char, i, forward=True)

        # Проход через рефлектор
        reflector_index = self.alphabet.index(current_char)
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

    def reset(self):
        """Сброс позиций роторов к начальным"""
        self.current_pos = self.rotor_pos.copy()


# Пример использования
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
    enigma = Enigma(rotor_order, rotor_positions, ring_settings)
    enigma.reflector = reflector
    return enigma.encrypt(text)