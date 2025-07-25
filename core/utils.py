from datetime import datetime

def get_timestamp():
    return datetime.now().strftime("%H:%M")

def get_datetime_str():
    return datetime.now().strftime("Current date and time: %Y-%m-%d %H:M:%S. Location: Bila Tserkva, Kyiv Oblast, Ukraine.")
