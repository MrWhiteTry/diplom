import sqlite3  # импорт модуля SQLite
import tkinter as tk  # импорт библиотеки tkinter
from tkinter import ttk  # импорт модуля TTk
from tkinter.filedialog import askopenfilename  # Импорт системной функции
from datetime import date  # # импорт захвата даты
from tkinter import messagebox as mb  # импорт окна сообщений
import os


class Main(tk.Frame):
    def __init__(self, root):
        super().__init__(root)
        self.init_main()
        self.db = db
        self.view_records()

    def init_main(self):  # главное окно
        toolbar = tk.Frame(bg='#d7d8e0', bd=2)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        self.add_img = tk.PhotoImage('')
        btn_open_dialog = tk.Button(toolbar, text='Добавить позицию', command=self.open_dialog,
                                    bg='#d7d8e0', bd=0, compound=tk.TOP, image=self.add_img)
        btn_open_dialog.pack(side=tk.LEFT)

        self.update = tk.PhotoImage('')
        btn_open_dialog = tk.Button(toolbar, text='обновить базу', command=self.view_records,
                                    bg='#d7d8e0', bd=0, compound=tk.TOP, image=self.update)
        btn_open_dialog.pack(side=tk.RIGHT)

        self.update_img = tk.PhotoImage('')
        btn_edit_dialog = tk.Button(toolbar, text='Редактировать', command=self.open_update_dialog,
                                    bg='#d7d8e0', bd=0, compound=tk.TOP, image=self.update_img)
        btn_edit_dialog.pack(side=tk.LEFT)

        self.search_img = tk.PhotoImage('')
        btn_open_search_dialog = tk.Button(toolbar, text='Поиск', command=self.open_search_dialog,
                                           bg='#d7d8e0', bd=0, image=self.search_img, compound=tk.TOP)
        btn_open_search_dialog.pack(side=tk.RIGHT)

        self.tree = ttk.Treeview(self, columns=('id', 'prefix', 'number', 'postfix', 'zavod',
                                                'quantity', 'cons_date', 'ubd_date'), height=15, show='headings')

        # vscrollbar = tk.Scrollbar(self, orient=tk.VERTICAL)
        # vscrollbar.pack(fill=tk.Y, side=tk.RIGHT, expand=tk.FALSE)

        # btn_open = tk.Button(self, text='Открыть изображение', command=self.open_file, bg='#d7d8e0')
        # btn_open.pack(side=tk.LEFT)

        btn_open = tk.Button(self, text='Распечатать изображение', command=self.print_file, bg='#d7d8e0')
        btn_open.pack(side=tk.BOTTOM)
        
        # функция сортровки при нажатии на заголовок столбца
        def treeview_sort_column(tv, col, reverse, key=str):
            l = [(tv.set(k, col), k) for k in tv.get_children()]
            l.sort(reverse=reverse, key=lambda t: key(t[0]))

            for index, (val, k) in enumerate(l):
                tv.move(k, '', index)

            tv.heading(col, command=lambda: treeview_sort_column(tv, col, not reverse, key=key))

        self.tree.column('id', width=30, anchor=tk.CENTER)
        self.tree.column('prefix', width=60, anchor=tk.CENTER)
        self.tree.column('number', width=150, anchor=tk.CENTER)
        self.tree.column('postfix', width=50, anchor=tk.CENTER)
        self.tree.column('zavod', width=80, anchor=tk.CENTER)
        self.tree.column('quantity', width=50, anchor=tk.CENTER)
        self.tree.column('cons_date', width=100, anchor=tk.CENTER)
        self.tree.column('ubd_date', width=100, anchor=tk.CENTER)

        self.tree.heading('id', text='ID', command=lambda: treeview_sort_column(self.tree, 'id', False, key=int))
        self.tree.heading('prefix', text='Префикс', command=lambda: treeview_sort_column(self.tree, "prefix", False))
        self.tree.heading('number', text='Номенклатура', command=lambda: self.order_by_num())
        self.tree.heading('postfix', text='Суфикс', command=lambda: treeview_sort_column(self.tree, "postfix", False))
        self.tree.heading('zavod', text='Завод', command=lambda: treeview_sort_column(self.tree, "zavod", False))
        self.tree.heading('quantity', text='Ящ норма', command=lambda: treeview_sort_column(self.tree, "quantity", False, key=int))
        self.tree.heading('cons_date', text='Дата консервации', command=lambda: treeview_sort_column(self.tree, "cons_date", False))
        self.tree.heading('ubd_date', text='Дата введения', command=lambda: treeview_sort_column(self.tree, "ubd_date", False))

        self.tree.pack()
        Login()

    # def open_file(self):
    #     item = self.tree.item(self.tree.focus())
    #     url = item['values'][8]
    #     os.startfile(url)
    
    # Кнопка вывода файла на печать
    def print_file(self):
        item = self.tree.item(self.tree.focus())
        url = item['values'][8]
        try:
            os.startfile(url, 'print')
        except OSError:
            mb.showerror("Файл не найден", "Указанный файл был редактирован или перемещён")
            
    # Добавляемых в таблицу новых данных
    def records(self, prefix, number, postfix, zavod, quantity, cons_date, ubd_date, url):
        if quantity.isdigit() and number.isalnum():
            self.db.insert_data(prefix, number, postfix, zavod, quantity, cons_date, ubd_date, url)
            self.view_records()
        else:
            mb.showerror("некорректные данные ввода", "Номенклатура может содержать только буквы и цифры.\n"
                                                      " Количество может содержать только цифры.")
    
    # функция редактирования записи в таблице
    def update_record(self, prefix, number, postfix, zavod, quantity, cons_date, ubd_date, url):
        self.db.c.execute('''UPDATE pasports SET prefix=?, number=?, postfix=?,zavod=?,
        quantity=?, cons_date=?,ubd_date=?, url=? WHERE id=?''',
                          (prefix, number, postfix, zavod, quantity, cons_date, ubd_date, url,
                           self.tree.set(self.tree.selection()[0], '#1')))
        self.db.conn.commit()
        self.view_records()

    # Вывод таблицы
    def view_records(self):
        self.db.c.execute('''SELECT * FROM pasports''')
        [self.tree.delete(i) for i in self.tree.get_children()]
        [self.tree.insert('', 'end', values=row) for row in self.db.c.fetchall()]

    # Сортировка с перечитыванием БД
    def order_by_num(self):
        self.db.c.execute('''SELECT * FROM pasports ORDER BY number''')
        [self.tree.delete(i) for i in self.tree.get_children()]
        [self.tree.insert('', 'end', values=row) for row in self.db.c.fetchall()]

    # Поиск по номенклатуре
    def search(self, number):
        self.db.c.execute(f"SELECT * FROM pasports WHERE number = '{number}'")
        [self.tree.delete(i) for i in self.tree.get_children()]
        [self.tree.insert('', 'end', values=row) for row in self.db.c.fetchall()]

    # def delete_all_records(self):
    #     self.db.c.execute('''DELETE FROM finance''')
    #     self.db.conn.commit()
    #     self.view_records()

    def open_dialog(self):
        Child()  # вызов дочернего окна

    def open_update_dialog(self):
        Update()

    def open_search_dialog(self):
        Search_win()

    def mainwindow_destroy(self):
        self.destroy()


