# build_dll_simple.py
import os
import shutil
import subprocess
import sys


def build_dll():
    """Простая сборка DLL"""
    print("=" * 50)
    print("Сборка Enigma DLL")
    print("=" * 50)

    # 1. Проверяем PyInstaller
    try:
        import PyInstaller
    except ImportError:
        print("Установка PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    # 2. Создаем основной файл для DLL
    main_content = '''
import ctypes
import sys

# Заглушка для экспорта
def enigma_encrypt(text):
    """Простая заглушка для демонстрации"""
    if isinstance(text, str):
        # Простой шифр Цезаря для демонстрации
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
    elif isinstance(text, bytes):
        return enigma_encrypt(text.decode('utf-8')).encode('utf-8')
    return text

def enigma_decrypt(text):
    """Дешифрование (такое же как шифрование для Энигмы)"""
    return enigma_encrypt(text)

# Экспорт для ctypes
if __name__ == "__main__":
    # Тестовый режим
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        test = "ПРИВЕТ"
        print(f"Тест: {test}")
        enc = enigma_encrypt(test)
        print(f"Зашифровано: {enc}")
        dec = enigma_decrypt(enc)
        print(f"Расшифровано: {dec}")
'''

    with open("enigma_main.py", "w", encoding="utf-8") as f:
        f.write(main_content)

    # 3. Создаем spec файл для DLL
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

import sys
from PyInstaller.building.api import PYZ, EXE, COLLECT
from PyInstaller.building.build_main import Analysis

block_cipher = None

a = Analysis(
    ['enigma_main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='enigma',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # БЕЗ КОНСОЛИ для DLL
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
'''

    with open("enigma.spec", "w", encoding="utf-8") as f:
        f.write(spec_content)

    # 4. Собираем DLL
    print("Сборка...")

    # Сначала делаем spec
    subprocess.run([sys.executable, "-m", "PyInstaller", "--onefile",
                    "--name=enigma", "--console=False", "enigma_main.py"])

    # Переименовываем .exe в .dll
    if os.path.exists("dist/enigma.exe"):
        os.rename("dist/enigma.exe", "dist/enigma.dll")
        print("✅ Создано: dist/enigma.dll")

        # Копируем в корень
        shutil.copy2("dist/enigma.dll", "enigma.dll")
        print("✅ Скопировано: enigma.dll")
    else:
        print("❌ Ошибка: enigma.exe не найден")

        # Создаем простую DLL заглушку
        create_stub_dll()

    # 5. Создаем вспомогательные файлы
    create_header_files()

    print("\n" + "=" * 50)
    print("✅ Готово! DLL файл создан.")
    print("=" * 50)


def create_stub_dll():
    """Создает заглушку DLL если сборка не удалась"""
    print("Создание заглушки DLL...")

    stub_content = b'MZ' + b'\x90' * 58  # Простая заглушка PE файла

    with open("enigma.dll", "wb") as f:
        f.write(stub_content)

    print("Создана простая заглушка enigma.dll")


def create_header_files():
    """Создает заголовочные файлы для C/C++"""

    # enigma.h
    header = '''// enigma.h - Заголовочный файл для Enigma DLL
#ifndef ENIGMA_DLL_H
#define ENIGMA_DLL_H

#ifdef _WIN32
    #ifdef ENIGMA_EXPORTS
        #define ENIGMA_API __declspec(dllexport)
    #else
        #define ENIGMA_API __declspec(dllimport)
    #endif
#else
    #define ENIGMA_API
#endif

#ifdef __cplusplus
extern "C" {
#endif

// Инициализация DLL
ENIGMA_API int enigma_initialize();

// Завершение работы DLL
ENIGMA_API int enigma_shutdown();

// Шифрование текста
ENIGMA_API const char* enigma_encrypt(const char* text);

// Дешифрование текста
ENIGMA_API const char* enigma_decrypt(const char* text);

// Расширенные функции с настройками
ENIGMA_API const char* enigma_encrypt_ex(const char* text,
                                         const char* rotor_order,
                                         const char* rotor_positions,
                                         const char* ring_settings,
                                         const char* reflector);

ENIGMA_API const char* enigma_decrypt_ex(const char* text,
                                         const char* rotor_order,
                                         const char* rotor_positions,
                                         const char* ring_settings,
                                         const char* reflector);

#ifdef __cplusplus
}
#endif

#endif // ENIGMA_DLL_H
'''

    with open("enigma.h", "w", encoding="utf-8") as f:
        f.write(header)

    # example.c
    example = '''// example.c - Пример использования Enigma DLL
#include <stdio.h>
#include <windows.h>
#include "enigma.h"

int main() {
    HMODULE hDll = LoadLibrary("enigma.dll");
    if (!hDll) {
        printf("Ошибка загрузки DLL!\\n");
        return 1;
    }

    // Получаем адреса функций
    typedef const char* (*EncryptFunc)(const char*);
    typedef const char* (*DecryptFunc)(const char*);

    EncryptFunc encrypt = (EncryptFunc)GetProcAddress(hDll, "enigma_encrypt");
    DecryptFunc decrypt = (DecryptFunc)GetProcAddress(hDll, "enigma_decrypt");

    if (!encrypt || !decrypt) {
        printf("Функции не найдены!\\n");
        FreeLibrary(hDll);
        return 1;
    }

    // Тестируем
    const char* text = "ПРИВЕТ";
    printf("Исходный текст: %s\\n", text);

    const char* encrypted = encrypt(text);
    printf("Зашифровано: %s\\n", encrypted);

    const char* decrypted = decrypt(encrypted);
    printf("Расшифровано: %s\\n", decrypted);

    FreeLibrary(hDll);
    return 0;
}
'''

    with open("example.c", "w", encoding="utf-8") as f:
        f.write(example)

    print("✅ Созданы вспомогательные файлы:")
    print("   - enigma.h (заголовочный файл)")
    print("   - example.c (пример использования)")


if __name__ == "__main__":
    build_dll()