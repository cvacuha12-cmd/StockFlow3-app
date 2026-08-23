from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.camera import Camera
from kivy.clock import Clock
from kivy.storage.jsonstore import JsonStore
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen

from pyzbar.pyzbar import decode
from PIL import Image as PILImage
from datetime import datetime
import hashlib

Window.size = (400, 750)

# ========== ЭКРАН ВХОДА ==========
class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        layout = BoxLayout(orientation='vertical', padding=30, spacing=15)
        
        layout.add_widget(Label(text='📦', font_size=70, size_hint=(1, 0.15)))
        layout.add_widget(Label(
            text='StockFlow Pro',
            font_size=30,
            bold=True,
            size_hint=(1, 0.1)
        ))
        layout.add_widget(Label(
            text='Система учёта товаров',
            font_size=14,
            color=(0.6, 0.6, 0.6, 1),
            size_hint=(1, 0.06)
        ))
        
        layout.add_widget(Label(text='Логин:', font_size=16, size_hint=(1, 0.04), halign='left'))
        self.username_input = TextInput(
            font_size=18,
            multiline=False,
            size_hint=(1, 0.08),
            hint_text='admin'
        )
        layout.add_widget(self.username_input)
        
        layout.add_widget(Label(text='Пароль:', font_size=16, size_hint=(1, 0.04), halign='left'))
        self.password_input = TextInput(
            font_size=18,
            multiline=False,
            password=True,
            size_hint=(1, 0.08),
            hint_text='admin123'
        )
        layout.add_widget(self.password_input)
        
        self.error_label = Label(
            text='',
            font_size=13,
            color=(0.96, 0.26, 0.37, 1),
            size_hint=(1, 0.04)
        )
        layout.add_widget(self.error_label)
        
        login_btn = Button(
            text='ВОЙТИ',
            font_size=20,
            background_color=(0.54, 0.36, 0.96, 1),
            background_normal='',
            size_hint=(1, 0.1)
        )
        login_btn.bind(on_press=self.login)
        layout.add_widget(login_btn)
        
        self.add_widget(layout)
    
    def login(self, instance):
        app = App.get_running_app()
        username = self.username_input.text.strip()
        password = self.password_input.text
        
        user = app.verify_user(username, password)
        if user:
            app.current_user = user
            app.show_main_screen()
        else:
            self.error_label.text = '❌ Неверный логин или пароль'

# ========== ЭКРАН СКАНИРОВАНИЯ ==========
class ScanScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.scanning = False
        
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        layout.add_widget(Label(
            text='📷 Сканирование',
            font_size=24,
            bold=True,
            size_hint=(1, 0.07)
        ))
        
        # Камера
        self.camera = Camera(
            resolution=(640, 480),
            play=True,
            size_hint=(1, 0.6)
        )
        layout.add_widget(self.camera)
        
        # Статус
        self.status_label = Label(
            text='Наведите камеру на штрихкод',
            font_size=14,
            size_hint=(1, 0.05)
        )
        layout.add_widget(self.status_label)
        
        # Кнопки
        btn_row = BoxLayout(size_hint=(1, 0.1), spacing=10)
        
        scan_btn = Button(
            text='🔍 СКАНИРОВАТЬ',
            font_size=16,
            background_color=(0.54, 0.36, 0.96, 1),
            background_normal=''
        )
        scan_btn.bind(on_press=self.scan)
        btn_row.add_widget(scan_btn)
        
        back_btn = Button(
            text='⬅️ НАЗАД',
            font_size=16,
            background_color=(0.96, 0.26, 0.37, 1),
            background_normal=''
        )
        back_btn.bind(on_press=self.go_back)
        btn_row.add_widget(back_btn)
        
        layout.add_widget(btn_row)
        
        # Ручной ввод
        manual_btn = Button(
            text='⌨️ ВВЕСТИ ВРУЧНУЮ',
            font_size=14,
            size_hint=(1, 0.08),
            background_color=(0.3, 0.3, 0.3, 1),
            background_normal=''
        )
        manual_btn.bind(on_press=self.manual_input)
        layout.add_widget(manual_btn)
        
        self.add_widget(layout)
        
        # Автосканирование каждые 2 секунды
        Clock.schedule_interval(self.auto_scan, 2.0)
    
    def auto_scan(self, dt):
        if not self.scanning:
            self.scan(None)
    
    def scan(self, instance):
        if self.scanning:
            return
        
        self.scanning = True
        self.status_label.text = '⏳ Обработка...'
        
        try:
            texture = self.camera.texture
            if texture:
                pixels = texture.pixels
                size = texture.size
                
                img = PILImage.frombytes('RGBA', size, pixels)
                img = img.convert('L')
                
                barcodes = decode(img)
                
                if barcodes:
                    barcode_data = barcodes[0].data.decode('utf-8')
                    self.status_label.text = f'✅ Найден: {barcode_data}'
                    
                    app = App.get_running_app()
                    Clock.schedule_once(lambda dt: app.process_barcode(barcode_data), 0.5)
                else:
                    self.status_label.text = 'Наведите на штрихкод'
        except Exception as e:
            self.status_label.text = 'Ошибка сканирования'
        
        self.scanning = False
    
    def manual_input(self, instance):
        app = App.get_running_app()
        app.show_manual_input()
    
    def go_back(self, instance):
        self.camera.play = False
        app = App.get_running_app()
        app.show_main_screen()
    
    def stop_camera(self):
        self.camera.play = False

