"""NetWatch localization — RU / EU (English)."""

from __future__ import annotations

from typing import Any

Lang = str  # "ru" | "eu"

_current: Lang = "ru"

COLUMN_IDS = ("protocol", "local", "remote", "state", "pid", "process")
COLUMN_WIDTHS = {
    "protocol": 80,
    "local": 150,
    "remote": 150,
    "state": 110,
    "pid": 70,
    "process": 180,
}

STRINGS: dict[Lang, dict[str, str]] = {
    "ru": {
        "app_title": "NetWatch",
        "brand": "NETWATCH",
        "all_ports": "ВСЕ ПОРТЫ",
        "port_label": "ПОРТ",
        "scan": "НАЙТИ",
        "all": "ВСЕ",
        "refresh": "ОБНОВИТЬ",
        "live": "ОНЛАЙН · 3 сек",
        "quick_ports": "БЫСТРЫЙ ВЫБОР",
        "connections": "ПОДКЛЮЧЕНИЯ",
        "kill_selected": "◆  ЗАВЕРШИТЬ ВЫБРАННЫЙ",
        "kill_all": "◆  ЗАВЕРШИТЬ ВСЕ НА ПОРТУ",
        "hint_time_wait": "TIME_WAIT · PID 0 — не завершается",
        "status": "СТАТУС",
        "ready": "ГОТОВО",
        "updating": "Обновление…",
        "error": "Ошибка",
        "done": "Готово",
        "result": "Результат",
        "selection": "Выбор",
        "no_access": "Нет доступа",
        "port": "Порт",
        "col_protocol": "ПРОТОКОЛ",
        "col_local": "ЛОКАЛЬНЫЙ",
        "col_remote": "УДАЛЁННЫЙ",
        "col_state": "СОСТОЯНИЕ",
        "col_pid": "PID",
        "col_process": "ПРОЦЕСС",
        "port_named": "ПОРТ :{port}",
        "stats": "{n} подключений · {pids} уник. PID",
        "invalid_port": "Введите корректный номер порта (1–65535).",
        "port_range": "Порт должен быть от 1 до 65535.",
        "access_denied": "Не удалось получить все подключения.\nЗапустите программу от имени администратора.",
        "refresh_failed": "Не удалось обновить список:\n{error}",
        "select_row": "Выберите соединение в списке.",
        "pid0_title": "PID 0",
        "pid0_msg": "TIME_WAIT / системное соединение — процесс завершить нельзя.",
        "kill_title": "Завершить процесс",
        "kill_confirm": "Завершить {name}\nPID {pid}?",
        "need_port": "Укажите номер порта для завершения всех сессий.",
        "no_pids": "На порту {port} нет процессов для завершения.",
        "kill_all_title": "Завершить все",
        "kill_all_confirm": "Порт {port}\nPID: {pids}\n\nTIME_WAIT (PID 0) закроется сам.",
        "killed_count": "Завершено: {n}\n\n{details}",
        "cancel": "ОТМЕНА",
        "confirm": "ПОДТВЕРДИТЬ",
        "ok": "ОК",
        "no_access_name": "<нет доступа>",
        "kill_pid0": "Нельзя завершить системное соединение (PID 0).",
        "killed": "Процесс {name} (PID {pid}) завершён.",
        "already_gone": "Процесс PID {pid} уже не существует.",
        "kill_denied": "Нет прав для завершения PID {pid}. Запустите от администратора.",
        "no_active": "Нет активных процессов для этого порта.",
        "state_LISTENING": "СЛУШАЕТ",
        "state_ESTABLISHED": "АКТИВНО",
        "state_TIME_WAIT": "TIME_WAIT",
        "state_CLOSE_WAIT": "ЗАКРЫТИЕ",
        "state_FIN_WAIT_1": "FIN_WAIT_1",
        "state_FIN_WAIT_2": "ЗАВЕРШЕНИЕ",
        "state_SYN_SENT": "SYN_SENT",
        "state_SYN_RECEIVED": "SYN_RECV",
        "state_CLOSE": "ЗАКРЫТО",
        "state_LAST_ACK": "LAST_ACK",
        "state_CLOSING": "ЗАКРЫТИЕ",
        "state_NONE": "—",
    },
    "eu": {
        "app_title": "NetWatch",
        "brand": "NETWATCH",
        "all_ports": "ALL PORTS",
        "port_label": "PORT",
        "scan": "SCAN",
        "all": "ALL",
        "refresh": "REFRESH",
        "live": "LIVE · 3s",
        "quick_ports": "QUICK PORTS",
        "connections": "CONNECTIONS",
        "kill_selected": "◆  KILL SELECTED",
        "kill_all": "◆  TERMINATE ALL ON PORT",
        "hint_time_wait": "TIME_WAIT · PID 0 — cannot terminate",
        "status": "STATUS",
        "ready": "READY",
        "updating": "Updating…",
        "error": "Error",
        "done": "Done",
        "result": "Result",
        "selection": "Selection",
        "no_access": "Access denied",
        "port": "Port",
        "col_protocol": "PROTOCOL",
        "col_local": "LOCAL",
        "col_remote": "REMOTE",
        "col_state": "STATE",
        "col_pid": "PID",
        "col_process": "PROCESS",
        "port_named": "PORT :{port}",
        "stats": "{n} connections · {pids} unique PID",
        "invalid_port": "Enter a valid port number (1–65535).",
        "port_range": "Port must be between 1 and 65535.",
        "access_denied": "Could not list all connections.\nRun as administrator for full access.",
        "refresh_failed": "Failed to refresh list:\n{error}",
        "select_row": "Select a connection in the list.",
        "pid0_title": "PID 0",
        "pid0_msg": "TIME_WAIT / system socket — cannot kill a process.",
        "kill_title": "Kill process",
        "kill_confirm": "Terminate {name}\nPID {pid}?",
        "need_port": "Specify a port to terminate all sessions.",
        "no_pids": "No processes to terminate on port {port}.",
        "kill_all_title": "Terminate all",
        "kill_all_confirm": "Port {port}\nPID: {pids}\n\nTIME_WAIT (PID 0) will clear on its own.",
        "killed_count": "Terminated: {n}\n\n{details}",
        "cancel": "CANCEL",
        "confirm": "CONFIRM",
        "ok": "OK",
        "no_access_name": "<no access>",
        "kill_pid0": "Cannot terminate system connection (PID 0).",
        "killed": "Process {name} (PID {pid}) terminated.",
        "already_gone": "Process PID {pid} no longer exists.",
        "kill_denied": "Access denied for PID {pid}. Run as administrator.",
        "no_active": "No active processes for this port.",
        "state_LISTENING": "LISTEN",
        "state_ESTABLISHED": "ESTABLISHED",
        "state_TIME_WAIT": "TIME_WAIT",
        "state_CLOSE_WAIT": "CLOSE_WAIT",
        "state_FIN_WAIT_1": "FIN_WAIT_1",
        "state_FIN_WAIT_2": "FIN_WAIT_2",
        "state_SYN_SENT": "SYN_SENT",
        "state_SYN_RECEIVED": "SYN_RECV",
        "state_CLOSE": "CLOSE",
        "state_LAST_ACK": "LAST_ACK",
        "state_CLOSING": "CLOSING",
        "state_NONE": "—",
    },
}


def get_lang() -> Lang:
    return _current


def set_lang(lang: Lang) -> None:
    global _current
    if lang not in STRINGS:
        raise ValueError(lang)
    _current = lang


def toggle_lang() -> Lang:
    set_lang("eu" if _current == "ru" else "ru")
    return _current


def t(key: str, **kwargs: Any) -> str:
    table = STRINGS.get(_current) or STRINGS["ru"]
    text = table.get(key) or STRINGS["ru"].get(key, key)
    if kwargs:
        return text.format(**kwargs)
    return text


def state_label(state: str) -> str:
    key = f"state_{state}"
    table = STRINGS.get(_current) or STRINGS["ru"]
    return table.get(key, state)


def column_title(col_id: str) -> str:
    return t(f"col_{col_id}")


def tree_columns() -> tuple[tuple[str, str, int], ...]:
    return tuple((cid, column_title(cid), COLUMN_WIDTHS[cid]) for cid in COLUMN_IDS)