class Login(tk.Toplevel):
    def __init__(self):
        super().__init__(root)
        self.init_login()

    def init_login(self):
        self.title('Войдите в систему')
        self.geometry('300x110+400+300')
        self.resizable(False, False)

        label_login = tk.Label(self, text='Введите логин:')
        label_login.place(x=50, y=10)
        label_password = tk.Label(self, text='Введите пароль:')
        label_password.place(x=50, y=40)

        entry_login = ttk.Entry(self)
        entry_login.place(x=150, y=10)
        entry_password = ttk.Entry(self, show="*")
        entry_password.place(x=150, y=40)

        def chek():
            if entry_login.get() != 'УСПК' and entry_password != '123':
                mb.showerror("Ошибка", "Не верно введены «Имя пользователя» или «пароль»")
            else:
                self.destroy()

        btn_cancel = ttk.Button(self, text='войти', command=chek)
        btn_cancel.place(x=130, y=70)

        self.grab_set()  # перехват всех событий, происходящих в приложении
        self.focus_set()  # захват и удержание фокуса
        self.wait_window()


# Дочернее окно для добавления и редактирования сертификатов
class Child(tk.Toplevel):
    def __init__(self):
        super().__init__(root)
        self.init_child()
        self.view = app

    def init_child(self):
        self.title('Добавить Паспорт')
        self.geometry('450x340+400+300')
        self.resizable(False, False)

        label_prefix = tk.Label(self, text='Префикс:')
        label_prefix.place(x=50, y=50)
        label_number = tk.Label(self, text='Номенклатура:')
        label_number.place(x=50, y=80)
        label_postfix = tk.Label(self, text='Суфикс:')
        label_postfix.place(x=50, y=110)
        label_zavod = tk.Label(self, text='Завод:')
        label_zavod.place(x=50, y=140)
        label_quantity = tk.Label(self, text='Ящ.норма:')
        label_quantity.place(x=50, y=170)
        label_cons_date = tk.Label(self, text='дата конс:')
        label_cons_date.place(x=50, y=200)
        label_ubd_date = tk.Label(self, text='дата ввода:')
        label_ubd_date.place(x=50, y=230)
        label_url = tk.Label(self, text='Изображение:')
        label_url.place(x=50, y=260)


        self.entry_prefix = ttk.Entry(self)
        self.entry_prefix.place(x=200, y=50)
        self.entry_number = ttk.Entry(self)
        self.entry_number.place(x=200, y=80)
        self.entry_postfix = ttk.Entry(self)
        self.entry_postfix.place(x=200, y=110)
        self.entry_zavod = ttk.Entry(self)
        self.entry_zavod.place(x=200, y=140)
        self.entry_quantity = ttk.Entry(self)
        self.entry_quantity.place(x=200, y=170)
        self.entry_cons_date = ttk.Entry(self)
        self.entry_cons_date.place(x=200, y=200)
        self.entry_ubd_date = ttk.Entry(self)
        self.entry_ubd_date.place(x=200, y=230)
        self.entry_ubd_date.insert(0, date.today())
        self.entry_url = ttk.Entry(self)
        self.entry_url.place(x=200, y=260)

        btn_cancel = ttk.Button(self, text='Закрыть', command=self.destroy)
        btn_cancel.place(x=220, y=300)

        def add_img():
            self.entry_url.insert(0, askopenfilename())

        btn_img = ttk.Button(self, text='Указать', command=add_img)
        btn_img.place(x=350, y=257)
        
        # захват введённых данных и передача их в функцию добавления
        self.btn_ok = ttk.Button(self, text='Добавить')
        self.btn_ok.place(x=120, y=300)
        self.btn_ok.bind('<Button-1>', lambda event: self.view.records(self.entry_prefix.get(),
                                                                       self.entry_number.get(),
                                                                       self.entry_postfix.get(),
                                                                       self.entry_zavod.get(),
                                                                       self.entry_quantity.get(),
                                                                       self.entry_cons_date.get(),
                                                                       self.entry_ubd_date.get(),
                                                                       self.entry_url.get()))

        self.grab_set()  # перехват всех событий, происходящих в приложении
        self.focus_set()  # захват и удержание фокуса

