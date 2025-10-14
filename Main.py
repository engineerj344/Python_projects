from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDRectangleFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.list import OneLineListItem, TwoLineListItem
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.menu import MDDropdownMenu
from kivy.lang import Builder
from kivy.clock import Clock
import sqlite3
import datetime

KV = '''
MDBoxLayout:
    orientation: 'vertical'
    
    MDTopAppBar:
        title: "Expense Tracker"
        elevation: 4
        right_action_items: [['chart-box', lambda x: app.show_stats()], ['delete', lambda x: app.clear_all_data()]]
    
    MDBoxLayout:
        orientation: 'vertical'
        padding: '20dp'
        spacing: '15dp'
        
        MDLabel:
            id: total_label
            text: 'Total Spent: $0.00'
            halign: 'center'
            font_style: 'H5'
            theme_text_color: 'Primary'
            
        MDBoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: '48dp'
            spacing: '10dp'
            
            MDRaisedButton:
                text: 'Add Expense'
                on_release: app.show_add_dialog()
                size_hint_x: 0.6
                
            MDRaisedButton:
                text: 'Filter'
                on_release: app.show_category_menu()
                size_hint_x: 0.4
        
        ScrollView:
            MDList:
                id: expense_list
                
    MDBoxLayout:
        size_hint_y: None
        height: '80dp'
        padding: '20dp'
        
        MDRaisedButton:
            text: "ADD EXPENSE"
            icon: "plus"
            on_release: app.show_add_dialog()
'''

class ExpenseTrackerApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None
        self.menu = None
        self.current_filter = "All"
        self.categories = ["Food", "Transport", "Shopping", "Bills", "Entertainment", "Other"]

    def build(self):
        self.theme_cls.primary_palette = "Teal"
        self.theme_cls.theme_style = "Light"
        self.db_conn = sqlite3.connect('expenses.db', check_same_thread=False)
        self.init_database()
        return Builder.load_string(KV)
    
    def init_database(self):
        cursor = self.db_conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL,
                category TEXT,
                description TEXT,
                date TEXT
            )
        ''')
        self.db_conn.commit()
    
    def show_add_dialog(self):
        content = MDBoxLayout(orientation='vertical', spacing='15dp', size_hint_y=None, height='280dp')
        
        amount_input = MDTextField(
            hint_text='Amount', 
            input_filter='float',
            helper_text="Enter amount in USD",
            helper_text_mode="on_focus"
        )
        
        category_input = MDTextField(
            hint_text='Category',
            helper_text="Choose or enter category"
        )
        
        desc_input = MDTextField(
            hint_text='Description (optional)',
            helper_text="What was this expense for?"
        )
        
        content.add_widget(amount_input)
        content.add_widget(category_input)
        content.add_widget(desc_input)
        
        self.dialog = MDDialog(
            title="Add New Expense",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    theme_text_color="Custom",
                    text_color=self.theme_cls.primary_color,
                    on_release=lambda x: self.dialog.dismiss()
                ),
                MDFlatButton(
                    text="SAVE",
                    theme_text_color="Custom",
                    text_color=self.theme_cls.primary_color,
                    on_release=lambda x: self.save_expense(amount_input, category_input, desc_input)
                ),
            ],
            size_hint=(0.8, None)
        )
        self.dialog.open()
    
    def save_expense(self, amount_input, category_input, desc_input):
        amount = amount_input.text.strip()
        category = category_input.text.strip() or "Other"
        description = desc_input.text.strip()
        
        if not amount:
            return
        
        try:
            cursor = self.db_conn.cursor()
            date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute(
                "INSERT INTO expenses (amount, category, description, date) VALUES (?, ?, ?, ?)",
                (float(amount), category, description, date)
            )
            self.db_conn.commit()
            self.dialog.dismiss()
            self.dialog = None
            self.load_expenses()
            
        except ValueError:
            pass  # Invalid amount
        except Exception as e:
            print(f"Error: {e}")
    
    def show_category_menu(self):
        menu_items = [{"text": "All Categories", "viewclass": "OneLineListItem", "on_release": lambda x="All": self.set_filter(x)}]
        
        for category in self.categories:
            menu_items.append({
                "text": category,
                "viewclass": "OneLineListItem", 
                "on_release": lambda x=category: self.set_filter(x)
            })
        
        self.menu = MDDropdownMenu(
            caller=self.root.ids.expense_list,
            items=menu_items,
            width_mult=4
        )
        self.menu.open()
    
    def set_filter(self, category):
        self.current_filter = category
        self.menu.dismiss()
        self.load_expenses()
    
    def show_stats(self):
        cursor = self.db_conn.cursor()
        cursor.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category")
        stats = cursor.fetchall()
        
        content = MDBoxLayout(orientation='vertical', spacing='10dp', size_hint_y=None)
        content.height = len(stats) * 50 + 100
        
        content.add_widget(MDLabel(
            text="Expense Statistics",
            halign="center",
            font_style="H6"
        ))
        
        total_all = 0
        for category, total in stats:
            total_all += total
            content.add_widget(MDLabel(
                text=f"{category}: ${total:.2f}",
                halign="center"
            ))
        
        content.add_widget(MDLabel(
            text=f"Total: ${total_all:.2f}",
            halign="center",
            font_style="Subtitle1"
        ))
        
        stats_dialog = MDDialog(
            title="Category Breakdown",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text="CLOSE",
                    on_release=lambda x: stats_dialog.dismiss()
                ),
            ],
        )
        stats_dialog.open()
    
    def clear_all_data(self):
        confirm_dialog = MDDialog(
            title="Clear All Data?",
            text="This will delete all your expenses. This action cannot be undone.",
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    on_release=lambda x: confirm_dialog.dismiss()
                ),
                MDFlatButton(
                    text="DELETE ALL",
                    theme_text_color="Custom",
                    text_color=(1, 0, 0, 1),
                    on_release=lambda x: self.confirm_clear_data(confirm_dialog)
                ),
            ],
        )
        confirm_dialog.open()
    
    def confirm_clear_data(self, dialog):
        cursor = self.db_conn.cursor()
        cursor.execute("DELETE FROM expenses")
        self.db_conn.commit()
        dialog.dismiss()
        self.load_expenses()
    
    def on_start(self):
        Clock.schedule_once(lambda dt: self.load_expenses())
    
    def load_expenses(self):
        if not hasattr(self, 'root') or not self.root:
            return
            
        expense_list = self.root.ids.expense_list
        total_label = self.root.ids.total_label
        
        expense_list.clear_widgets()
        
        cursor = self.db_conn.cursor()
        
        if self.current_filter == "All":
            cursor.execute("SELECT * FROM expenses ORDER BY date DESC")
        else:
            cursor.execute("SELECT * FROM expenses WHERE category = ? ORDER BY date DESC", (self.current_filter,))
        
        expenses = cursor.fetchall()
        
        total = 0
        if not expenses:
            item = OneLineListItem(text="No expenses yet. Tap ADD EXPENSE to add your first expense!")
            expense_list.add_widget(item)
        else:
            for expense in expenses:
                expense_id, amount, category, description, date = expense
                total += amount
                
                # Format date nicely
                try:
                    date_obj = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
                    display_date = date_obj.strftime("%b %d, %H:%M")
                except:
                    display_date = date
                
                item_text = f"${amount:.2f}"
                if category:
                    item_text += f" • {category}"
                if description:
                    item_text += f" • {description}"
                
                item = TwoLineListItem(
                    text=item_text,
                    secondary_text=display_date
                )
                expense_list.add_widget(item)
        
        filter_text = "" if self.current_filter == "All" else f" ({self.current_filter})"
        total_label.text = f'Total Spent{filter_text}: ${total:.2f}'
    
    def on_stop(self):
        if hasattr(self, 'db_conn') and self.db_conn:
            self.db_conn.close()

if __name__ == "__main__":
    ExpenseTrackerApp().run()
