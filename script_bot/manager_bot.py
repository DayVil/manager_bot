from commands import run_command_bot
import threading
import time


#Multithreading
def main():
    bot_commad = threading.Thread(target=run_command_bot())
    bot_commad.start()


if __name__ == '__main__':
    main()