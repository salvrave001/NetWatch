"""NetWatch — cyberpunk-minimalist UI widgets."""

from __future__ import annotations

from collections.abc import Callable
from tkinter import PhotoImage, ttk

import customtkinter as ctk

from process_checker.i18n import column_title, t, tree_columns
from process_checker.paths import asset_path
from process_checker.theme import COLORS, FONTS, SIZES

_ICON_PHOTO: PhotoImage | None = None
_ICON_ICO: str | None = None
_WIN_HICONS: list[int] = []


def _icon_paths() -> tuple[str | None, str | None]:
    global _ICON_ICO
    ico = asset_path("netwatch.ico")
    png = asset_path("logo_header.png")
    ico_s = str(ico) if ico.is_file() else None
    png_s = str(png) if png.is_file() else None
    if ico_s:
        _ICON_ICO = ico_s
    return ico_s, png_s


def _get_icon_photo(master) -> PhotoImage | None:
    global _ICON_PHOTO
    if _ICON_PHOTO is not None:
        return _ICON_PHOTO
    _, png = _icon_paths()
    if not png:
        return None
    try:
        root = master.winfo_toplevel()
        while True:
            parent = getattr(root, "master", None)
            if parent is None:
                break
            root = parent.winfo_toplevel() if hasattr(parent, "winfo_toplevel") else parent
        _ICON_PHOTO = PhotoImage(master=root, file=png)
        return _ICON_PHOTO
    except Exception:
        try:
            _ICON_PHOTO = PhotoImage(file=png)
            return _ICON_PHOTO
        except Exception:
            return None


def _apply_win32_icon(window, ico_path: str) -> None:
    """Set title-bar icon via Win32 WM_SETICON (bypasses CTk default)."""
    try:
        import ctypes

        user32 = ctypes.windll.user32
        WM_SETICON = 0x0080
        ICON_SMALL = 0
        ICON_BIG = 1
        IMAGE_ICON = 1
        LR_LOADFROMFILE = 0x0010
        LR_DEFAULTSIZE = 0x0040
        GA_ROOT = 2

        hwnd = int(window.winfo_id())
        root_hwnd = user32.GetAncestor(hwnd, GA_ROOT) or hwnd

        for size, which in ((16, ICON_SMALL), (32, ICON_BIG)):
            hicon = user32.LoadImageW(
                None,
                ico_path,
                IMAGE_ICON,
                size,
                size,
                LR_LOADFROMFILE,
            )
            if hicon:
                _WIN_HICONS.append(hicon)
                user32.SendMessageW(root_hwnd, WM_SETICON, which, hicon)
                user32.SendMessageW(hwnd, WM_SETICON, which, hicon)
    except Exception:
        pass


def apply_window_icon(window, *, retries: bool = True) -> None:
    """Force NetWatch icon on any Tk/CTk window (kills default blue CTk icon)."""
    ico, _ = _icon_paths()

    def _apply(_event=None) -> None:
        try:
            if ico:
                try:
                    window.iconbitmap(default=ico)
                except Exception:
                    pass
                try:
                    window.iconbitmap(ico)
                except Exception:
                    pass
                try:
                    window.wm_iconbitmap(ico)
                except Exception:
                    pass
                try:
                    if window.winfo_exists():
                        _apply_win32_icon(window, ico)
                except Exception:
                    pass
        except Exception:
            pass
        try:
            photo = _get_icon_photo(window)
            if photo is not None:
                window._netwatch_icon_photo = photo
                window.iconphoto(False, photo)
                window.iconphoto(True, photo)
        except Exception:
            pass

    _apply()
    if retries:
        try:
            window.after_idle(_apply)
            window.after(20, _apply)
            window.after(100, _apply)
            window.after(300, _apply)
            window.bind("<Map>", _apply, add="+")
        except Exception:
            pass


class HudFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs) -> None:
        kwargs.setdefault("fg_color", COLORS["bg_panel"])
        kwargs.setdefault("border_width", 1)
        kwargs.setdefault("border_color", COLORS["border_dim"])
        kwargs.setdefault("corner_radius", 0)
        super().__init__(master, **kwargs)


