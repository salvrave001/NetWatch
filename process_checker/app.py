"""NetWatch — cyberpunk-minimalist desktop UI."""

from __future__ import annotations

import threading
from tkinter import ttk

import customtkinter as ctk
import psutil
from PIL import Image

from process_checker.i18n import get_lang, set_lang, state_label, t, toggle_lang
from process_checker.network import (
    ConnectionRow,
    collect_connections,
    kill_all_on_port,
    kill_process,
    pids_for_port,
)
from process_checker.paths import asset_path
from process_checker.theme import COLORS, FONTS, QUICK_PORTS, SIZES, SORT_KEYS
from process_checker.ui import (
    ConfirmDialog,
    ConnectionTree,
    HudButton,
    HudEntry,
    HudFrame,
    HudLabel,
    InfoDialog,
    PortChip,
    apply_window_icon,
)


class NetWatchApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()

        ctk.set_appearance_mode("dark")
        self.configure(fg_color=COLORS["bg"])

        # Windows taskbar identity — use exe/app icon, not python/CTk default
        try:
            import ctypes

            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("NetWatch.App.1.0")
        except Exception:
            pass

        self.title(t("app_title"))
        self.geometry("1100x720")
        self.minsize(900, 560)
        apply_window_icon(self)
        self.bind("<Map>", lambda _e: apply_window_icon(self, retries=False), add="+")

        self._rows: list[ConnectionRow] = []
        self._selected_index: int | None = None
        self._auto_job: str | None = None
        self._sort_col: str = "local"
        self._sort_asc: bool = True
        self._refreshing = False
        self._refresh_token = 0
        self._last_port: int | None = None
        self._logo_image: ctk.CTkImage | None = None

        self._build_ui()
        apply_window_icon(self)
        self.refresh()

    def _build_ui(self) -> None:
        self._build_header()
        self._build_scan_bar()
        self._build_body()
        self._build_actions()
        self._build_status_bar()

    def _build_header(self) -> None:
        header = HudFrame(self, fg_color=COLORS["bg"], border_width=0)
        header.pack(fill="x", padx=20, pady=(18, 0))

        left = ctk.CTkFrame(header, fg_color="transparent")
        left.pack(side="left", fill="x", expand=True)

        logo_path = asset_path("logo_header.png")
        if logo_path.is_file():
            pil_logo = Image.open(logo_path)
            self._logo_image = ctk.CTkImage(light_image=pil_logo, dark_image=pil_logo, size=(32, 32))
            ctk.CTkLabel(left, text="", image=self._logo_image, width=32, height=32).pack(
                side="left", padx=(0, 10)
            )

        self._brand_label = ctk.CTkLabel(
            left,
            text=t("brand"),
            font=FONTS["title"],
            text_color=COLORS["text"],
            anchor="w",
        )
        self._brand_label.pack(side="left")

        ctk.CTkLabel(
            left,
            text="  v1.0",
            font=FONTS["caption"],
            text_color=COLORS["accent"],
            anchor="w",
        ).pack(side="left", pady=(4, 0))

        right = ctk.CTkFrame(header, fg_color="transparent")
        right.pack(side="right")

        self._lang_btn = HudButton(
            right,
            text=self._lang_button_text(),
            width=64,
            accent=True,
            command=self._toggle_language,
        )
        self._lang_btn.pack(side="right", padx=(12, 0))

        self._live_dot = ctk.CTkFrame(
            right, width=SIZES["dot"], height=SIZES["dot"], fg_color=COLORS["text_muted"], corner_radius=4
        )
        self._live_dot.pack(side="right", padx=(6, 0), pady=4)
        self._live_dot.pack_propagate(False)

        self._scan_label = ctk.CTkLabel(
            right,
            text=t("all_ports"),
            font=FONTS["heading"],
            text_color=COLORS["text_dim"],
        )
        self._scan_label.pack(side="right")

        ctk.CTkFrame(self, height=1, fg_color=COLORS["border_dim"], corner_radius=0).pack(
            fill="x", padx=20, pady=(14, 0)
        )

    @staticmethod
    def _lang_button_text() -> str:
        # Show current language code on the button
        return "RU" if get_lang() == "ru" else "EU"

    def _toggle_language(self) -> None:
        toggle_lang()
        self._apply_language()

    def _apply_language(self) -> None:
        self.title(t("app_title"))
        self._brand_label.configure(text=t("brand"))
        self._lang_btn.configure(text=self._lang_button_text())
        self._port_label.configure(text=t("port_label"))
        self._scan_btn.configure(text=t("scan"))
        self._all_btn.configure(text=t("all"))
        self._refresh_btn.configure(text=t("refresh"))
        self._live_toggle.configure(text=t("live"))
        self._quick_label.configure(text=t("quick_ports"))
        self._conn_label.configure(text=t("connections"))
        self._kill_btn.configure(text=t("kill_selected"))
        self._kill_all_btn.configure(text=t("kill_all"))
        self._hint_label.configure(text=t("hint_time_wait"))
        self._status_title.configure(text=t("status"))
        self.tree.refresh_headers()
        self._fill_list()
        self._update_header_stats(self._last_port)

    def _build_scan_bar(self) -> None:
        bar = ctk.CTkFrame(self, fg_color="transparent")
        bar.pack(fill="x", padx=20, pady=(16, 0))

        self._port_label = HudLabel(bar, text=t("port_label"), heading=True)
        self._port_label.pack(side="left", padx=(0, 10))

        self.port_var = ctk.StringVar()
        entry = HudEntry(bar, textvariable=self.port_var, width=110, placeholder_text="8000")
        entry.pack(side="left", padx=(0, 12))
        entry.bind("<Return>", lambda _e: self.refresh())

        self._scan_btn = HudButton(bar, text=t("scan"), width=90, accent=True, command=self.refresh)
        self._scan_btn.pack(side="left", padx=(0, 6))
        self._all_btn = HudButton(bar, text=t("all"), width=70, command=self.show_all)
        self._all_btn.pack(side="left", padx=(0, 6))
        self._refresh_btn = HudButton(bar, text=t("refresh"), width=110, command=self.refresh)
        self._refresh_btn.pack(side="left")

        self.auto_refresh_var = ctk.BooleanVar(value=False)
        self._live_toggle = ctk.CTkCheckBox(
            bar,
            text=t("live"),
            variable=self.auto_refresh_var,
            command=self._toggle_auto_refresh,
            font=FONTS["heading"],
            text_color=COLORS["text_dim"],
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_dim"],
            border_color=COLORS["border"],
            checkmark_color=COLORS["text"],
            corner_radius=0,
        )
        self._live_toggle.pack(side="right")

    def _build_body(self) -> None:
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=20, pady=(16, 0))
        body.grid_columnconfigure(1, weight=1)
        body.grid_rowconfigure(0, weight=1)

        self._build_quick_ports(body)
        self._build_connection_panel(body)

    def _build_quick_ports(self, parent: ctk.CTkFrame) -> None:
        panel = HudFrame(parent, width=SIZES["sidebar"])
        panel.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        panel.grid_propagate(False)

        self._quick_label = HudLabel(panel, text=t("quick_ports"), heading=True)
        self._quick_label.pack(anchor="w", padx=12, pady=(12, 10))

        grid = ctk.CTkFrame(panel, fg_color="transparent")
        grid.pack(fill="both", expand=True, padx=10, pady=(0, 12))

        for i, port in enumerate(QUICK_PORTS):
            chip = PortChip(grid, port, lambda p=port: self._select_port(p))
            chip.grid(row=i // 2, column=i % 2, padx=4, pady=4, sticky="ew")
            grid.grid_columnconfigure(i % 2, weight=1)

    def _build_connection_panel(self, parent: ctk.CTkFrame) -> None:
        panel = HudFrame(parent)
        panel.grid(row=0, column=1, sticky="nsew")
        panel.grid_rowconfigure(1, weight=1)
        panel.grid_columnconfigure(0, weight=1)

        top = ctk.CTkFrame(panel, fg_color="transparent")
        top.pack(fill="x", padx=12, pady=(12, 0))

        self._conn_label = HudLabel(top, text=t("connections"), heading=True)
        self._conn_label.pack(side="left")
        self._count_label = HudLabel(top, text="0", dim=True)
        self._count_label.pack(side="right")

        table_wrap = ctk.CTkFrame(panel, fg_color=COLORS["bg"])
        table_wrap.pack(fill="both", expand=True, padx=12, pady=(8, 12))
        table_wrap.grid_rowconfigure(0, weight=1)
        table_wrap.grid_columnconfigure(0, weight=1)

        self.tree = ConnectionTree(table_wrap, on_sort=self._on_sort)
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.tree.set_sort_indicator(self._sort_col, self._sort_asc)

        vsb = ttk.Scrollbar(table_wrap, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.grid(row=0, column=1, sticky="ns")

        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)

    def _build_actions(self) -> None:
        ctk.CTkFrame(self, height=1, fg_color=COLORS["border_dim"], corner_radius=0).pack(
            fill="x", padx=20, pady=(12, 0)
        )

        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.pack(fill="x", padx=20, pady=14)

        self._kill_btn = HudButton(
            actions,
            text=t("kill_selected"),
            width=250,
            danger=True,
            command=self.kill_selected,
        )
        self._kill_btn.pack(side="left", padx=(0, 10))

        self._kill_all_btn = HudButton(
            actions,
            text=t("kill_all"),
            width=320,
            danger=True,
            command=self.kill_all_sessions,
        )
        self._kill_all_btn.pack(side="left")

        self._hint_label = HudLabel(actions, text=t("hint_time_wait"), dim=True)
        self._hint_label.pack(side="right")

    def _build_status_bar(self) -> None:
        ctk.CTkFrame(self, height=1, fg_color=COLORS["border_dim"], corner_radius=0).pack(fill="x", padx=20)

        bar = ctk.CTkFrame(self, fg_color="transparent")
        bar.pack(fill="x", padx=20, pady=(10, 16))

        self._status_title = HudLabel(bar, text=t("status"), heading=True)
        self._status_title.pack(side="left", padx=(0, 10))
        self.status_var = ctk.StringVar(value=t("ready"))
        HudLabel(bar, textvariable=self.status_var, dim=True).pack(side="left")

    def _select_port(self, port: int) -> None:
        self.port_var.set(str(port))
        self.refresh()

    def _parse_port(self) -> int | None:
        raw = self.port_var.get().strip()
        if not raw:
            return None
        try:
            port = int(raw)
        except ValueError:
            InfoDialog(self, t("error"), t("invalid_port"), is_error=True)
            return None
        if not 1 <= port <= 65535:
            InfoDialog(self, t("error"), t("port_range"), is_error=True)
            return None
        return port

    def show_all(self) -> None:
        self.port_var.set("")
        self.refresh()

    def refresh(self) -> None:
        port = self._parse_port()
        if self.port_var.get().strip() and port is None:
            return
        if self._refreshing:
            return

        self._refreshing = True
        self._refresh_token += 1
        token = self._refresh_token
        self.status_var.set(t("updating"))

        def worker() -> None:
            try:
                rows = collect_connections(port)
                error: str | None = None
            except psutil.AccessDenied:
                try:
                    rows = collect_connections(port)
                    error = t("access_denied")
                except Exception as exc:
                    rows = []
                    error = str(exc)
            except Exception as exc:
                rows = []
                error = str(exc)

            self.after(0, lambda: self._on_data_ready(token, port, rows, error))

        threading.Thread(target=worker, daemon=True).start()

    def _on_data_ready(
        self,
        token: int,
        port: int | None,
        rows: list[ConnectionRow],
        error: str | None,
    ) -> None:
        if token != self._refresh_token:
            return
        self._refreshing = False
        self._last_port = port

        if error and not rows:
            InfoDialog(self, t("error"), t("refresh_failed", error=error), is_error=True)
            self.status_var.set(t("error"))
            return
        if error and not self.auto_refresh_var.get():
            InfoDialog(self, t("no_access"), error, is_error=True)

        self._rows = rows
        self._selected_index = None
        self._apply_sort()
        self._fill_list()
        self._update_header_stats(port)

    def _on_sort(self, col: str) -> None:
        if self._sort_col == col:
            self._sort_asc = not self._sort_asc
        else:
            self._sort_col = col
            self._sort_asc = True
        self.tree.set_sort_indicator(self._sort_col, self._sort_asc)
        self._selected_index = None
        self._apply_sort()
        self._fill_list()

    def _sort_value(self, row: ConnectionRow):
        key = SORT_KEYS.get(self._sort_col, "local_addr")
        if key == "protocol":
            return row.protocol
        if key == "local_addr":
            return row.local_addr
        if key == "remote_addr":
            return row.remote_addr
        if key == "state":
            return state_label(row.state)
        if key == "pid":
            return row.pid
        if key == "process_name":
            return row.process_name.lower()
        return row.local_addr

    def _apply_sort(self) -> None:
        self._rows.sort(key=self._sort_value, reverse=not self._sort_asc)

    def _update_header_stats(self, port: int | None) -> None:
        unique_pids = {r.pid for r in self._rows if r.pid > 0}
        port_text = t("port_named", port=port) if port else t("all_ports")
        self._scan_label.configure(text=port_text)
        self._count_label.configure(text=str(len(self._rows)))
        self.status_var.set(t("stats", n=len(self._rows), pids=len(unique_pids)))
        self._live_dot.configure(
            fg_color=COLORS["accent"] if self.auto_refresh_var.get() else COLORS["text_muted"]
        )

    def _fill_list(self) -> None:
        self.tree.delete(*self.tree.get_children())
        for idx, row in enumerate(self._rows):
            tags: list[str] = ["odd" if idx % 2 else "even"]
            if row.state == "LISTENING":
                tags.append("listening")
            self.tree.insert(
                "",
                "end",
                iid=str(idx),
                values=(
                    row.protocol,
                    row.local_addr,
                    row.remote_addr,
                    state_label(row.state),
                    row.pid if row.pid > 0 else "—",
                    row.process_name,
                ),
                tags=tuple(tags),
            )

    def _on_tree_select(self, _event=None) -> None:
        sel = self.tree.selection()
        if not sel:
            self._selected_index = None
            return
        self._selected_index = int(sel[0])

    def _selected_row(self) -> ConnectionRow | None:
        if self._selected_index is None:
            return None
        if 0 <= self._selected_index < len(self._rows):
            return self._rows[self._selected_index]
        return None

    def kill_selected(self) -> None:
        row = self._selected_row()
        if not row:
            InfoDialog(self, t("selection"), t("select_row"))
            return
        if row.pid <= 0:
            InfoDialog(self, t("pid0_title"), t("pid0_msg"))
            return

        ConfirmDialog(
            self,
            t("kill_title"),
            t("kill_confirm", name=row.process_name, pid=row.pid),
            on_confirm=lambda: self._do_kill(row.pid),
        )

    def _do_kill(self, pid: int) -> None:
        ok, msg = kill_process(pid)
        if ok:
            InfoDialog(self, t("done"), msg)
        else:
            InfoDialog(self, t("error"), msg, is_error=True)
        self.refresh()

    def kill_all_sessions(self) -> None:
        port = self._parse_port()
        if port is None:
            InfoDialog(self, t("port"), t("need_port"))
            return

        pids = pids_for_port(port)
        if not pids:
            InfoDialog(self, t("port"), t("no_pids", port=port))
            return

        pid_list = ", ".join(str(p) for p in sorted(pids))
        ConfirmDialog(
            self,
            t("kill_all_title"),
            t("kill_all_confirm", port=port, pids=pid_list),
            on_confirm=lambda: self._do_kill_all(port),
        )

    def _do_kill_all(self, port: int) -> None:
        killed, messages = kill_all_on_port(port)
        InfoDialog(self, t("result"), t("killed_count", n=killed, details="\n".join(messages)))
        self.refresh()

    def _toggle_auto_refresh(self) -> None:
        if self._auto_job:
            self.after_cancel(self._auto_job)
            self._auto_job = None
        self._live_dot.configure(
            fg_color=COLORS["accent"] if self.auto_refresh_var.get() else COLORS["text_muted"]
        )
        if self.auto_refresh_var.get():
            self._schedule_auto_refresh()

    def _schedule_auto_refresh(self) -> None:
        if not self.auto_refresh_var.get():
            return
        self.refresh()
        self._auto_job = self.after(3000, self._schedule_auto_refresh)


def main() -> None:
    set_lang("ru")
    app = NetWatchApp()
    app.mainloop()


if __name__ == "__main__":
    main()
