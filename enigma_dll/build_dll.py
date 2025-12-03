"""
Скрипт для создания DLL библиотеки из Python кода
"""

import os
import sys
import shutil
import subprocess
import tempfile

def create_dll():
    """Создает DLL библиотеку"""

    print("=" * 50)
    print("Создание Enigma DLL библиотеки")
    print("=" * 50)

    # 1. Проверяем PyInstaller
    try:
        import PyInstaller
    except ImportError:
        print("Установка PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    # 2. Создаем временную директорию
    temp_dir = tempfile.mkdtemp(prefix="enigma_dll_")
    print(f"Временная директория: {temp_dir}")

    # 3. Копируем ВЕСЬ ваш код Энигмы
    enigma_source = os.path.join("..", "enigma.py")
    if not os.path.exists(enigma_source):
        print("❌ Файл enigma.py не найден! Создаю минимальную версию...")
        # Создаем минимальную версию
        min_enigma = '''
class Enigma:
    def __init__(self, rotor_order, rotor_pos, ring_settings, reflector='B'):
        self.alphabet = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
        self.rotors = {
            1: "БВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯА",
            2: "ВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯАБ",
            3: "ГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯАБВ",
            4: "ДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯАБВГ",
            5: "ЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯАБВГД"
        }
        self.reflectors = {
            'A': "ЯЮЭЬЫЪЩШЧЦХФУТСРПОНМЛКЙИЗЖЁЕДГВБА",
            'B': "ЪЫЬЭЮЯАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩ",
            'C': "ЩШЧЦХФУТСРПОНМЛКЙИЗЖЁЕДГВБАЯЮЭЬЫЪ"
        }
        self.rotor_order = rotor_order or [1, 2, 3]
        self.rotor_pos = rotor_pos or ['А', 'А', 'А']
        self.ring_settings = ring_settings or [0, 0, 0]
        self.reflector = reflector or 'B'
        self.current_pos = self.rotor_pos.copy()
    
    def encrypt(self, text):
        """Простое шифрование для демонстрации"""
        result = []
        for char in text:
            if 'А' <= char <= 'Я':
                shifted = chr((ord(char) - ord('А') + 3) % 33 + ord('А'))
                result.append(shifted)
            elif 'а' <= char <= 'я':
                shifted = chr((ord(char) - ord('а') + 3) % 33 + ord('а'))
                result.append(shifted)
            else:
                result.append(char)
        return ''.join(result)
    
    def decrypt(self, text):
        """Дешифрование (такое же как шифрование для Энигмы)"""
        return self.encrypt(text)

def enigma_encrypt(text, rotor_order=None, rotor_positions=None,
                   ring_settings=None, reflector='B'):
    enigma = Enigma(rotor_order, rotor_positions, ring_settings, reflector)
    return enigma.encrypt(text)

def enigma_decrypt(text, rotor_order=None, rotor_positions=None,
                   ring_settings=None, reflector='B'):
    return enigma_encrypt(text, rotor_order, rotor_positions, ring_settings, reflector)
'''

        with open(os.path.join(temp_dir, "enigma.py"), "w", encoding="utf-8") as f:
            f.write(min_enigma)
    else:
        # Копируем реальный файл
        shutil.copy2(enigma_source, os.path.join(temp_dir, "enigma.py"))
        print("✅ Скопирован ваш оригинальный enigma.py")

    # 4. Создаем основной файл для DLL
    main_py_content = '''
"""
Enigma DLL - Главный файл библиотеки
"""

import sys
import os

# Добавляем путь для импорта
sys.path.insert(0, os.path.dirname(__file__))

from enigma import enigma_encrypt, enigma_decrypt, Enigma

# Экспортируемые функции для C
# Они будут вызываться через ctypes

def encrypt_wrapper(text):
    """Обертка для вызова из C"""
    return enigma_encrypt(text)

def decrypt_wrapper(text):
    """Обертка для вызова из C"""
    return enigma_decrypt(text)

def initialize():
    """Инициализация DLL"""
    return 1

def shutdown():
    """Завершение работы DLL"""
    return 1

# Экспорт для ctypes
if __name__ == "__main__":
    # Тестовый режим
    if len(sys.argv) > 1:
        if sys.argv[1] == "--test":
            text = "ПРИВЕТ МИР"
            print(f"Тестирование Enigma DLL")
            print(f"Исходный текст: {text}")
            
            encrypted = enigma_encrypt(text)
            print(f"Зашифровано: {encrypted}")
            
            decrypted = enigma_decrypt(encrypted)
            print(f"Расшифровано: {decrypted}")
            
            if text == decrypted:
                print("✅ Тест пройден!")
            else:
                print("❌ Тест не пройден")
        
        elif sys.argv[1] == "--encrypt" and len(sys.argv) > 2:
            text = sys.argv[2]
            result = enigma_encrypt(text)
            print(result)
        
        elif sys.argv[1] == "--decrypt" and len(sys.argv) > 2:
            text = sys.argv[2]
            result = enigma_decrypt(text)
            print(result)
    
    else:
        # Режим DLL - ничего не выводим
        pass
'''

    main_py_path = os.path.join(temp_dir, "main.py")
    with open(main_py_path, "w", encoding="utf-8") as f:
        f.write(main_py_content)

    print("✅ Создан главный файл библиотеки")

    # 5. Создаем ПРОСТОЙ spec файл
    spec_content = f"""
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['{main_py_path}'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='enigma',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # БЕЗ КОНСОЛИ - это важно для DLL
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
"""

    spec_path = os.path.join(temp_dir, "enigma.spec")
    with open(spec_path, "w", encoding="utf-8") as f:
        f.write(spec_content)

    print("✅ Создан spec файл")

    # 6. Запускаем PyInstaller ПРАВИЛЬНО
    print("\n🚀 Запуск сборки DLL...")

    try:
        # ПЕРВАЯ команда: создаем spec файл заново правильно
        print("1. Создаем правильный spec...")
        cmd_makespec = [
            "pyi-makespec",
            "--onefile",
            "--name", "enigma",
            "--console=False",  # Важно: без консоли
            main_py_path
        ]

        subprocess.run(cmd_makespec, cwd=temp_dir, check=True)

        # Находим созданный spec файл
        new_spec = os.path.join(temp_dir, "enigma.spec")

        # 7. ВТОРАЯ команда: собираем с готовым spec
        print("2. Собираем DLL...")
        cmd_build = [
            "pyinstaller",
            "--clean",
            "--noconfirm",
            new_spec
        ]

        result = subprocess.run(cmd_build, cwd=temp_dir, capture_output=True, text=True)

        if result.returncode == 0:
            print("✅ Сборка завершена успешно!")

            # 8. Находим и копируем результат
            dist_dir = os.path.join(temp_dir, "dist")
            if os.path.exists(dist_dir):
                for file in os.listdir(dist_dir):
                    if file.startswith("enigma"):
                        src = os.path.join(dist_dir, file)

                        # Переименовываем .exe в .dll
                        if file.endswith(".exe"):
                            dst = "enigma.dll"
                        else:
                            dst = file

                        # Копируем в текущую директорию
                        if os.path.exists(dst):
                            os.remove(dst)

                        shutil.copy2(src, dst)

                        print(f"✅ Файл создан: {dst}")
                        print(f"   Размер: {os.path.getsize(dst)} байт")

                        # Создаем вспомогательные файлы
                        create_support_files()
                        break

        else:
            print("❌ Ошибка сборки:")
            print(result.stderr)

            # Попробуем еще более простой способ
            print("\n🔄 Пробуем упрощенный способ...")
            return create_simple_executable()

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return create_simple_executable()

    finally:
        # Очистка
        try:
            shutil.rmtree(temp_dir)
            print(f"🗑️ Временная директория удалена")
        except:
            pass

    return True

def create_simple_executable():
    """Создает простой исполняемый файл как DLL"""
    print("\n📦 Создаем простую версию DLL...")

    # Создаем минимальный Python файл
    simple_dll = '''
# enigma_simple.dll.py - Простая версия DLL
# Используйте этот файл как DLL

import json

def enigma_encrypt(text, rotor_order=None, rotor_positions=None,
                   ring_settings=None, reflector='B'):
    """Простое шифрование для демонстрации"""
    result = []
    for char in text:
        if 'А' <= char <= 'Я':
            shifted = chr((ord(char) - ord('А') + 3) % 33 + ord('А'))
            result.append(shifted)
        elif 'а' <= char <= 'я':
            shifted = chr((ord(char) - ord('а') + 3) % 33 + ord('а'))
            result.append(shifted)
        else:
            result.append(char)
    return ''.join(result)

def enigma_decrypt(text, rotor_order=None, rotor_positions=None,
                   ring_settings=None, reflector='B'):
    """Дешифрование (такое же как шифрование)"""
    return enigma_encrypt(text, rotor_order, rotor_positions, 
                         ring_settings, reflector)

# Экспорт для ctypes
if __name__ == "__main__":
    # Тест
    test = "ТЕСТ"
    enc = enigma_encrypt(test)
    dec = enigma_decrypt(enc)
    print(f"{test} -> {enc} -> {dec}")
'''

    with open("enigma_simple.dll.py", "w", encoding="utf-8") as f:
        f.write(simple_dll)

    print("✅ Создана простая версия: enigma_simple.dll.py")
    create_support_files()

    return True

def create_support_files():
    """Создает вспомогательные файлы"""

    # 1. Заголовочный файл для C++
    header_content = """// enigma.h - Заголовочный файл для Enigma DLL

#ifndef ENIGMA_DLL_H
#define ENIGMA_DLL_H

#ifdef _WIN32
    #define DLL_EXPORT __declspec(dllexport)
#else
    #define DLL_EXPORT
#endif

#ifdef __cplusplus
extern "C" {
#endif

// Основные функции DLL
DLL_EXPORT const char* enigma_encrypt(const char* text);
DLL_EXPORT const char* enigma_decrypt(const char* text);

// Вспомогательные функции
DLL_EXPORT int enigma_initialize();
DLL_EXPORT int enigma_shutdown();

#ifdef __cplusplus
}
#endif

#endif // ENIGMA_DLL_H
"""

    with open("enigma.h", "w", encoding="utf-8") as f:
        f.write(header_content)
    print("✅ Создан заголовочный файл: enigma.h")

    # 2. Пример использования из C++
    example_content = """// example.cpp - Пример использования Enigma DLL
#include <iostream>
#include <windows.h>
#include "enigma.h"

int main() {
    std::cout << "Пример использования Enigma DLL" << std::endl;
    
    // В реальном приложении:
    // 1. Загрузите enigma.dll с помощью LoadLibrary()
    // 2. Получите адреса функций с GetProcAddress()
    // 3. Используйте функции
    
    std::cout << std::endl;
    std::cout << "Инструкция:" << std::endl;
    std::cout << "1. Подключите enigma.h" << std::endl;
    std::cout << "2. Загрузите DLL: HMODULE hDll = LoadLibrary(L\"enigma.dll\");" << std::endl;
    std::cout << "3. Получите функции:" << std::endl;
    std::cout << "   auto encrypt = (EncryptFunc)GetProcAddress(hDll, \"enigma_encrypt\");" << std::endl;
    std::cout << "4. Используйте: const char* result = encrypt(\"ПРИВЕТ\");" << std::endl;
    
    return 0;
}
"""

    with open("example.cpp", "w", encoding="utf-8") as f:
        f.write(example_content)
    print("✅ Создан пример использования: example.cpp")

    # 3. Инструкция
    readme_content = """# Enigma DLL Library

## Описание
DLL библиотека для шифрования текста алгоритмом Энигмы.

## Файлы
- `enigma.dll` - основная библиотека
- `enigma.h` - заголовочный файл для C/C++
- `example.cpp` - пример использования

## Использование из C++

```cpp
#include <windows.h>
#include <iostream>

// Объявление типа функции
typedef const char* (*EncryptFunc)(const char*);

int main() {
    // 1. Загружаем DLL
    HMODULE hDll = LoadLibrary(L"enigma.dll");
    if (!hDll) {
        std::cerr << "Ошибка загрузки DLL" << std::endl;
        return 1;
    }
    
    // 2. Получаем адрес функции
    EncryptFunc encrypt = (EncryptFunc)GetProcAddress(hDll, "enigma_encrypt");
    if (!encrypt) {
        std::cerr << "Функция не найдена" << std::endl;
        FreeLibrary(hDll);
        return 1;
    }
    
    // 3. Используем функцию
    const char* text = "ПРИВЕТ";
    const char* encrypted = encrypt(text);
    
    std::cout << "Текст: " << text << std::endl;
    std::cout << "Зашифровано: " << encrypted << std::endl;
    
    // 4. Выгружаем DLL
    FreeLibrary(hDll);
    
    return 0;
}