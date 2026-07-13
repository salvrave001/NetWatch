#!/usr/bin/env python3
"""ProcessChecker — просмотр процессов и портов, завершение сессий."""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass

import psutil

STATE_LABELS = {
    psutil.CONN_LISTEN: "LISTENING",
    psutil.CONN_ESTABLISHED: "ESTABLISHED",
    psutil.CONN_SYN_SENT: "SYN_SENT",
    psutil.CONN_SYN_RECV: "SYN_RECEIVED",
    psutil.CONN_FIN_WAIT1: "FIN_WAIT_1",
    psutil.CONN_FIN_WAIT2: "FIN_WAIT_2",
    psutil.CONN_TIME_WAIT: "TIME_WAIT",
    psutil.CONN_CLOSE: "CLOSE",
    psutil.CONN_CLOSE_WAIT: "CLOSE_WAIT",
    psutil.CONN_LAST_ACK: "LAST_ACK",
    psutil.CONN_CLOSING: "CLOSING",
    psutil.CONN_NONE: "-",
}


def format_state(state: str) -> str:
    return STATE_LABELS.get(state, state.upper() if state else "-")


@dataclass
class ConnectionInfo:
    proto: str
    local: str
    remote: str
    state: str
    pid: int
    process_name: str


def format_addr(addr) -> str:
    if not addr:
        return "*:*"
    ip, port = addr
    if ":" in ip and not ip.startswith("["):
        ip = f"[{ip}]"
    return f"{ip}:{port}"


def get_process_name(pid: int) -> str:
    if pid == 0:
        return "-"
    try:
        return psutil.Process(pid).name()
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return "<unknown>"


def collect_connections(port: int | None = None, listening_only: bool = False) -> list[ConnectionInfo]:
    results: list[ConnectionInfo] = []

    for conn in psutil.net_connections(kind="inet"):
        local_port = conn.laddr.port if conn.laddr else None
        remote_port = conn.raddr.port if conn.raddr else None

        if port is not None and local_port != port and remote_port != port:
            continue

        state = conn.status if conn.status else "-"
        if listening_only and state != psutil.CONN_LISTEN:
            continue

        remote = format_addr(conn.raddr)
        if state == psutil.CONN_LISTEN:
            remote = "0.0.0.0:0"

        results.append(
            ConnectionInfo(
                proto="TCP" if conn.type.name == "SOCK_STREAM" else "UDP",
                local=format_addr(conn.laddr),
                remote=remote,
                state=format_state(state),
                pid=conn.pid or 0,
                process_name=get_process_name(conn.pid or 0),
            )
        )

    results.sort(key=lambda c: (c.local, c.state, c.pid))
    return results


def print_connections(connections: list[ConnectionInfo]) -> None:
    if not connections:
        print("Соединений не найдено.")
        return

    header = f"{'Proto':<5} {'Local Address':<22} {'Foreign Address':<22} {'State':<14} {'PID':<8} Process"
    print(header)
    print("-" * len(header))

    for c in connections:
        print(
            f"{c.proto:<5} {c.local:<22} {c.remote:<22} {c.state:<14} {c.pid:<8} {c.process_name}"
        )


def get_pids_for_port(port: int, include_listening: bool = True) -> dict[int, list[str]]:
    """Возвращает PID -> список состояний соединений на указанном порту."""
    pid_states: dict[int, list[str]] = {}

    for conn in psutil.net_connections(kind="inet"):
        local_port = conn.laddr.port if conn.laddr else None
        remote_port = conn.raddr.port if conn.raddr else None

        if local_port != port and remote_port != port:
            continue

        state = format_state(conn.status or "-")
        if not include_listening and conn.status == psutil.CONN_LISTEN:
            continue

        pid = conn.pid or 0
        if pid == 0:
            continue

        pid_states.setdefault(pid, []).append(state)

    return pid_states