# захват введённых данных из Дочернего окна и передача их в функцию редактирования записи таблицы
class Update(Child):
    def __init__(self):
        super().__init__()
        self.init_edit()
        self.view = app

    def init_edit(self):
        self.title('Редактировать позицию')
        btn_edit = ttk.Button(self, text='Редактировать')
        btn_edit.place(x=120, y=300)
        btn_edit.bind('<Button-1>', lambda event: self.view.update_record(self.entry_prefix.get(),
                                                                          self.entry_number.get(),
                                                                          self.entry_postfix.get(),
                                                                          self.entry_zavod.get(),
                                                                          self.entry_quantity.get(),
                                                                          self.entry_cons_date.get(),
                                                                          self.entry_ubd_date.get(),
                                                                          self.entry_url.get()))

        self.btn_ok.destroy()


class Search_win(tk.Toplevel):
    def __init__(self):
        super().__init__()
        self.init_search()
        self.view = app

    def init_search(self):
        self.title('Посик сертификата')
        self.geometry('300x110+400+300')
        self.resizable(False, False)

        label_number = tk.Label(self, text='Введите номенклатуру:')
        label_number.place(x=20, y=10)

        entry_number = ttk.Entry(self)
        entry_number.place(x=160, y=10)

        def end_search():
            self.view.search(entry_number.get())
            self.destroy()

        self.title('Поиск')
        btn_edit = ttk.Button(self, text='Найти', command=end_search)
        btn_edit.place(x=120, y=60)

        self.grab_set()  # перехват всех событий, происходящих в приложении
        self.focus_set()  # захват и удержание фокуса

# Класс создания таблицы БД при первом запуске и функция добавления данных
class DB:
    def __init__(self):
        self.conn = sqlite3.connect('pasport.db')
        self.c = self.conn.cursor()
        self.c.execute('CREATE TABLE IF NOT EXISTS pasports'
                       '    (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,'
                       '    prefix TEXT,'
                       '    number INT,'
                       '    postfix TEXT,'
                       '    zavod TEXT,'
                       '    quantity NUMBER,'
                       '    cons_date DATE,'
                       '    ubd_date DATE,'
                       '    url TEXT'
                       '    )')
        self.conn.commit()
        
    # функция добавления новой строки в таблицу
    def insert_data(self, prefix, number, postfix, zavod, quantity, cons_date, ubd_date, url):
        self.c.execute(f"SELECT * FROM pasports WHERE url = '{url}'")
        if self.c.fetchone() is None:
            self.c.execute('INSERT INTO pasports (prefix, number, postfix, zavod, quantity, cons_date, ubd_date, '
                       'url) VALUES(?,?,?,?,?,?,?,?)',
                       (prefix, number, postfix, zavod, quantity, cons_date, ubd_date, url))
            self.conn.commit()
        else:
            for check in self.c.execute(f"SELECT * FROM pasports WHERE url = '{url}'"):
                mb.showerror("Изображение повторяется!", "Указанный паспорт уже используется как - " + str(check))


if __name__ == "__main__":
    root = tk.Tk()  # корневое окно программы
    db = DB()  # экземпляр класса DB
    app = Main(root)
    app.pack()
    root.title("Сертификаты соответствия")  # название окна
    root.geometry("700x450+350+200")  # размеры окна
    root.resizable(False, False)  # фиксация окна по обеим осям
    root.mainloop()  # запуск главного цикла обработки событий
