from gi.repository import Gtk

from Gui.Icon import Icon


# array with gtk toolbuttons
class ButtonToolbar(Gtk.Toolbar):

    # button labels
    toolbar_buttons_text = ["Старт", "Выбор программ", "Настройки тюнера",
                            "Настройки анализа", "Запись потока",
                            "О программе"]

    # button tooltip text
    tooltip_arr = ["Запустить анализ", "Выбор программ для анализа",
                   "Настройки ТВ тюнера", "Настройки алгоритмов определения "
                   "искажений изображения и звука",
                   "Запись потока на внутренний диск или съемный носитель",
                   "О программе"]

    # themed icon names
    ico_arr = ["media-playback-start-symbolic", "tv-symbolic",
               "network-wireless-symbolic", "emblem-system-symbolic",
               "drive-harddisk-symbolic", "help-about-symbolic"]

    # create a toolbar
    def __init__(self):
        Gtk.Toolbar.__init__(self, hexpand=False, vexpand=True,
                             orientation=Gtk.Orientation.VERTICAL,
                             toolbar_style=Gtk.ToolbarStyle.ICONS)
        # setting this toolbar as primary for the window
        self.get_style_context().add_class(Gtk.STYLE_CLASS_PRIMARY_TOOLBAR)

        # create tool buttons
        self.btn_arr = []
        for i in range(len(self.ico_arr)):
            self.btn_arr.append(Gtk.ToolButton.new(
                Icon(self.ico_arr[i]),
                self.toolbar_buttons_text[i]))
            self.btn_arr[i].set_is_important(True)
            self.btn_arr[i].set_has_tooltip(True)
            self.btn_arr[i].set_tooltip_text(self.tooltip_arr[i])
            self.insert(self.btn_arr[i], i)

    # change text and tooltip for start button
    def change_start_icon(self):
        # if current state is "start"
        if self.btn_arr[0].get_label() == "Старт":
            # change label and icon of toolbutton
            self.tooltip_arr[0] = "Остановить анализ"
            self.btn_arr[0].set_label("Стоп")
            self.btn_arr[0].set_icon_widget(
                Icon("media-playback-stop-symbolic"))
        # if current state is "stop"
        else:
            # change label and icon of toolbutton
            self.tooltip_arr[0] = "Запустить анализ"
            self.btn_arr[0].set_label("Старт")
            self.btn_arr[0].set_icon_widget(
                Icon("media-playback-start-symbolic"))
        self.btn_arr[0].set_tooltip_text(self.tooltip_arr[0])
        self.btn_arr[0].show_all()

