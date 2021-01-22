from datetime import datetime
from time import sleep
from api.actualizacion_peliculas import do_update


def waiting():
    time = datetime.now().hour
    while time != 0:
        print(time)
        sleep(3600)
        time = datetime.now().hour
    # debug # print("Actualizar!!!!!!!!!!!")
    do_update()
    sleep(3600)
    waiting()


if __name__ == "__main__":
    waiting()
