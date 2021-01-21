from datetime import datetime
from time import sleep


def waiting():
    time = datetime.now().hour
    while time != 0:
        print(time)
        sleep(3600)
        time = datetime.now().hour
    print("Actualizar!!!!!!!!!!!")
    sleep(3600)
    waiting()


if __name__ == "__main__":
    waiting()
