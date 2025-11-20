"""
Модуль графического интерфейса приложения.
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
import logging
from quote_generator import QuoteGenerator
from exceptions import QuoteGeneratorException


class QuoteGeneratorGUI:
    """Класс графического интерфейса приложения."""
    
    def __init__(self, root: tk.Tk):
        """
        Инициализация GUI.
        
        Args:
            root: Корневое окно tkinter
        """
        self.root = root
        self.root.title("Генератор цитат и фактов")
        self.root.geometry("1000x700")
        
        # Инициализация генератора
        self.generator = QuoteGenerator()
        
        # Настройка логирования
        self.setup_logging()
        
        # Создание интерфейса
        self.create_menu()
        self.create_widgets()
        
        # Обновление данных
        self.refresh_table()
        self.update_graph()
        self.update_log_display()
    
    def setup_logging(self):
        """Настройка системы логирования."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('activity.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info("Приложение запущено")
    
    def create_menu(self):
        """Создание меню приложения."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Меню "Файл"
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Обновить", command=self.refresh_all)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.on_exit)
        
        # Меню "Помощь"
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Помощь", menu=help_menu)
        help_menu.add_command(label="О программе", command=self.show_about)
        help_menu.add_command(label="Справка", command=self.show_help)
    
    def create_widgets(self):
        """Создание виджетов интерфейса."""
        # Основной контейнер
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Настройка весов для растягивания
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Левая панель - ввод данных
        left_panel = ttk.LabelFrame(main_frame, text="Добавление цитаты/факта", padding="10")
        left_panel.grid(row=0, column=0, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        # Поле ввода темы
        ttk.Label(left_panel, text="Тема:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.topic_entry = ttk.Entry(left_panel, width=25)
        self.topic_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        # Поле ввода содержимого
        ttk.Label(left_panel, text="Содержимое:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.content_text = scrolledtext.ScrolledText(left_panel, width=25, height=5)
        self.content_text.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        # Кнопки
        button_frame = ttk.Frame(left_panel)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Добавить", command=self.add_quote).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Случайная цитата", command=self.show_random_quote).pack(side=tk.LEFT, padx=5)
        
        # Центральная панель - таблица
        center_panel = ttk.LabelFrame(main_frame, text="Цитаты и факты", padding="10")
        center_panel.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        center_panel.columnconfigure(0, weight=1)
        center_panel.rowconfigure(0, weight=1)
        
        # Выбор темы для таблицы
        topic_frame = ttk.Frame(center_panel)
        topic_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(topic_frame, text="Тема:").pack(side=tk.LEFT, padx=5)
        self.topic_combo = ttk.Combobox(topic_frame, state="readonly", width=20)
        self.topic_combo.pack(side=tk.LEFT, padx=5)
        self.topic_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_table())
        
        # Таблица
        table_frame = ttk.Frame(center_panel)
        table_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        
        # Treeview для таблицы
        columns = ("№", "Содержимое", "Дата")
        self.table = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)
        
        for col in columns:
            self.table.heading(col, text=col)
            self.table.column(col, width=100)
        
        self.table.column("Содержимое", width=300)
        
        scrollbar_table = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.table.yview)
        self.table.configure(yscrollcommand=scrollbar_table.set)
        
        self.table.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar_table.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Правая панель - график и логи
        right_panel = ttk.Frame(main_frame)
        right_panel.grid(row=0, column=2, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        right_panel.columnconfigure(0, weight=1)
        right_panel.rowconfigure(0, weight=1)
        right_panel.rowconfigure(1, weight=1)
        
        # График активности
        graph_frame = ttk.LabelFrame(right_panel, text="График активности", padding="10")
        graph_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        graph_frame.columnconfigure(0, weight=1)
        graph_frame.rowconfigure(0, weight=1)
        
        self.fig, self.ax = plt.subplots(figsize=(4, 3))
        self.canvas = FigureCanvasTkAgg(self.fig, graph_frame)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Логи активности
        log_frame = ttk.LabelFrame(right_panel, text="Логи активности", padding="10")
        log_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_display = scrolledtext.ScrolledText(log_frame, width=30, height=10)
        self.log_display.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    def add_quote(self):
        """Добавление новой цитаты/факта."""
        try:
            topic = self.topic_entry.get()
            content = self.content_text.get("1.0", tk.END).strip()
            
            self.generator.add_quote(topic, content)
            
            # Очистка полей
            self.topic_entry.delete(0, tk.END)
            self.content_text.delete("1.0", tk.END)
            
            # Обновление интерфейса
            self.refresh_table()
            self.update_graph()
            self.update_log_display()
            
            self.logger.info(f"Добавлена цитата в тему '{topic}'")
            messagebox.showinfo("Успех", "Цитата/факт успешно добавлен!")
            
        except QuoteGeneratorException as e:
            self.logger.error(f"Ошибка при добавлении: {e}")
            messagebox.showerror("Ошибка", str(e))
        except Exception as e:
            self.logger.error(f"Неожиданная ошибка: {e}")
            messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")
    
    def show_random_quote(self):
        """Показать случайную цитату."""
        try:
            topic = self.topic_combo.get()
            # Если выбрано "Все темы" или пусто, передаем None
            if not topic or topic == 'Все темы':
                topic = None
            quote = self.generator.get_random_quote(topic)
            
            if quote:
                # Определяем тему для отображения
                display_topic = topic if topic else 'Все темы'
                messagebox.showinfo(
                    "Случайная цитата/факт",
                    f"Тема: {display_topic}\n\n{quote['content']}"
                )
                self.update_graph()
                self.update_log_display()
            else:
                messagebox.showwarning("Предупреждение", "Нет доступных цитат/фактов")
                
        except QuoteGeneratorException as e:
            self.logger.error(f"Ошибка при получении цитаты: {e}")
            messagebox.showerror("Ошибка", str(e))
    
    def refresh_table(self):
        """Обновление таблицы с цитатами."""
        # Очистка таблицы
        for item in self.table.get_children():
            self.table.delete(item)
        
        # Обновление списка тем
        topics = self.generator.get_topics()
        self.topic_combo['values'] = ['Все темы'] + topics
        
        # Если список тем пуст, устанавливаем "Все темы" по умолчанию
        if not self.topic_combo.get():
            self.topic_combo.set('Все темы')
        
        # Получение выбранной темы
        selected_topic = self.topic_combo.get()
        if not selected_topic or selected_topic == 'Все темы':
            # Показать все цитаты
            if topics:
                row_num = 1
                for topic in topics:
                    try:
                        quotes = self.generator.get_quotes_by_topic(topic)
                        for quote in quotes:
                            date = datetime.fromisoformat(quote['date']).strftime('%Y-%m-%d %H:%M')
                            self.table.insert("", tk.END, values=(row_num, quote['content'], date))
                            row_num += 1
                    except QuoteGeneratorException:
                        pass
        else:
            # Показать цитаты выбранной темы
            try:
                quotes = self.generator.get_quotes_by_topic(selected_topic)
                for idx, quote in enumerate(quotes, 1):
                    date = datetime.fromisoformat(quote['date']).strftime('%Y-%m-%d %H:%M')
                    self.table.insert("", tk.END, values=(idx, quote['content'], date))
            except QuoteGeneratorException:
                pass
    
    def update_graph(self):
        """Обновление графика активности."""
        self.ax.clear()
        
        stats = self.generator.get_activity_stats()
        
        if stats:
            topics = list(stats.keys())
            counts = list(stats.values())
            
            self.ax.bar(topics, counts, color='skyblue', edgecolor='navy', alpha=0.7)
            self.ax.set_xlabel('Тема')
            self.ax.set_ylabel('Количество действий')
            self.ax.set_title('Активность по темам')
            self.ax.tick_params(axis='x', rotation=45)
            
            plt.tight_layout()
        
        self.canvas.draw()
    
    def update_log_display(self):
        """Обновление отображения логов."""
        self.log_display.delete("1.0", tk.END)
        
        # Показать последние 20 записей
        recent_logs = self.generator.activity_log[-20:]
        
        for entry in reversed(recent_logs):
            timestamp = datetime.fromisoformat(entry['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
            action = entry['action']
            topic = entry['topic']
            content = entry['content']
            
            log_line = f"[{timestamp}] {action.upper()}: {topic} - {content}\n"
            self.log_display.insert(tk.END, log_line)
    
    def refresh_all(self):
        """Обновление всех компонентов интерфейса."""
        self.refresh_table()
        self.update_graph()
        self.update_log_display()
        self.logger.info("Интерфейс обновлен")
    
    def show_about(self):
        """Показать информацию о программе."""
        messagebox.showinfo(
            "О программе",
            "Генератор цитат и фактов\n\n"
            "Версия 1.0\n\n"
            "Приложение для управления и генерации цитат и фактов по различным темам."
        )
    
    def show_help(self):
        """Показать справку."""
        help_text = """
