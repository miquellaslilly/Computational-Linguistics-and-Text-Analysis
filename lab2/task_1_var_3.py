# -*- coding: utf-8 -*-
"""
Лабораторная работа №2. Задание 1.
Вариант 3: поиск корректных URI адресов в тексте.

Поддерживаемые протоколы:
    http, https (RFC 7230)
    ftp        (RFC 3986)
    sftp, ssh, smb (draft)

Стандарт URI: RFC 3986
"""

import re

# ============================================================
# РЕГУЛЯРНОЕ ВЫРАЖЕНИЕ ДЛЯ ПОИСКА КОРРЕКТНЫХ URI
# ============================================================
URI_REGEX = re.compile(r"""
    (?<![A-Za-z0-9])
    (?:
        https?  |  ftp  |  sftp  |  ssh  |  smb
    )
    ://
    (?:
        (?:[A-Za-z0-9\-._~!$&'()*+,;=:]|%[0-9A-Fa-f]{2})+@
    )?
    (?:
        (?:\d{1,3}\.){3}\d{1,3}
        |
        \[[0-9A-Fa-f:.]+\]
        |
        (?:
            (?:[A-Za-z0-9](?:[A-Za-z0-9\-]*[A-Za-z0-9])?\.)+
            [A-Za-z0-9](?:[A-Za-z0-9\-]*[A-Za-z0-9])?
        )
    )
    (?::\d{1,5})?
    (?:[/?#][A-Za-z0-9\-._~!$&'()*+,;=:@%/?\#]*)?
    (?![A-Za-z0-9\-._~!$&'()*+,;=:@%/?])
""", re.VERBOSE)


def find_uris(text: str) -> list[str]:
    """Находит все корректные URI в тексте."""
    return [m.group(0) for m in URI_REGEX.finditer(text)]


def highlight_uris(text: str, color: str = "\033[42m\033[30m") -> str:
    """Подсвечивает найденные URI зелёным фоном."""
    RESET = "\033[0m"
    result, last_end = [], 0
    for match in URI_REGEX.finditer(text):
        start, end = match.span()
        result.append(text[last_end:start])
        result.append(color + text[start:end] + RESET)
        last_end = end
    result.append(text[last_end:])
    return "".join(result)


# ============================================================
# ТЕСТИРОВАНИЕ
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("ЗАДАНИЕ 1. Поиск корректных URI (вариант 3)")
    print("=" * 60)

    test_text = """
    Корректные URI:
    http://example.com
    https://ex.com/articles/page1?v=2&s=ex
    http://127.0.0.1:1235
    ftp://example.com/files/example.txt
    http://xn--fsqu00a.xn--3lr804guic/
    ssh://login@server.com:1234/repository.git
    smb://192.168.1.7/USERS/
    ftp://ftp.example.com/path/

    Некорректные URI (НЕ должны попасть в результат):
    hhttp://example.com
    http//example.com
    C:/Users/User/example.com
    /home/user/example.com
    """

    print("--- Исходный текст ---")
    print(test_text)

    print("\n--- Текст с подсветкой корректных URI ---")
    print(highlight_uris(test_text))

    print("\n--- Список найденных URI ---")
    uris = find_uris(test_text)
    for i, uri in enumerate(uris, 1):
        print(f"{i:2}. {uri}")
    print(f"\nВсего найдено: {len(uris)}")