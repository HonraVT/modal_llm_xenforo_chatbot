from time import sleep

from src.bot import main, first_run


def run():
    print("run")
    while True:
        main(production=False)
        sleep(10)


# execute the first_run function just ONCE to create the database with the latest alert ID
# and prevent bot responding ALL old messages.
# comment run() function below before run first_run function.

# first_run(production=False)
run()
