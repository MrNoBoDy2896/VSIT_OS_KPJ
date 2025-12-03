"""
Экспортируемые функции DLL
"""

import sys
import json
from enigma_core import encrypt, decrypt

# Глобальные переменные
_dll_initialized = False


def enigma_initialize():
    """Инициализация DLL"""
    global _dll_initialized
    _dll_initialized = True
    return 1  # Успех


def enigma_shutdown():
    """Завершение работы DLL"""
    global _dll_initialized
    _dll_initialized = False
    return 1  # Успех


def enigma_encrypt(text, rotor_order=None, rotor_positions=None,
                   ring_settings=None, reflector='B'):
    """Шифрование текста - для экспорта в C"""
    if not _dll_initialized:
        return None

    # Конвертируем строки JSON в Python объекты
    rotor_order_list = None
    if rotor_order:
        try:
            rotor_order_list = json.loads(rotor_order)
        except:
            rotor_order_list = [1, 2, 3]

    rotor_positions_list = None
    if rotor_positions:
        try:
            rotor_positions_list = json.loads(rotor_positions)
        except:
            rotor_positions_list = ['А', 'А', 'А']

    ring_settings_list = None
    if ring_settings:
        try:
            ring_settings_list = json.loads(ring_settings)
        except:
            ring_settings_list = [0, 0, 0]

    # Выполняем шифрование
    result = encrypt(
        text,
        rotor_order_list,
        rotor_positions_list,
        ring_settings_list,
        reflector
    )

    # Возвращаем как строку C (нужно освободить с free())
    return result


def enigma_decrypt(text, rotor_order=None, rotor_positions=None,
                   ring_settings=None, reflector='B'):
    """Дешифрование текста - для экспорта в C"""
    # Дешифрование такое же как шифрование
    return enigma_encrypt(text, rotor_order, rotor_positions,
                          ring_settings, reflector)


# Точка входа для PyInstaller
def main():
    """Точка входа - для совместимости с PyInstaller"""
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        # Тестовый режим
        print("Enigma DLL Test Mode")
        print("=" * 30)

        test_text = "ПРИВЕТ"
        encrypted = encrypt(test_text)
        decrypted = decrypt(encrypted)

        print(f"Original: {test_text}")
        print(f"Encrypted: {encrypted}")
        print(f"Decrypted: {decrypted}")

        if test_text == decrypted:
            print("✓ Test PASSED")
        else:
            print("✗ Test FAILED")

    else:
        print("Enigma DLL Library")
        print("Use from C/C++ with: enigma_encrypt() and enigma_decrypt()")


if __name__ == "__main__":
    main()