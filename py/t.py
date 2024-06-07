import re

s = "00001        BIOL        101-NYA-05            General Biology I                                       TF             0800-0930"
sectionReg = r"^\d{5}\s{2,}[A-Z]+\s{2,}\d{3}-\w{3}-\w{2}\s{2,}(?:\w|\s|[\(\)<>&\+])+\s{2,}[MTWRF]{1,5}\s{2,}\d{4}-\d{4}$"

print(re.match(sectionReg, s))
