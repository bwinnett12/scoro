from random import randrange

import scoro

def main():
    p1 = scoro.Scoro()
    p1.uncheck("blueberry")

    test = p1.pull()

    print(test)

    p1.reset()


if __name__ == '__main__':
    main()
    