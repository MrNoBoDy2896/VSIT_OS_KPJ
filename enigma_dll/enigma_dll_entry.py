# enigma_dll_entry.py
import ctypes
import json
from enigma_core import enigma_encrypt, enigma_decrypt


# Экспортируемые функции
def encrypt_wrapper(text_ptr, rotor_order_ptr=None, rotor_positions_ptr=None,
                    ring_settings_ptr=None, reflector_ptr='B'):
    """Обертка для шифрования"""
    try:
        # Конвертируем из C строк
        text = ctypes.c_char_p(text_ptr).value.decode('utf-8') if text_ptr else ""

        # Конвертируем настройки
        rotor_order = None
        if rotor_order_ptr:
            rotor_order = json.loads(ctypes.c_char_p(rotor_order_ptr).value.decode('utf-8'))

        rotor_positions = None
        if rotor_positions_ptr:
            rotor_positions = json.loads(ctypes.c_char_p(rotor_positions_ptr).value.decode('utf-8'))

        ring_settings = None
        if ring_settings_ptr:
            ring_settings = json.loads(ctypes.c_char_p(ring_settings_ptr).value.decode('utf-8'))

        reflector = 'B'
        if reflector_ptr:
            reflector = ctypes.c_char_p(reflector_ptr).value.decode('utf-8')

        # Выполняем шифрование
        result = enigma_encrypt(text, rotor_order, rotor_positions, ring_settings, reflector)

        # Возвращаем как C строку (нужно освободить в вызывающем коде)
        return ctypes.c_char_p(result.encode('utf-8'))
    except Exception as e:
        error_msg = f"Error: {str(e)}".encode('utf-8')
        return ctypes.c_char_p(error_msg)


def decrypt_wrapper(text_ptr, rotor_order_ptr=None, rotor_positions_ptr=None,
                    ring_settings_ptr=None, reflector_ptr='B'):
    """Обертка для дешифрования (использует ту же функцию)"""
    return encrypt_wrapper(text_ptr, rotor_order_ptr, rotor_positions_ptr,
                           ring_settings_ptr, reflector_ptr)


def initialize():
    """Инициализация DLL"""
    return 1


def shutdown():
    """Завершение работы DLL"""
    return 1


# Экспортируемые символы для ctypes
__all__ = ['encrypt_wrapper', 'decrypt_wrapper', 'initialize', 'shutdown']

if __name__ == "__main__":
    # Тестирование
    test_text = "ПРИВЕТ"
    result = encrypt_wrapper(test_text.encode('utf-8'))
    print(f"Test: {test_text} -> {result.value.decode('utf-8')}")