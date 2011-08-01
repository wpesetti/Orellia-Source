#for debugging
G_DEBUG = False


def debug(module="?", text=""):
    if(G_DEBUG):
        print "DEBUG in ",module, ": ", text