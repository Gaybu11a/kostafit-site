"""Google Sheets bilan ishlash: sotuvlar, xodimlar va sozlamalar."""
from dataclasses import dataclass
from datetime import datetime

import gspread

SALES_SHEET = "Sotuvlar"
STAFF_SHEET = "Xodimlar"
SETTINGS_SHEET = "Sozlamalar"

SALES_HEADER = ["Sana", "Mijoz ismi", "Telefon", "Qo'shimcha telefon", "Manzil",
                "Mahsulot", "Summa (so'm)", "Xodim", "Xodim ID"]
STAFF_HEADER = ["Telegram ID", "Ism", "Username", "Qo'shilgan sana", "Holat"]

DATE_FMT = "%d.%m.%Y %H:%M"

# Xodim holatlari
PENDING = "kutilmoqda"
ACTIVE = "faol"
BLOCKED = "o'chirilgan"


@dataclass
class Staff:
    user_id: int
    name: str
    username: str
    added: str
    status: str
    row: int  # jadvaldagi qator raqami


class Storage:
    def __init__(self, credentials_file: str, spreadsheet: str):
        gc = gspread.service_account(filename=credentials_file)
        if spreadsheet.startswith("http"):
            self.book = gc.open_by_url(spreadsheet)
        else:
            self.book = gc.open_by_key(spreadsheet)
        self.sales = self._sheet(SALES_SHEET, SALES_HEADER)
        self.staff_ws = self._sheet(STAFF_SHEET, STAFF_HEADER)
        self.settings = self._sheet(SETTINGS_SHEET, ["Kalit", "Qiymat"])
        self.staff: dict[int, Staff] = {}
        self.reload_staff()

    def _sheet(self, title: str, header: list[str]):
        try:
            ws = self.book.worksheet(title)
        except gspread.WorksheetNotFound:
            ws = self.book.add_worksheet(title=title, rows=1000, cols=len(header))
        if ws.row_values(1) != header:
            ws.update([header], "A1")
            ws.format("1:1", {"textFormat": {"bold": True}})
            ws.freeze(rows=1)
        return ws

    # ---------- sozlamalar (admin ID shu yerda saqlanadi) ----------
    def get_setting(self, key: str) -> str | None:
        for row in self.settings.get_all_values()[1:]:
            if row and row[0] == key:
                return row[1] if len(row) > 1 else ""
        return None

    def set_setting(self, key: str, value: str) -> None:
        rows = self.settings.get_all_values()
        for i, row in enumerate(rows[1:], start=2):
            if row and row[0] == key:
                self.settings.update([[key, value]], f"A{i}", value_input_option="RAW")
                return
        self.settings.append_row([key, value], value_input_option="RAW")

    # ---------- xodimlar ----------
    def reload_staff(self) -> None:
        self.staff = {}
        for i, row in enumerate(self.staff_ws.get_all_values()[1:], start=2):
            row = (row + [""] * 5)[:5]
            if not row[0].strip().lstrip("-").isdigit():
                continue
            uid = int(row[0])
            self.staff[uid] = Staff(uid, row[1], row[2], row[3], row[4] or PENDING, i)

    def add_staff(self, user_id: int, name: str, username: str, now: datetime) -> Staff:
        values = [str(user_id), name, username, now.strftime(DATE_FMT), PENDING]
        self.staff_ws.append_row(values, value_input_option="RAW")
        self.reload_staff()
        return self.staff[user_id]

    def set_staff_status(self, user_id: int, status: str) -> Staff | None:
        s = self.staff.get(user_id)
        if not s:
            return None
        self.staff_ws.update([[status]], f"E{s.row}", value_input_option="RAW")
        s.status = status
        return s

    # ---------- sotuvlar ----------
    def add_sale(self, now: datetime, name: str, phone: str, phone2: str, address: str,
                 product: str, amount: int, staff_name: str, staff_id: int) -> None:
        self.sales.append_row(
            [now.strftime(DATE_FMT), name, phone, phone2, address, product, amount,
             staff_name, str(staff_id)],
            value_input_option="RAW",
        )

    def all_sales(self) -> list[dict]:
        """Hisobot uchun: [{date, amount, staff_id, staff_name}]"""
        out = []
        # UNFORMATTED: summa ustuni qanday formatlangan bo'lmasin, sof son keladi
        for row in self.sales.get_all_values(value_render_option="UNFORMATTED_VALUE")[1:]:
            row = (list(row) + [""] * 9)[:9]
            try:
                date = datetime.strptime(str(row[0]), DATE_FMT)
            except ValueError:
                continue
            amount = row[6]
            if not isinstance(amount, (int, float)):
                digits = "".join(ch for ch in str(amount) if ch.isdigit())
                amount = int(digits) if digits else 0
            staff_id = str(row[8]).strip()
            out.append({
                "date": date,
                "amount": int(amount),
                "staff_name": str(row[7]),
                "staff_id": int(staff_id) if staff_id.isdigit() else 0,
            })
        return out
