import os


def mkd(name):
    if not os.path.exists(name):
        os.mkdir(name)
    os.chdir(name)


