// enigma.h - Заголовочный файл для Enigma DLL
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
