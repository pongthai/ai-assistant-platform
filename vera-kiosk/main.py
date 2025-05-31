from ui.screen_display import ScreenDisplay
from device_io.input_manager import InputManager

def main():
    screen = ScreenDisplay()
    input_mgr = InputManager()
    
    screen.show_welcome()
    input_mgr.listen_for_touch()
    input_mgr.listen_for_voice()

if __name__ == "__main__":
    main()
