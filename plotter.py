import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import host_subplot
import mpl_toolkits.axisartist as AA
import math
import json
import os

MEDIAN_MAGIC_CONST = 30

def percentile(data, perc: int):
    size = len(data)
    return sorted(data)[int(math.ceil((size*perc)/100))-1]

def open_json(filename):
    with open(filename) as f:
        data = json.load(f)
    return data

def list_files(path):
    for file in os.listdir(path):
        if os.path.isfile(os.path.join(path, file)) and 'stressng' in file and 'json' in file:
            yield file

def median(x):
    total = 0
    for i in x:
        total = total + i
    return total/len(x)

def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

for file in list_files('.'):
    data = open_json(file)
    list_of_freq = list()
    list_of_temp = list()
    for k,v in data.items():
        list_of_freq.append(round(int(v['FREQ'])/1000000, 2))
        list_of_temp.append(int(v['CPUTEMP'])/1000)
    data_freq = list()
    data_temp = list()
    for i in list(chunks(list_of_freq, MEDIAN_MAGIC_CONST)):
        data_freq.append(median(i))
    for i in list(chunks(list_of_temp, MEDIAN_MAGIC_CONST)):
        data_temp.append(median(i))

    print(data_temp, data_freq)

    host = host_subplot(111, axes_class=AA.Axes)
    cputemp = host.twinx()
    host.tick_params(axis='y')

    host.set_ylabel('Frequency, Ghz')
    cputemp.set_ylabel('Temperature, °C')

    cputemp.axis['right'].toggle(all=True)

    p1, = host.plot(range(0, len(data_freq)), data_freq, color='blue', label='frequency', linewidth=1)
    p2, = cputemp.plot(range(0, len(data_temp)), data_temp, color='orange', label='temp', linewidth=1)
    host.legend(loc=4)
    host.axis['left'].label.set_color(p1.get_color())
    cputemp.axis['right'].label.set_color(p2.get_color())
    plt.title('temp 50%: {:.2f}°C, 95%: {:.2f}°C, 99%: {:.2f}°C, \n freq 50%: {:.2f}Ghz, 95%: {:.2f}Ghz, 99%: {:.2f}Ghz'.format(
        percentile(list_of_temp, 50), percentile(list_of_temp, 95), percentile(list_of_temp, 99),
        percentile(list_of_freq, 50), percentile(list_of_freq, 95), percentile(list_of_freq, 99)))
    plt.savefig(file[:-4]+'jpeg', dpi=900)
    plt.close()