from textual.app import App, ComposeResult
from textual.containers import HorizontalGroup, VerticalScroll
from textual.widgets import Button, Digits, Footer, Header
from textual.widgets import Footer, Label, ListItem, ListView
from textual.message import Message

class ListViewExample(App):
    CSS_PATH = "day_prototype.tcss"

    def compose(self) -> ComposeResult:
        secondary_label = Label("Lu", id="secondary-label")
        secondary_label.styles.height = 5
        
        new_button = Button("New Button", id="primary-label")
        new_button.styles.height = 5

        # Create many more items to enable scrolling
        items = []
        for i in range(20):
            items.append(ListItem(Label(f"Item {i + 1}")))
        
        # Add your custom items
        items.extend([
            ListItem(Button("Primary Label", id="primary-label")),
            ListItem(secondary_label),
            ListItem(new_button)
        ])
        
        list_view = ListView(*items)
        
        # The time display area to the left of the ListView
        times = ""
        for i in range(24):
            times += f"{i:02}:00\n"
            times += 5*"\n"


        daytime = Label(times)
        daytime.styles.height = "100vh"
        daytime.styles.width = "20"
        
        list_view.styles.height = "100vh"
        list_view.styles.width = "80"

        vscroll = VerticalScroll(HorizontalGroup(daytime, list_view))
        # vscroll.styles.height = "100vh"

        yield vscroll
        yield Footer()

    def on_mount(self) -> None:
        """Set focus to the ListView when the app starts."""
        self.query_one(ListView).focus()
    
    def on_list_view_selected(self, message: ListView.Selected) -> None:
        """Handle ListView selection - trigger button press if item contains a button."""
        # Get the selected ListItem
        list_item = message.item
        
        # Check if the ListItem contains a Button
        buttons = list_item.query(Button)
        if buttons:
            # If there's a button, simulate pressing it
            button = buttons.first()
            button.press()
    
    def on_button_pressed(self, message: Button.Pressed) -> None:
        """Handle button press events."""
        if message.button.id == "primary-label":
            self.notify("Primary button was pressed!")

if __name__ == "__main__":
    app = ListViewExample()
    app.run()