# ========== ОСНОВНОЕ ПРИЛОЖЕНИЕ ==========
class StockFlowApp(App):
    def build(self):
        self.title = 'StockFlow Pro'
        
        # Хранилище данных
        self.store = JsonStore('stockflow_data.json')
        self.users_store = JsonStore('users.json')
        
        # Пользователи
        if not self.users_store.exists('users'):
            self.users_store.put('users', data=[
                {
                    'id': 1,
                    'username': 'admin',
                    'password': self.hash_password('admin123'),
                    'role': 'admin',
                    'name': 'Администратор'
                },
                {
                    'id': 2,
                    'username': 'user1',
                    'password': self.hash_password('user123'),
                    'role': 'user',
                    'name': 'Пользователь'
                }
            ])
        
        self.users = self.users_store.get('users')['data']
        
        # Товары и операции
        if not self.store.exists('products'):
            self.store.put('products', data=[])
        if not self.store.exists('operations'):
            self.store.put('operations', data=[])
        
        self.products = self.store.get('products')['data']
        self.operations = self.store.get('operations')['data']
        
        self.current_user = None
        self.mode = 'receive'
        
        # Screen Manager
        self.sm = ScreenManager()
        
        self.login_screen = LoginScreen(name='login')
        self.scan_screen = ScanScreen(name='scan')
        
        self.sm.add_widget(self.login_screen)
        self.sm.add_widget(self.scan_screen)
        
        return self.sm
    
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_user(self, username, password):
        hashed = self.hash_password(password)
        for u in self.users:
            if u['username'] == username and u['password'] == hashed:
                return u
        return None
    
    def show_main_screen(self):
        self.sm.current = 'main'
        if not hasattr(self, 'main_screen'):
            self.create_main_screen()
        self.render_products()
    
    def create_main_screen(self):
        self.main_screen = Screen(name='main')
        
        layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        # Заголовок
        header = BoxLayout(size_hint=(1, 0.08))
        header.add_widget(Label(
            text='📦 StockFlow Pro',
            font_size=22,
            bold=True
        ))
        header.add_widget(Label(
            text=f"👤 {self.current_user['name']}" if self.current_user else '',
            font_size=12,
            color=(0.54, 0.36, 0.96, 1)
        ))
        layout.add_widget(header)
        
        # Статистика
        stats = BoxLayout(size_hint=(1, 0.06), spacing=10)
        self.stock_label = Label(
            text='✅ 0',
            font_size=16,
            color=(0.06, 0.73, 0.51, 1)
        )
        self.shipped_label = Label(
            text='📤 0',
            font_size=16,
            color=(0.96, 0.26, 0.37, 1)
        )
        stats.add_widget(self.stock_label)
        stats.add_widget(self.shipped_label)
        layout.add_widget(stats)
        
        # Режимы
        modes = BoxLayout(size_hint=(1, 0.08), spacing=10)
        
        self.btn_receive = Button(
            text='📥 ПРИЁМКА',
            font_size=16,
            background_color=(0.06, 0.73, 0.51, 1),
            background_normal=''
        )
        self.btn_receive.bind(on_press=lambda x: self.set_mode('receive'))
        modes.add_widget(self.btn_receive)
        
        self.btn_ship = Button(
            text='📤 ОТГРУЗКА',
            font_size=16,
            background_color=(0.3, 0.3, 0.3, 1),
            background_normal=''
        )
        self.btn_ship.bind(on_press=lambda x: self.set_mode('ship'))
        modes.add_widget(self.btn_ship)
        
        layout.add_widget(modes)
        
        # Кнопка сканирования
        scan_btn = Button(
            text='📷 СКАНИРОВАТЬ ЧЕРЕЗ КАМЕРУ',
            font_size=18,
            size_hint=(1, 0.12),
            background_color=(0.54, 0.36, 0.96, 1),
            background_normal=''
        )
        scan_btn.bind(on_press=lambda x: self.open_scanner())
        layout.add_widget(scan_btn)
        
        # Список товаров
        layout.add_widget(Label(
            text='📋 Товары на складе:',
            font_size=16,
            size_hint=(1, 0.05),
            halign='left'
        ))
        
        self.scroll = ScrollView(size_hint=(1, 0.35))
        self.products_layout = GridLayout(cols=1, spacing=3, size_hint_y=None)
        self.products_layout.bind(minimum_height=self.products_layout.setter('height'))
        self.scroll.add_widget(self.products_layout)
        layout.add_widget(self.scroll)
        
        # Кнопки внизу
        btn_row = BoxLayout(size_hint=(1, 0.08), spacing=5)
        
        history_btn = Button(
            text='📋 История',
            font_size=12,
            background_color=(0.3, 0.3, 0.3, 1),
            background_normal=''
        )
        history_btn.bind(on_press=self.show_history)
        btn_row.add_widget(history_btn)
        
        logout_btn = Button(
            text='🚪 Выйти',
            font_size=12,
            background_color=(0.96, 0.26, 0.37, 1),
            background_normal=''
        )
        logout_btn.bind(on_press=lambda x: self.logout())
        btn_row.add_widget(logout_btn)
        
        layout.add_widget(btn_row)
        
        self.main_screen.add_widget(layout)
        self.sm.add_widget(self.main_screen)
    
    def open_scanner(self):
        self.scan_screen.camera.play = True
        self.sm.current = 'scan'
    
    def process_barcode(self, barcode):
        found_product = None
        found_unit = None
        
        for p in self.products:
            for u in p['units']:
                if u['barcode'] == barcode:
                    found_product = p
                    found_unit = u
                    break
            if found_product:
                break
        
        if self.mode == 'receive':
            if found_product and found_unit:
                if found_unit['status'] == 'на складе':
                    self.show_popup('⚠️ Внимание', f"Товар уже на складе:\n{found_product['name']}")
                else:
                    found_unit['status'] = 'на складе'
                    self.add_operation('receive', barcode, found_product['name'])
                    self.show_popup('✅ Успех', f"Принят: {found_product['name']}")
            else:
                self.show_name_input(barcode)
        else:
            if not found_product:
                self.show_popup('❌ Ошибка', f"Товар не найден!\nБаркод {barcode}\nне был принят на склад")
            elif found_unit['status'] == 'отгружена':
                self.show_popup('⚠️ Внимание', f"Товар уже отгружен:\n{found_product['name']}")
            else:
                found_unit['status'] = 'отгружена'
                self.add_operation('ship', barcode, found_product['name'])
                self.show_popup('✅ Успех', f"Отгружен: {found_product['name']}")
        
        self.save_data()
        self.show_main_screen()
    
    def show_name_input(self, barcode):
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        content.add_widget(Label(
            text=f'Баркод: {barcode}\n\nВведите название товара:',
            font_size=16,
            halign='center'
        ))
        
        name_input = TextInput(font_size=18, multiline=False)
        content.add_widget(name_input)
        
        def save(instance):
            name = name_input.text.strip()
            if name:
                product = next((p for p in self.products if p['name'] == name), None)
                if not product:
                    product = {'name': name, 'units': []}
                    self.products.append(product)
                product['units'].append({'barcode': barcode, 'status': 'на складе'})
                self.add_operation('receive', barcode, name)
                self.save_data()
                popup.dismiss()
                self.show_main_screen()
        
        save_btn = Button(
            text='💾 СОХРАНИТЬ',
            font_size=16,
            size_hint=(1, 0.25),
            background_color=(0.06, 0.73, 0.51, 1),
            background_normal=''
        )
        save_btn.bind(on_press=save)
        content.add_widget(save_btn)
        
        popup = Popup(
            title='🆕 Новый товар',
            content=content,
            size_hint=(0.85, 0.5),
            auto_dismiss=False
        )
        name_input.bind(on_text_validate=save)
        popup.open()
    
    def show_manual_input(self):
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        content.add_widget(Label(
            text='Введите штрихкод:',
            font_size=16
        ))
        
        barcode_input = TextInput(font_size=18, multiline=False)
        content.add_widget(barcode_input)
        
        def submit(instance):
            barcode = barcode_input.text.strip()
            if barcode:
                popup.dismiss()
                self.process_barcode(barcode)
        
        btn = Button(
            text='ОК',
            font_size=16,
            size_hint=(1, 0.25),
            background_color=(0.54, 0.36, 0.96, 1),
            background_normal=''
        )
        btn.bind(on_press=submit)
        content.add_widget(btn)
        
        popup = Popup(
            title='⌨️ Ручной ввод',
            content=content,
            size_hint=(0.8, 0.35)
        )
        barcode_input.bind(on_text_validate=submit)
        popup.open()
    
    def show_popup(self, title, message):
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        content.add_widget(Label(text=message, font_size=16, halign='center'))
        
        btn = Button(
            text='ОК',
            font_size=16,
            size_hint=(1, 0.3),
            background_color=(0.54, 0.36, 0.96, 1),
            background_normal=''
        )
        
        popup = Popup(
            title=title,
            content=content,
            size_hint=(0.8, 0.4),
            auto_dismiss=False
        )
        btn.bind(on_press=popup.dismiss)
        content.add_widget(btn)
        popup.open()
    
    def set_mode(self, mode):
        self.mode = mode
        if mode == 'receive':
            self.btn_receive.background_color = (0.06, 0.73, 0.51, 1)
            self.btn_ship.background_color = (0.3, 0.3, 0.3, 1)
        else:
            self.btn_receive.background_color = (0.3, 0.3, 0.3, 1)
            self.btn_ship.background_color = (0.96, 0.26, 0.37, 1)
    
    def render_products(self):
        if not hasattr(self, 'products_layout'):
            return
        
        self.products_layout.clear_widgets()
        
        on_stock = 0
        shipped = 0
        
        for p in self.products:
            stock = len([u for u in p['units'] if u['status'] == 'на складе'])
            ship = len([u for u in p['units'] if u['status'] == 'отгружена'])
            on_stock += stock
            shipped += ship
            
            box = BoxLayout(
                orientation='vertical',
                padding=[10, 5],
                size_hint_y=None,
                height=55
            )
            box.add_widget(Label(
                text=p['name'],
                font_size=14,
                size_hint_y=0.5,
                halign='left'
            ))
            box.add_widget(Label(
                text=f'✅ {stock} на складе | 📤 {ship} отгружено',
                font_size=11,
                color=(0.5, 0.5, 0.5, 1),
                size_hint_y=0.5
            ))
            self.products_layout.add_widget(box)
        
        self.stock_label.text = f'✅ {on_stock}'
        self.shipped_label.text = f'📤 {shipped}'
    
    def add_operation(self, op_type, barcode, product_name):
        self.operations.append({
            'timestamp': datetime.now().isoformat(),
            'type': op_type,
            'barcode': barcode,
            'product': product_name,
            'user': self.current_user['name'] if self.current_user else '—'
        })
    
    def save_data(self):
        self.store.put('products', data=self.products)
        self.store.put('operations', data=self.operations)
    
    def show_history(self, instance):
        content = BoxLayout(orientation='vertical', padding=20)
        
        scroll = ScrollView()
        text = Label(
            text=self.get_history_text(),
            font_size=12,
            size_hint_y=None,
            halign='left'
        )
        text.bind(width=lambda s, w: setattr(s, 'text_size', (w, None)))
        scroll.add_widget(text)
        content.add_widget(scroll)
        
        btn = Button(
            text='ЗАКРЫТЬ',
            size_hint=(1, 0.1),
            background_color=(0.54, 0.36, 0.96, 1),
            background_normal=''
        )
        popup = Popup(
            title='📋 История операций',
            content=content,
            size_hint=(0.9, 0.8)
        )
        btn.bind(on_press=popup.dismiss)
        content.add_widget(btn)
        popup.open()
    
    def get_history_text(self):
        lines = []
        for op in reversed(self.operations[-100:]):
            emoji = '📥' if op['type'] == 'receive' else '📤'
            t = datetime.fromisoformat(op['timestamp']).strftime('%d.%m %H:%M')
            lines.append(f"{emoji} {t} | {op['product']} | {op.get('user', '—')}")
        return '\n'.join(lines) if lines else 'Нет операций'
    
    def logout(self):
        self.current_user = None
        self.sm.current = 'login'


if __name__ == '__main__':
    StockFlowApp().run()