СПРАВКА ПО ПРИЛОЖЕНИЮ

1. Добавление цитаты/факта:
   - Введите тему в поле "Тема"
   - Введите содержимое в поле "Содержимое"
   - Нажмите кнопку "Добавить"

2. Просмотр цитат:
   - Выберите тему в выпадающем списке
   - Таблица автоматически обновится

3. Случайная цитата:
   - Нажмите кнопку "Случайная цитата"
   - Если выбрана тема, будет показана цитата из этой темы
   - Если тема не выбрана, будет показана цитата из всех тем

4. График активности:
   - Отображает количество действий по каждой теме
   - Обновляется автоматически

5. Логи активности:
   - Показывает последние 20 действий
   - Обновляется автоматически

6. Меню:
   - Файл > Обновить - обновить все компоненты
   - Файл > Выход - закрыть приложение
   - Помощь > О программе - информация о приложении
   - Помощь > Справка - эта справка
        """
        messagebox.showinfo("Справка", help_text)
    
    def on_exit(self):
        """Обработка выхода из приложения."""
        if messagebox.askokcancel("Выход", "Вы уверены, что хотите выйти?"):
            self.logger.info("Приложение закрыто")
            # Закрываем соединение с БД
            if hasattr(self, 'generator'):
                self.generator.close()
            self.root.quit()
            self.root.destroy()

