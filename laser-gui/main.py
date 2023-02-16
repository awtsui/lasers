import tkinter
import customtkinter
from PIL import Image
from CTkColorPicker import AskColor
from scanner import scan_network

customtkinter.set_appearance_mode("system")


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # VARIABLES
        self.ip_address = ""
        self.port = ""

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
            values=["IP Address Lookup"],
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

        # TODO: Figure out how to obtain server name
        self.label_server_name = customtkinter.CTkLabel(
            master=self.frame_connect_top, text="Server Name"
        )
        self.label_server_name.grid(row=0, column=3, pady=10, padx=10)

        self.frame_connect_bot = customtkinter.CTkFrame(self.frame_connect)
        self.frame_connect_bot.grid_columnconfigure((0, 1), weight=1)
        self.frame_connect_bot.grid_rowconfigure((0, 1, 2), weight=1)
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

    # CALLBACK FUNCTIONS

    def button_connect_callback(self):
        print("Connecting to", self.ip_address)
        self.switch_frames("connect")
        self.label_ip_address.configure(text=self.ip_address)
        self.label_port.configure(text=self.port)
        # self.label_server_name.configure()

    def button_disconnect_callback(self):
        print("Disconnecting...")
        self.switch_frames("disconnect")

    def button_rescan_callback(self):
        try:
            self.button_rescan.configure(state="disabled")
            result = scan_network()
            devices = [device["ip"] for device in result]
            self.menu_lookup.configure(values=["IP Address Lookup"] + devices)
        except Exception as e:
            print("Network scan failed: \n", e)
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
        print("Sensitivity slider value: ", value)
        self.label_sensitivity.configure(
            text="Sensitivity {:0.0f}%".format(100 * (value / 1.0))
        )

    def slider_brightness_callback(self, value):
        print("Brightness slider value: ", value)
        self.label_brightness.configure(
            text="Brightness {:0.0f}%".format(100 * (value / 1.0))
        )

    def entry_port_callback(self, value):
        if value.isnumeric():
            print("Set Port: ", value)
            self.port = value
            if self.ip_address:
                self.button_connect.configure(state="normal")
        else:
            self.port = ""
            self.button_connect.configure(state="disabled")
        return True

    def button_color_callback(self):
        pick_color = AskColor()  # Open the Color Picker
        color = pick_color.get() or "#ffffff"  # Get the color
        self.button_color.configure(fg_color=color)
        self.button_color.configure(text=color)

    def change_appearance_mode_event(self, new_appearance_mode):
        customtkinter.set_appearance_mode(new_appearance_mode)

    # HELPER FUNCTIONS

    def switch_frames(self, action):
        if action == "connect":
            self.frame_connect.grid(row=0, column=0, sticky="nsew")
        else:
            self.frame_connect.grid_forget()
        if action == "disconnect":
            self.frame_disconnect.grid(row=0, column=0, sticky="nsew")
        else:
            self.frame_disconnect.grid_forget()


if __name__ == "__main__":
    app = App()
    app.mainloop()