class HudLabel(ctk.CTkLabel):
    def __init__(self, master, *, dim: bool = False, heading: bool = False, **kwargs) -> None:
        if heading:
            kwargs.setdefault("font", FONTS["heading"])
            kwargs.setdefault("text_color", COLORS["text_dim"])
        else:
            kwargs.setdefault("font", FONTS["body"])
            kwargs.setdefault("text_color", COLORS["text_dim"] if dim else COLORS["text"])
        kwargs.setdefault("anchor", "w")
        super().__init__(master, **kwargs)


class HudButton(ctk.CTkButton):
    def __init__(
        self,
        master,
        *,
        accent: bool = False,
        danger: bool = False,
        **kwargs,
    ) -> None:
        kwargs.setdefault("corner_radius", 0)
        kwargs.setdefault("height", SIZES["btn_height"])
        kwargs.setdefault("font", FONTS["heading"])

        if danger:
            kwargs.setdefault("fg_color", COLORS["accent"])
            kwargs.setdefault("hover_color", COLORS["accent_dim"])
            kwargs.setdefault("text_color", COLORS["text"])
            kwargs.setdefault("border_width", 0)
        elif accent:
            kwargs.setdefault("fg_color", "transparent")
            kwargs.setdefault("hover_color", COLORS["bg_row_hover"])
            kwargs.setdefault("text_color", COLORS["accent"])
            kwargs.setdefault("border_width", 1)
            kwargs.setdefault("border_color", COLORS["accent"])
        else:
            kwargs.setdefault("fg_color", "transparent")
            kwargs.setdefault("hover_color", COLORS["bg_row_hover"])
            kwargs.setdefault("text_color", COLORS["text"])
            kwargs.setdefault("border_width", 1)
            kwargs.setdefault("border_color", COLORS["border"])

        super().__init__(master, **kwargs)


class HudEntry(ctk.CTkEntry):
    def __init__(self, master, **kwargs) -> None:
        kwargs.setdefault("corner_radius", 0)
        kwargs.setdefault("height", SIZES["entry_height"])
        kwargs.setdefault("font", FONTS["mono_lg"])
        kwargs.setdefault("fg_color", COLORS["bg"])
        kwargs.setdefault("border_color", COLORS["border"])
        kwargs.setdefault("border_width", 1)
        kwargs.setdefault("text_color", COLORS["accent"])
        kwargs.setdefault("placeholder_text_color", COLORS["text_muted"])
        super().__init__(master, **kwargs)


class PortChip(ctk.CTkButton):
    def __init__(self, master, port: int, command: Callable[[], None], **kwargs) -> None:
        kwargs.setdefault("text", str(port))
        kwargs.setdefault("width", SIZES["chip_width"])
        kwargs.setdefault("height", SIZES["chip_height"])
        kwargs.setdefault("corner_radius", 0)
        kwargs.setdefault("font", FONTS["body"])
        kwargs.setdefault("fg_color", COLORS["bg"])
        kwargs.setdefault("hover_color", COLORS["bg_row_hover"])
        kwargs.setdefault("text_color", COLORS["text_dim"])
        kwargs.setdefault("border_width", 1)
        kwargs.setdefault("border_color", COLORS["border_dim"])
        super().__init__(master, command=command, **kwargs)


def configure_tree_style() -> None:
    style = ttk.Style()
    style.theme_use("clam")
    style.configure(
        "Hud.Treeview",
        background=COLORS["bg"],
        foreground=COLORS["text"],
        fieldbackground=COLORS["bg"],
        borderwidth=0,
        rowheight=28,
        font=FONTS["body"],
    )
    style.configure(
        "Hud.Treeview.Heading",
        background=COLORS["bg_panel"],
        foreground=COLORS["text_dim"],
        borderwidth=0,
        relief="flat",
        font=FONTS["heading"],
        padding=(6, 8),
    )
    style.map(
        "Hud.Treeview",
        background=[("selected", COLORS["bg_row_selected"])],
        foreground=[("selected", COLORS["text"])],
    )
    style.map(
        "Hud.Treeview.Heading",
        background=[("active", COLORS["bg_row_hover"])],
        foreground=[("active", COLORS["accent"])],
    )


