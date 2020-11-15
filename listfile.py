import os

listfile = ""
for f_name in os.listdir('./'):
    if f_name.endswith('.mjpeg'):
        listfile += f_name + ' '

print(listfile)