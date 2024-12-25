def stripAccent(s: str):
    s = s.replace("\u00e9", "e")  # * removes é
    s = s.replace("\u00e8", "e")  # * removes è
    s = s.replace("\u00e2", "a")  # * removes â
    s = s.replace("\u00e7", "c")  # * removes ç
    s = s.replace("\u00e0", "a")  # * removes à
    s = s.replace("\u0000", "")  # * removes null character

    return s
