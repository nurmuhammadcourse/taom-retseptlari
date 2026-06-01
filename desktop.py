# Pomodoro + Vazifalar menejeri (Desktop dastur)
# Kutubxonalar: tkinter (o'rnatilgan), json, threading

import tkinter as tk
from tkinter import ttk, messagebox
import json
import threading
import time

POMODORO_VAQT = 25 * 60   # 25 daqiqa (sekundlarda)
TANAFFUS_VAQT = 5 * 60    # 5 daqiqa
FAYL = "vazifalar.json"


# ===================== VAZIFA CLASS =====================
class Vazifa:
    def __init__(self, matn, bajarilgan=False, pomidorlar=0):
        self.matn = matn
        self.bajarilgan = bajarilgan
        self.pomidorlar = pomidorlar

    def to_dict(self):
        return {
            "matn": self.matn,
            "bajarilgan": self.bajarilgan,
            "pomidorlar": self.pomidorlar,
        }

    @classmethod
    def from_dict(cls, d):
        return cls(d["matn"], d.get("bajarilgan", False), d.get("pomidorlar", 0))


# ===================== ASOSIY APP =====================
class PomodoroApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pomodoro & Vazifalar")
        self.root.geometry("780x520")
        self.root.configure(bg="#f5f5f5")

        self.vazifalar = []

        # Taymer holati
        self.qolgan_vaqt = POMODORO_VAQT
        self.ishlayapti = False
        self.tanaffusda = False

        self.ui_qurish()
        self.vazifalarni_yuklash()
        self.royxatni_yangilash()
        self.taymerni_yangilash()

    # ----------- UI QURISH -----------
    def ui_qurish(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", rowheight=28, font=("Helvetica", 11))
        style.configure("Treeview.Heading", font=("Helvetica", 11, "bold"))

        # CHAP PANEL — vazifalar
        chap = tk.Frame(self.root, bg="#f5f5f5", padx=15, pady=15)
        chap.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Label(chap, text="📝 Vazifalar", font=("Helvetica", 18, "bold"),
                 bg="#f5f5f5", fg="#2d3436").pack(anchor="w")

        # Yangi vazifa kiritish
        kirish_frame = tk.Frame(chap, bg="#f5f5f5")
        kirish_frame.pack(fill=tk.X, pady=10)

        self.yangi_entry = ttk.Entry(kirish_frame, font=("Helvetica", 12))
        self.yangi_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5), ipady=5)
        self.yangi_entry.bind("<Return>", lambda e: self.vazifa_qoshish())
        ttk.Button(kirish_frame, text="➕ Qo'shish",
                   command=self.vazifa_qoshish).pack(side=tk.RIGHT)

        # Vazifalar jadvali
        self.tree = ttk.Treeview(
            chap, columns=("status", "pomidorlar"),
            show="tree headings", height=13,
        )
        self.tree.heading("#0", text="Vazifa")
        self.tree.heading("status", text="Holat")
        self.tree.heading("pomidorlar", text="🍅")
        self.tree.column("#0", width=240)
        self.tree.column("status", width=70, anchor="center")
        self.tree.column("pomidorlar", width=50, anchor="center")
        self.tree.pack(fill=tk.BOTH, expand=True, pady=5)

        # Boshqaruv tugmalari
        tugma_frame = tk.Frame(chap, bg="#f5f5f5")
        tugma_frame.pack(fill=tk.X, pady=(8, 0))

        ttk.Button(tugma_frame, text="✓ Bajarildi",
                   command=self.bajarildi_belgilash).pack(side=tk.LEFT, padx=2)
        ttk.Button(tugma_frame, text="🗑 O'chirish",
                   command=self.vazifa_ochirish).pack(side=tk.LEFT, padx=2)
        ttk.Button(tugma_frame, text="🧹 Bajarilganlarni tozalash",
                   command=self.bajarilganlarni_tozalash).pack(side=tk.LEFT, padx=2)

        # Vertikal ajratuvchi
        tk.Frame(self.root, bg="#dcdde1", width=2).pack(side=tk.LEFT, fill=tk.Y)

        # O'NG PANEL — Pomodoro
        ong = tk.Frame(self.root, bg="#f5f5f5", padx=20, pady=15)
        ong.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        tk.Label(ong, text="🍅 Pomodoro Taymer", font=("Helvetica", 18, "bold"),
                 bg="#f5f5f5", fg="#2d3436").pack(pady=(0, 5))

        self.holat_label = tk.Label(ong, text="Ish vaqti", font=("Helvetica", 14),
                                    bg="#f5f5f5", fg="#636e72")
        self.holat_label.pack(pady=5)

        # Katta taymer ekrani
        self.taymer_label = tk.Label(ong, text="25:00",
                                     font=("Helvetica", 72, "bold"),
                                     bg="#f5f5f5", fg="#d63031")
        self.taymer_label.pack(pady=20)

        # Boshqaruv tugmalari
        boshqaruv = tk.Frame(ong, bg="#f5f5f5")
        boshqaruv.pack(pady=10)

        self.start_btn = ttk.Button(boshqaruv, text="▶ Boshlash",
                                    command=self.taymerni_boshlash)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        ttk.Button(boshqaruv, text="⏸ Pauza",
                   command=self.taymerni_toxtatish).pack(side=tk.LEFT, padx=5)
        ttk.Button(boshqaruv, text="🔄 Reset",
                   command=self.taymerni_reset).pack(side=tk.LEFT, padx=5)

        # Statistika
        self.stat_label = tk.Label(ong, text="Jami pomidorlar: 0 🍅",
                                   font=("Helvetica", 12, "bold"),
                                   bg="#f5f5f5", fg="#2d3436")
        self.stat_label.pack(pady=15)

        # Ko'rsatma
        eslatma = tk.Label(
            ong,
            text="Avval vazifani tanlang,\nso'ngra taymerni boshlang.\nHar 25 daqiqalik ish — 1 pomidor.",
            font=("Helvetica", 10), bg="#f5f5f5", fg="#95a5a6",
            justify="center",
        )
        eslatma.pack(pady=10)

    # ----------- VAZIFA AMALLARI -----------
    def vazifa_qoshish(self):
        matn = self.yangi_entry.get().strip()
        if not matn:
            return
        self.vazifalar.append(Vazifa(matn))
        self.yangi_entry.delete(0, tk.END)
        self.saqlash()
        self.royxatni_yangilash()

    def tanlangan_index(self):
        sel = self.tree.selection()
        if not sel:
            return None
        return int(sel[0])

    def bajarildi_belgilash(self):
        idx = self.tanlangan_index()
        if idx is None:
            messagebox.showinfo("Eslatma", "Avval vazifani tanlang!")
            return
        self.vazifalar[idx].bajarilgan = not self.vazifalar[idx].bajarilgan
        self.saqlash()
        self.royxatni_yangilash()

    def vazifa_ochirish(self):
        idx = self.tanlangan_index()
        if idx is None:
            messagebox.showinfo("Eslatma", "Avval vazifani tanlang!")
            return
        if messagebox.askyesno("Tasdiqlash", "Vazifani o'chirishga ishonchingiz komilmi?"):
            del self.vazifalar[idx]
            self.saqlash()
            self.royxatni_yangilash()

    def bajarilganlarni_tozalash(self):
        bajarilganlar = [v for v in self.vazifalar if v.bajarilgan]
        if not bajarilganlar:
            messagebox.showinfo("Eslatma", "Bajarilgan vazifa yo'q.")
            return
        if messagebox.askyesno("Tasdiqlash",
                               f"{len(bajarilganlar)} ta bajarilgan vazifa o'chiriladi. Davom etamizmi?"):
            self.vazifalar = [v for v in self.vazifalar if not v.bajarilgan]
            self.saqlash()
            self.royxatni_yangilash()

    def royxatni_yangilash(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for i, v in enumerate(self.vazifalar):
            holat = "✅" if v.bajarilgan else "⏳"
            matn = v.matn
            self.tree.insert("", "end", iid=str(i), text=matn,
                             values=(holat, v.pomidorlar))
        jami = sum(v.pomidorlar for v in self.vazifalar)
        bajarilgan = sum(1 for v in self.vazifalar if v.bajarilgan)
        umumiy = len(self.vazifalar)
        self.stat_label.config(
            text=f"Vazifalar: {bajarilgan}/{umumiy}   Pomidorlar: {jami} 🍅"
        )

    # ----------- TAYMER -----------
    def taymerni_boshlash(self):
        if self.ishlayapti:
            return
        if not self.tanaffusda and self.tanlangan_index() is None:
            messagebox.showinfo("Eslatma", "Avval vazifani tanlang!")
            return
        self.ishlayapti = True
        threading.Thread(target=self.taymerni_yuritish, daemon=True).start()

    def taymerni_toxtatish(self):
        self.ishlayapti = False

    def taymerni_reset(self):
        self.ishlayapti = False
        self.tanaffusda = False
        self.qolgan_vaqt = POMODORO_VAQT
        self.holat_label.config(text="Ish vaqti", fg="#636e72")
        self.taymer_label.config(fg="#d63031")
        self.taymerni_yangilash()

    def taymerni_yuritish(self):
        while self.ishlayapti and self.qolgan_vaqt > 0:
            time.sleep(1)
            self.qolgan_vaqt -= 1
            self.root.after(0, self.taymerni_yangilash)
        if self.qolgan_vaqt <= 0 and self.ishlayapti:
            self.root.after(0, self.davr_tugadi)

    def taymerni_yangilash(self):
        daqiqa = self.qolgan_vaqt // 60
        soniya = self.qolgan_vaqt % 60
        self.taymer_label.config(text=f"{daqiqa:02d}:{soniya:02d}")

    def davr_tugadi(self):
        self.ishlayapti = False
        if not self.tanaffusda:
            # Pomodoro tugadi — pomidor sonini oshiramiz
            idx = self.tanlangan_index()
            if idx is not None:
                self.vazifalar[idx].pomidorlar += 1
                self.saqlash()
                self.royxatni_yangilash()
            self.tanaffusda = True
            self.qolgan_vaqt = TANAFFUS_VAQT
            self.holat_label.config(text="☕ Tanaffus", fg="#00b894")
            self.taymer_label.config(fg="#00b894")
            self.taymerni_yangilash()
            messagebox.showinfo("Pomodoro tugadi!",
                                "🎉 Ajoyib ish!\nEndi 5 daqiqa dam oling.")
        else:
            # Tanaffus tugadi
            self.tanaffusda = False
            self.qolgan_vaqt = POMODORO_VAQT
            self.holat_label.config(text="Ish vaqti", fg="#636e72")
            self.taymer_label.config(fg="#d63031")
            self.taymerni_yangilash()
            messagebox.showinfo("Tanaffus tugadi",
                                "🚀 Yana ishlashga qaytamiz!")

    # ----------- SAQLASH / YUKLASH -----------
    def saqlash(self):
        with open(FAYL, "w", encoding="utf-8") as f:
            json.dump([v.to_dict() for v in self.vazifalar],
                      f, ensure_ascii=False, indent=2)

    def vazifalarni_yuklash(self):
        try:
            with open(FAYL, "r", encoding="utf-8") as f:
                ma = json.load(f)
                self.vazifalar = [Vazifa.from_dict(d) for d in ma]
        except FileNotFoundError:
            self.vazifalar = []
        except json.JSONDecodeError:
            self.vazifalar = []


# ===================== ISHGA TUSHIRISH =====================
if __name__ == "__main__":
    root = tk.Tk()
    app = PomodoroApp(root)
    root.mainloop()