class ConnectionTree(ttk.Treeview):
    def __init__(self, master, *, on_sort: Callable[[str], None]) -> None:
        configure_tree_style()
        cols = tree_columns()
        super().__init__(
            master,
            columns=tuple(c[0] for c in cols),
            show="headings",
            selectmode="browse",
            style="Hud.Treeview",
        )
        self._on_sort = on_sort
        self._sort_col: str | None = None
        self._sort_asc = True

        for col_id, title, width in cols:
            stretch = col_id == "process"
            self.heading(col_id, text=title, command=lambda c=col_id: self._on_sort(c), anchor="w")
            self.column(col_id, width=width, minwidth=50, stretch=stretch, anchor="w")

        self.tag_configure("odd", background=COLORS["bg_row_alt"])
        self.tag_configure("even", background=COLORS["bg"])
        self.tag_configure("listening", foreground=COLORS["accent"])

    def refresh_headers(self) -> None:
        self.set_sort_indicator(self._sort_col, self._sort_asc)

    def set_sort_indicator(self, col: str | None, ascending: bool) -> None:
        self._sort_col = col
        self._sort_asc = ascending
        for col_id, _, _ in tree_columns():
            title = column_title(col_id)
            if col_id == col:
                arrow = " ▲" if ascending else " ▼"
                self.heading(col_id, text=title + arrow)
            else:
                self.heading(col_id, text=title)


class ConfirmDialog(ctk.CTkToplevel):
    def __init__(self, master, title: str, message: str, on_confirm: Callable[[], None]) -> None:
        super().__init__(master)
        self.withdraw()
        self.title(t("app_title"))
        self.configure(fg_color=COLORS["bg"])
        self.resizable(False, False)
        self.transient(master)
        apply_window_icon(self)
        self.grab_set()

        self._on_confirm = on_confirm

        frame = HudFrame(self)
        frame.pack(fill="both", expand=True, padx=1, pady=1)

        HudLabel(frame, text=title.upper(), heading=True).pack(anchor="w", padx=16, pady=(16, 8))
        HudLabel(frame, text=message, dim=True, wraplength=420, justify="left").pack(
            anchor="w", padx=20, pady=(0, 16)
        )

        actions = ctk.CTkFrame(frame, fg_color="transparent")
        actions.pack(fill="x", padx=20, pady=(0, 16))

        HudButton(actions, text=t("cancel"), width=110, command=self.destroy).pack(side="right", padx=(8, 0))
        HudButton(actions, text=t("confirm"), width=140, danger=True, command=self._confirm).pack(side="right")

        self.update_idletasks()
        x = master.winfo_x() + (master.winfo_width() - self.winfo_width()) // 2
        y = master.winfo_y() + (master.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")
        apply_window_icon(self)
        self.deiconify()
        self.lift()
        self.focus_force()

    def _confirm(self) -> None:
        self._on_confirm()
        self.destroy()


class InfoDialog(ctk.CTkToplevel):
    def __init__(self, master, title: str, message: str, *, is_error: bool = False) -> None:
        super().__init__(master)
        self.withdraw()
        self.title(t("app_title"))
        self.configure(fg_color=COLORS["bg"])
        self.resizable(False, False)
        self.transient(master)
        apply_window_icon(self)
        self.grab_set()

        frame = HudFrame(self)
        frame.pack(fill="both", expand=True, padx=1, pady=1)

        color = COLORS["accent"] if is_error else COLORS["text_dim"]
        ctk.CTkLabel(frame, text=title.upper(), font=FONTS["heading"], text_color=color).pack(
            anchor="w", padx=16, pady=(16, 8)
        )
        HudLabel(frame, text=message, dim=True, wraplength=420, justify="left").pack(
            anchor="w", padx=20, pady=(0, 16)
        )
        HudButton(frame, text=t("ok"), width=90, accent=True, command=self.destroy).pack(
            padx=20, pady=(0, 16), anchor="e"
        )

        self.update_idletasks()
        x = master.winfo_x() + (master.winfo_width() - self.winfo_width()) // 2
        y = master.winfo_y() + (master.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")
        apply_window_icon(self)
        self.deiconify()
        self.lift()
        self.focus_force()
