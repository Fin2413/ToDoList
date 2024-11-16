import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from tkcalendar import Calendar
import sqlite3

# Создаем базу данных и таблицу для хранения задач
def init_db():
    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            task TEXT NOT NULL,
            completed INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

class TaskManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Менеджер задач")
        self.root.geometry("700x500")

        # Устанавливаем стиль
        self.style = ttk.Style()
        self.style.configure("TButton", font=("Arial", 10), padding=5)
        self.style.configure("TLabel", font=("Arial", 12))

        # Верхняя панель с календарем и задачами
        top_frame = ttk.Frame(self.root, padding=10)
        top_frame.pack(side=tk.TOP, fill=tk.X)

        # Календарь
        self.calendar = Calendar(top_frame, selectmode="day", date_pattern="dd.mm.yyyy")
        self.calendar.pack(side=tk.LEFT, padx=10)
        self.calendar.bind("<<CalendarSelected>>", self.update_task_list)

        # Поле ввода задачи и кнопка
        entry_frame = ttk.Frame(top_frame, padding=10)
        entry_frame.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        self.task_entry = ttk.Entry(entry_frame, width=40, font=("Arial", 12))
        self.task_entry.pack(pady=5, padx=5)

        self.add_button = ttk.Button(entry_frame, text="Добавить задачу", command=self.add_task)
        self.add_button.pack(pady=5, padx=5)

        # Панель задач
        self.tasks_frame = ttk.Frame(self.root, padding=10)
        self.tasks_frame.pack(fill=tk.BOTH, expand=True)

        self.update_task_list()

    def add_task(self):
        task = self.task_entry.get().strip()
        date = self.calendar.get_date()
        if not task:
            messagebox.showwarning("Ошибка", "Введите задачу!")
            return

        conn = sqlite3.connect("tasks.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tasks (date, task) VALUES (?, ?)", (date, task))
        conn.commit()
        conn.close()

        self.task_entry.delete(0, tk.END)
        self.update_task_list()
        messagebox.showinfo("Успех", f"Задача добавлена на {date}!")

    def toggle_task(self, task_id, completed_var, checkbutton):
        new_status = completed_var.get()
        conn = sqlite3.connect("tasks.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE tasks SET completed = ? WHERE id = ?", (new_status, task_id))
        conn.commit()
        conn.close()

        # Обновление шрифта (зачёркивание текста)
        font = ("Arial", 10, "overstrike") if new_status else ("Arial", 10)
        checkbutton.config(font=font)

    def delete_task(self, task_id):
        response = messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить задачу?")
        if response:
            conn = sqlite3.connect("tasks.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            conn.commit()
            conn.close()

            self.update_task_list()
            messagebox.showinfo("Удалено", "Задача удалена!")

    def update_task_list(self, event=None):
        # Очистка предыдущих виджетов
        for widget in self.tasks_frame.winfo_children():
            widget.destroy()

        selected_date = self.calendar.get_date()

        # Получение задач из базы данных
        conn = sqlite3.connect("tasks.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, task, completed FROM tasks WHERE date = ?", (selected_date,))
        tasks_for_date = cursor.fetchall()
        conn.close()

        ttk.Label(self.tasks_frame, text=f"Задачи на {selected_date}:", style="TLabel").pack(anchor="w")
        if not tasks_for_date:
            ttk.Label(self.tasks_frame, text="Нет задач", style="TLabel").pack(anchor="w", pady=5)
        else:
            for task_id, task, completed in tasks_for_date:
                task_frame = ttk.Frame(self.tasks_frame)
                task_frame.pack(anchor="w", fill=tk.X, pady=2)

                completed_var = tk.IntVar(value=completed)
                font = ("Arial", 10, "overstrike") if completed else ("Arial", 10)

                # Создаем Checkbutton сначала
                check_button = tk.Checkbutton(
                    task_frame,
                    text=task,
                    variable=completed_var,
                    font=font
                )
                check_button.pack(side=tk.LEFT, anchor="w", pady=2)

                # Затем передаем его в замыкание
                check_button.config(
                    command=lambda tid=task_id, var=completed_var, cb=check_button: self.toggle_task(tid, var, cb)
                )

                # Кнопка для удаления
                delete_button = ttk.Button(
                    task_frame,
                    text="Удалить",
                    command=lambda tid=task_id: self.delete_task(tid),
                    style="TButton"
                )
                delete_button.pack(side=tk.RIGHT, padx=5)

# Инициализация базы данных и запуск приложения
if __name__ == "__main__":
    init_db()
    root = tk.Tk()
    app = TaskManager(root)
    root.mainloop()
