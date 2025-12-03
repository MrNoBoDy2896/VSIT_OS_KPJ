// example.c - Пример использования Enigma DLL
#include <stdio.h>
#include <windows.h>
#include "enigma.h"

int main() {
    HMODULE hDll = LoadLibrary("enigma.dll");
    if (!hDll) {
        printf("Ошибка загрузки DLL!\n");
        return 1;
    }

    // Получаем адреса функций
    typedef const char* (*EncryptFunc)(const char*);
    typedef const char* (*DecryptFunc)(const char*);

    EncryptFunc encrypt = (EncryptFunc)GetProcAddress(hDll, "enigma_encrypt");
    DecryptFunc decrypt = (DecryptFunc)GetProcAddress(hDll, "enigma_decrypt");

    if (!encrypt || !decrypt) {
        printf("Функции не найдены!\n");
        FreeLibrary(hDll);
        return 1;
    }

    // Тестируем
    const char* text = "ПРИВЕТ";
    printf("Исходный текст: %s\n", text);

    const char* encrypted = encrypt(text);
    printf("Зашифровано: %s\n", encrypted);

    const char* decrypted = decrypt(encrypted);
    printf("Расшифровано: %s\n", decrypted);

    FreeLibrary(hDll);
    return 0;
}
