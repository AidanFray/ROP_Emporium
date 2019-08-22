def _recvall(io):
    """
    Prints final output of the program
    """

    d = io.recvall()
    print(d.decode("utf-8"))