from sunsynk_data import SunsynkData

username = "*****"
password = "*****"
serial_number = 923492352
sunsync_data = SunsynkData(serial_number, username, password)
battery = sunsync_data.get_battery()
pv = sunsync_data.get_pv()
load = sunsync_data.get_load()
info = sunsync_data.get_info()

print(battery)
print(pv)
print(load)
print(info)


