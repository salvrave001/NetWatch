"""Сбор сетевых подключений и управление процессами."""

from __future__ import annotations

import psutil
from dataclasses import dataclass

from process_checker.i18n import t


@dataclass(frozen=True, slots=True)
class ConnectionRow:
    protocol: str
    local_addr: str
    remote_addr: str
    state: str
    pid: int
    process_name: str


_name_cache: dict[int, str] = {}


def _format_addr(addr) -> str:
    if not addr:
        return "*:*"
    ip, port = addr
    if ip in ("0.0.0.0", "::", ""):
        ip = "*"
    return f"{ip}:{port}"


def _process_name(pid: int) -> str:
    if pid <= 0:
        return "—"
    cached = _name_cache.get(pid)
    if cached is not None:
        return cached
    try:
        name = psutil.Process(pid).name()
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        return t("no_access_name")
    _name_cache[pid] = name
    return name


def collect_connections(port_filter: int | None = None) -> list[ConnectionRow]:
    rows: list[ConnectionRow] = []
    for conn in psutil.net_connections(kind="inet"):
        laddr = conn.laddr
        raddr = conn.raddr

        if port_filter is not None:
            local_port = laddr.port if laddr else None
            remote_port = raddr.port if raddr else None
            if local_port != port_filter and remote_port != port_filter:
                continue

        pid = conn.pid if conn.pid is not None else 0
        rows.append(
            ConnectionRow(
                protocol="TCP" if conn.type.name == "SOCK_STREAM" else "UDP",
                local_addr=_format_addr(laddr),
                remote_addr=_format_addr(raddr),
                state=conn.status if conn.status else "—",
                pid=pid,
                process_name=_process_name(pid),
            )
        )
    return rows


def pids_for_port(port: int) -> set[int]:
    pids: set[int] = set()
    for conn in psutil.net_connections(kind="inet"):
        laddr = conn.laddr
        raddr = conn.raddr
        local_port = laddr.port if laddr else None
        remote_port = raddr.port if raddr else None
        if local_port == port or remote_port == port:
            if conn.pid and conn.pid > 0:
                pids.add(conn.pid)
    return pids


def kill_process(pid: int) -> tuple[bool, str]:
    if pid <= 0:
        return False, t("kill_pid0")

    try:
        proc = psutil.Process(pid)
        name = proc.name()
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except psutil.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=3)
        _name_cache.pop(pid, None)
        return True, t("killed", name=name, pid=pid)
    except psutil.NoSuchProcess:
        _name_cache.pop(pid, None)
        return True, t("already_gone", pid=pid)
    except psutil.AccessDenied:
        return False, t("kill_denied", pid=pid)
    except Exception as exc:
        return False, str(exc)


def kill_all_on_port(port: int) -> tuple[int, list[str]]:
    pids = pids_for_port(port)
    if not pids:
        return 0, [t("no_active")]

    messages: list[str] = []
    killed = 0
    for pid in sorted(pids):
        ok, msg = kill_process(pid)
        messages.append(msg)
        if ok:
            killed += 1
    return killed, messages
