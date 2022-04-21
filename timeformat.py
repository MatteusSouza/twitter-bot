from datetime import datetime

def setTime(lastHour = 0, lastMinute = 0):
    now = datetime.utcnow()
    ss = now.second
    mm = now.minute - lastMinute
    HH = now.hour - lastHour
    DD = now.day
    MM = now.month
    YYYY = now.year
    
    if ss < 0:
        ss = 60-(-ss)
        mm -=1
    if mm < 0:
        mm = 60-(-mm)
        HH -= 1
    if HH < 0:
        HH = 60-(-mm)
        DD -=1
    if DD < 0:
        DD = 24-(-DD)
        MM -= 1
    if MM <0:
        MM = 12-(-MM)
        YYYY-=1

    var = f"{YYYY:04}-{MM:02}-{DD:02}T{HH:02}:{mm:02}:{ss:02}.00"
    return datetime.strptime(var, '%Y-%m-%dT%H:%M:%S.%f')

def now():
    return datetime.now()