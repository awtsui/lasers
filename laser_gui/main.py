from tkinter import filedialog
import customtkinter
from PIL import Image
from CTkColorPicker import AskColor
from scanner import scan_network
from client import DisconnectedClientError, GUIClient
from tkinter.messagebox import showerror, showinfo
import os

customtkinter.set_appearance_mode("system")

DEFAULT_IPS = ["IP Address Lookup", "127.0.0.1"]


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # VARIABLES
        self.ip_address = ""
        self.port = 0
        self.server_name = ""
        self.client = GUIClient()
        self.color = "#ffffff"
        self.brightness = 50
        self.sensitivity = 50
        self.ilda_shows = []

        # TOP LEVEL SETTINGS
        self.title("LASERS")
        self.geometry("700x450")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # FRAME DISCONNECTED
        self.frame_disconnect = customtkinter.CTkFrame(self)
        self.frame_disconnect.grid(row=0, column=0, sticky="nsew")
        self.frame_disconnect.grid_rowconfigure(1, weight=1)
        self.frame_disconnect.grid_columnconfigure(0, weight=1)

        self.frame_disconnect_top = customtkinter.CTkFrame(self.frame_disconnect)
        self.frame_disconnect_top.grid_columnconfigure((0, 1, 2, 3), weight=1)
        self.frame_disconnect_top.grid(row=0, column=0)

        self.label_name = customtkinter.CTkLabel(
            master=self.frame_disconnect,
            text="LASERS",
            font=customtkinter.CTkFont("ITF Devanagari Marathi", 100, "normal"),
        )
        self.label_name.grid(row=1, column=0, pady=10, padx=10)

        self.button_connect = customtkinter.CTkButton(
            master=self.frame_disconnect_top,
            command=self.button_connect_callback,
            text="Connect",
            state="disabled",
        )
        self.button_connect.grid(row=0, column=3, pady=10, padx=10)

        self.menu_lookup = customtkinter.CTkOptionMenu(
            master=self.frame_disconnect_top,
            values=DEFAULT_IPS,
            command=self.menu_lookup_callback,
        )
        self.menu_lookup.grid(row=0, column=1, pady=10, padx=10)
        self.menu_lookup.set("IP Address Lookup")

        self.entry_port = customtkinter.CTkEntry(
            master=self.frame_disconnect_top,
            placeholder_text="Port",
            validate="key",
            validatecommand=(
                self.register(self.entry_port_callback),
                "%P",
            ),
        )
        self.entry_port.grid(row=0, column=2, pady=10, padx=10)

        self.button_rescan = customtkinter.CTkButton(
            master=self.frame_disconnect_top,
            command=self.button_rescan_callback,
            text="Scan Network",
        )
        self.button_rescan.grid(row=0, column=0, pady=10, padx=10)

        # FRAME CONNECTED
        self.frame_connect = customtkinter.CTkFrame(self)
        self.frame_connect.grid_columnconfigure(0, weight=1)
        self.frame_connect.grid_rowconfigure(1, weight=1)
        # self.frame_connect.grid(row=0, column=0, sticky="nsew")

        self.frame_connect_top = customtkinter.CTkFrame(self.frame_connect)
        self.frame_connect_top.grid_columnconfigure((0, 1, 2, 3), weight=1)
        self.frame_connect_top.grid(row=0, column=0)

        self.button_disconnect = customtkinter.CTkButton(
            master=self.frame_connect_top,
            command=self.button_disconnect_callback,
            text="Disconnect",
        )
        self.button_disconnect.grid(row=0, column=2, pady=10, padx=10)

        self.label_ip_address = customtkinter.CTkLabel(
            master=self.frame_connect_top, text="IP Address"
        )
        self.label_ip_address.grid(row=0, column=0, pady=10, padx=10)

        self.label_port = customtkinter.CTkLabel(
            master=self.frame_connect_top, text="Port"
        )
        self.label_port.grid(row=0, column=1, pady=10, padx=10)

        self.label_server_name = customtkinter.CTkLabel(
            master=self.frame_connect_top, text="Server Name"
        )
        self.label_server_name.grid(row=0, column=3, pady=10, padx=10)

        self.frame_connect_bot = customtkinter.CTkFrame(self.frame_connect)
        self.frame_connect_bot.grid_columnconfigure((0, 1), weight=1)
        self.frame_connect_bot.grid_rowconfigure((0, 1, 2, 3, 4), weight=1)
        self.frame_connect_bot.grid(row=1, column=0)

        self.label_color = customtkinter.CTkLabel(
            master=self.frame_connect_bot, text="Color"
        )
        self.label_color.grid(row=0, column=0, pady=10, padx=10)

        self.button_color = customtkinter.CTkButton(
            master=self.frame_connect_bot,
            command=self.button_color_callback,
            text="",
            fg_color="white",
            border_color="black",
        )
        self.button_color.grid(row=0, column=1, pady=10, padx=10)
        self.button_color.configure(fg_color="#ffffff")
        self.button_color.configure(text="#ffffff")

        self.label_sensitivity = customtkinter.CTkLabel(
            master=self.frame_connect_bot, text="Sensitivity 50%"
        )
        self.label_sensitivity.grid(row=1, column=0, pady=10, padx=10)

        self.slider_sensitivity = customtkinter.CTkSlider(
            master=self.frame_connect_bot,
            command=self.slider_sensitivity_callback,
            from_=0,
            to=1,
        )
        self.slider_sensitivity.grid(row=1, column=1, pady=10, padx=10)
        self.slider_sensitivity.set(0.5)

        self.label_brightness = customtkinter.CTkLabel(
            master=self.frame_connect_bot, text="Brightness 50%"
        )
        self.label_brightness.grid(row=2, column=0, pady=10, padx=10)

        self.slider_brightness = customtkinter.CTkSlider(
            master=self.frame_connect_bot,
            command=self.slider_brightness_callback,
            from_=0,
            to=1,
        )
        self.slider_brightness.grid(row=2, column=1, pady=10, padx=10)
        self.slider_brightness.set(0.5)

        self.label_ilda = customtkinter.CTkLabel(
            master=self.frame_connect_bot, text="Upload Lasershow"
        )
        self.label_ilda.grid(row=3, column=0, pady=10, padx=10)

        self.frame_connect_bot_upload = customtkinter.CTkFrame(self.frame_connect_bot)
        self.frame_connect_bot_upload.grid(row=3, column=1)

        self.textbox_ilda = customtkinter.CTkTextbox(
            master=self.frame_connect_bot_upload, activate_scrollbars=False, height=12
        )
        self.textbox_ilda.grid(row=0, column=0, pady=10, padx=10)

        self.button_ilda = customtkinter.CTkButton(
            master=self.frame_connect_bot_upload,
            command=self.button_ilda_callback,
            text="Browse",
            width=50,
        )
        self.button_ilda.grid(row=0, column=1, pady=10, padx=10)

        self.button_import_ilda = customtkinter.CTkButton(
            master=self.frame_connect_bot_upload,
            command=self.button_import_ilda_callback,
            text="Upload",
            width=50,
        )
        self.button_import_ilda.grid(row=0, column=2, pady=10, padx=10)

        self.label_choose_ilda = customtkinter.CTkLabel(
            master=self.frame_connect_bot, text="Select Lasershow"
        )
        self.label_choose_ilda.grid(row=4, column=0, padx=10, pady=10)

        self.frame_connect_bot_ilda = customtkinter.CTkFrame(self.frame_connect_bot)
        self.frame_connect_bot_ilda.grid(row=4, column=1)

        self.menu_select_ilda = customtkinter.CTkOptionMenu(
            master=self.frame_connect_bot_ilda,
            values=[],
            dynamic_resizing=True,
        )
        self.menu_select_ilda.grid(row=0, column=0, pady=10, padx=10)
        self.menu_select_ilda.set("")

        self.button_select_ilda = customtkinter.CTkButton(
            master=self.frame_connect_bot_ilda,
            command=self.button_select_ilda_callback,
            text="Select",
            width=75,
        )
        self.button_select_ilda.grid(row=0, column=2, pady=10, padx=10)

        self.button_update_settings = customtkinter.CTkButton(
            master=self.frame_connect,
            command=self.button_update_settings_callback,
            text="Update",
        )
        self.button_update_settings.grid(row=2, column=0, pady=20, padx=10)

    # CALLBACK FUNCTIONS

    def button_connect_callback(self):
        print(f"Connecting to {self.ip_address}:{self.port}")
        try:
            server_name, ilda_files = self.client.connect(self.ip_address, self.port)
            self.populate_ilda(ilda_files)
            self.server_name = server_name
            self.label_ip_address.configure(text=self.ip_address)
            self.label_port.configure(text=self.port)
            self.label_server_name.configure(text=server_name)
            self.switch_frames("connect")
        except Exception as e:
            showerror(
                title="error",
                message=f"Failed to connect to selected server. Please retry!\nError stack:\n{e}",
            )
            print(
                f"Failed to connect to selected server. Please retry!\nError stack:\n{e}"
            )

    def button_disconnect_callback(self):
        print("Disconnecting...")
        self.client.disconnect()
        self.reset_state()
        print("Disconnected")
        self.switch_frames("disconnect")

    def button_rescan_callback(self):
        try:
            self.button_rescan.configure(state="disabled")
            result = scan_network()
            devices = [device["ip"] for device in result]
            self.menu_lookup.configure(values=DEFAULT_IPS + devices)
        except Exception as e:
            showerror(title="Error", message=f"Network scan failed:\n{e}")
            print("Network scan failed:\n", e)
        self.button_rescan.configure(state="normal")

    def menu_lookup_callback(self, choice):
        if choice == "IP Address Lookup":
            self.button_connect.configure(state="disabled")
            return
        print("Set IP Address: ", choice)
        self.ip_address = choice
        if self.port:
            self.button_connect.configure(state="normal")
        else:
            self.button_connect.configure(state="disabled")

    def slider_sensitivity_callback(self, value):
        self.sensitivity = int(100 * (value / 1.0))
        self.label_sensitivity.configure(text=f"Sensitivity {self.sensitivity}%")

    def slider_brightness_callback(self, value):
        self.brightness = int(100 * (value / 1.0))
        self.label_brightness.configure(text=f"Brightness {self.brightness}%")

    def entry_port_callback(self, value):
        if value.isnumeric():
            print("Set Port: ", value)
            self.port = int(value)
            if self.ip_address:
                self.button_connect.configure(state="normal")
        else:
            self.port = ""
            self.button_connect.configure(state="disabled")
        return True

    def button_color_callback(self):
        pick_color = AskColor()  # Open the Color Picker
        color = pick_color.get() or "#ffffff"  # Get the color
        self.color = color
        self.button_color.configure(fg_color=color)
        self.button_color.configure(text=color)

    def button_ilda_callback(self):
        filename = filedialog.askopenfilename(
            initialdir="/",
            title="Select a File",
            filetypes=[("ILDA files", "*.ild")],
        )
        self.textbox_ilda.delete("0.0", "end")
        self.textbox_ilda.insert("0.0", filename)

    def button_import_ilda_callback(self):
        try:
            filepath = self.textbox_ilda.get("0.0", "end").strip()
            self.client.sendFileMessage(filepath)
            self.reload_ilda_menu(filepath)
            showinfo(title="Info", message="File successfully uploaded.")
        except Exception as e:
            showerror(title="Error", message=f"Failed to upload file. Error stack: {e}")

    def button_update_settings_callback(self):
        try:
            self.client.sendSettingsMessage(
                self.color, self.brightness, self.sensitivity
            )
            showinfo(title="Info", message="Settings succesfully uploaded.")
        except Exception as e:
            showerror(
                title="Error", message=f"Failed to upload settings. Error stack: {e}"
            )

    def button_select_ilda_callback(self):
        file_name = self.menu_select_ilda.get()
        if file_name:
            try:
                self.client.sendShowMessage(file_name)
                showinfo(title="Info", message="Show successfully selected.")
            except Exception as e:
                showerror(
                    title="Error", message=f"Failed to select show. Error stack: {e}"
                )
        else:
            return

    def change_appearance_mode_event(self, new_appearance_mode):
        customtkinter.set_appearance_mode(new_appearance_mode)

    # HELPER FUNCTIONS

    def populate_ilda(self, files):
        if len(files) == 0:
            self.menu_select_ilda.configure(state="disabled")
            self.button_select_ilda.configure(state="disabled")
            return
        self.ilda_shows = files
        self.menu_select_ilda.set(files[0])
        self.menu_select_ilda.configure(values=files)

    def reload_ilda_menu(self, filepath):
        self.ilda_shows.append(os.path.basename(filepath))
        self.menu_select_ilda.configure(values=self.ilda_shows)

    def switch_frames(self, action):
        if action == "connect":
            self.frame_connect.grid(row=0, column=0, sticky="nsew")
        else:
            self.frame_connect.grid_forget()
        if action == "disconnect":
            self.frame_disconnect.grid(row=0, column=0, sticky="nsew")
        else:
            self.frame_disconnect.grid_forget()

    def reset_state(self):
        self.ip_address = ""
        self.port = 0
        self.server_name = ""
        self.client = GUIClient()
        self.color = "#ffffff"
        self.brightness = 50
        self.sensitivity = 50

        self.menu_lookup.set("IP Address Lookup")
        self.entry_port.delete("0", "end")
        self.button_color.configure(fg_color=self.color)
        self.button_color.configure(text=self.color)
        self.slider_brightness.set(0.5)
        self.label_brightness.configure(text="Brightness 50%")
        self.slider_sensitivity.set(0.5)
        self.label_sensitivity.configure(text="Sensitivity 50%")


if __name__ == "__main__":
    app = App()
    app.mainloop()