def kill_processes_on_port(port: int, force: bool = False, yes: bool = False) -> int:
    pid_states = get_pids_for_port(port)

    if not pid_states:
        print(f"На порту {port} нет активных процессов для завершения.")
        return 1

    print(f"Процессы на порту {port}:")
    for pid, states in sorted(pid_states.items()):
        name = get_process_name(pid)
        states_str = ", ".join(sorted(set(states)))
        print(f"  PID {pid} ({name}) — {states_str}")

    if not yes:
        answer = input("\nЗавершить эти процессы? [y/N]: ").strip().lower()
        if answer not in ("y", "yes", "д", "да"):
            print("Отменено.")
            return 0

    killed = 0
    errors = 0

    for pid, states in sorted(pid_states.items()):
        name = get_process_name(pid)
        states_str = ", ".join(sorted(set(states)))
        try:
            proc = psutil.Process(pid)
            proc.kill() if force else proc.terminate()
            action = "убит" if force else "остановлен"
            print(f"  PID {pid} ({name}) — {action} [{states_str}]")
            killed += 1
        except psutil.NoSuchProcess:
            print(f"  PID {pid} ({name}) — уже завершён")
        except psutil.AccessDenied:
            print(f"  PID {pid} ({name}) — отказано в доступе (нужны права администратора)")
            errors += 1
        except psutil.Error as exc:
            print(f"  PID {pid} ({name}) — ошибка: {exc}")
            errors += 1

    print(f"\nЗавершено процессов: {killed}, ошибок: {errors}")
    return 0 if errors == 0 else 1


def list_listening_ports() -> None:
    entries: list[tuple[str, int, str]] = []

    for conn in psutil.net_connections(kind="inet"):
        if conn.status != psutil.CONN_LISTEN or not conn.laddr:
            continue

        pid = conn.pid or 0
        entries.append((format_addr(conn.laddr), pid, get_process_name(pid)))

    if not entries:
        print("Нет процессов в состоянии LISTENING.")
        return

    entries.sort(key=lambda e: (e[0], e[1]))

    header = f"{'Local Address':<22} {'PID':<8} Process"
    print(header)
    print("-" * len(header))

    for local, pid, name in entries:
        print(f"{local:<22} {pid:<8} {name}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Просмотр процессов и портов (аналог netstat -ano) с возможностью завершения сессий.",
        epilog="Примеры:\n"
        "  python process_checker.py --listen\n"
        "  python process_checker.py --port 8000\n"
        "  python process_checker.py --port 8000 --kill\n"
        "  python process_checker.py --port 8000 --kill --force",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "-p", "--port",
        type=int,
        help="Фильтр по порту (как findstr :8000)",
    )
    parser.add_argument(
        "-l", "--listen",
        action="store_true",
        help="Показать только порты в состоянии LISTENING",
    )
    parser.add_argument(
        "-k", "--kill",
        action="store_true",
        help="Завершить все процессы, связанные с указанным портом",
    )
    parser.add_argument(
        "-f", "--force",
        action="store_true",
        help="Принудительное завершение (kill вместо terminate)",
    )
    parser.add_argument(
        "-y", "--yes",
        action="store_true",
        help="Не спрашивать подтверждение при --kill",
    )
    return parser


def main() -> int:
    if sys.platform != "win32":
        print("Предупреждение: утилита оптимизирована для Windows.", file=sys.stderr)

    parser = build_parser()
    args = parser.parse_args()

    if args.kill:
        if args.port is None:
            parser.error("--kill требует указания --port")
        return kill_processes_on_port(args.port, force=args.force, yes=args.yes)

    if args.listen and args.port is None:
        list_listening_ports()
        return 0

    connections = collect_connections(port=args.port, listening_only=args.listen)
    print_connections(connections)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\nПрервано.")
        raise SystemExit(130)
    except psutil.AccessDenied:
        print(
            "Ошибка доступа. Запустите от имени администратора.",
            file=sys.stderr,
        )
        raise SystemExit(1)
