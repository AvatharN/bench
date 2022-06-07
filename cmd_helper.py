import subprocess
import json
import time
from datetime import timedelta
from params import AdbHelper, Sysbench, Tinymembench, StressNg, Settings


class SysbenchRunner:
    DEFAULT = object()

    def __init__(self):
        self.result = {}
        self.cpu_count = self.get_cores_count()

    def get_json(self):
        return json.dumps(self.result)

    def save_json(self):
        with open('sysbench_run_' + str(int(time.time())) + '.json', 'w', encoding='utf-8') as f:
            json.dump(self.result, f, ensure_ascii=False, indent=4)

    @staticmethod
    def get_cores_count():
        cpuinfo = subprocess.run([*AdbHelper.SHELL, 'cat /proc/cpuinfo'], capture_output=True, text=True)
        cpu_count = 1
        for line in cpuinfo.stdout:
            if 'processor' in line:
                cpu_count = line.split(':')[1].strip
        return int(cpu_count)

    @staticmethod
    def parse_result(run_result):
        test_result = {}
        temp = None
        tag = 'Threads started!'
        tag_found = False
        for line in run_result.splitlines():
            if not tag_found:
                tag_found = tag in line
            if ':' in line and tag_found:
                if line.split(':')[1] == '':
                    temp = line.split(':')[0]
                    test_result[temp] = {}
                else:
                    key, value = line.split(':')[0].strip(), line.split(':')[1].strip()
                    if temp is None:
                        test_result[key] = value
                    else:
                        test_result[temp][key] = value
        return test_result

    def run_cpu_test(self, max_prime=Sysbench.DEFAULT.CPU_MAX_PRIME, threads=DEFAULT):
        if threads is self.DEFAULT:
            threads = str(self.get_cores_count())
        print('Starting CPU Test...')
        sysbench_run = subprocess.run(
            [*AdbHelper.SHELL, Sysbench.PATH, Sysbench.CPU_RUN, Sysbench.CPU_THREADS + threads,
             Sysbench.CPU_MAX_PRIME + max_prime], capture_output=True, text=True)
        self.result['CPU'] = self.parse_result(sysbench_run.stdout)

    def run_threads_test(self, yields=Sysbench.DEFAULT.THREADS_YIELDS, thread_locks=Sysbench.DEFAULT.THREADS_LOCKS,
                         threads=DEFAULT):
        if threads is self.DEFAULT:
            threads = str(self.get_cores_count() * 4)
        print('Starting threads test...')
        sysbench_run = subprocess.run(
            [*AdbHelper.SHELL, Sysbench.PATH, Sysbench.THREADS_RUN, Sysbench.THREADS_YIELDS + yields,
             Sysbench.THREADS_LOCKS + thread_locks, Sysbench.THREADS_THREADS + threads], capture_output=True, text=True)
        self.result['Threads'] = self.parse_result(sysbench_run.stdout)

    def run_mem_test(self, mem_total=Sysbench.DEFAULT.MEM_TOTAL, mem_block=Sysbench.DEFAULT.MEM_BLOCK, threads=DEFAULT):
        if threads is self.DEFAULT:
            threads = str(self.get_cores_count() * 4)
        print('Starting mem test...')
        sysbench_run = subprocess.run(
            [*AdbHelper.SHELL, Sysbench.PATH, Sysbench.MEM_RUN, Sysbench.MEM_TOTAL + mem_total,
             Sysbench.MEM_BLOCK + mem_block, Sysbench.MEM_THREADS + threads],
            capture_output=True, text=True)
        self.result['Memory'] = self.parse_result(sysbench_run.stdout)

    def run_fileio_test(self, io_total=Sysbench.DEFAULT.IO_TOTAL, io_test_mode=Sysbench.DEFAULT.IO_TEST_MODE,
                        io_fsync_freq=Sysbench.DEFAULT.IO_FSYNC_FREQ):
        sysbench_prep = subprocess.run(
            [*AdbHelper.SHELL, Sysbench.PATH, Sysbench.IO_PREPARE, Sysbench.IO_TOTAL + io_total],
            capture_output=True, text=True)
        if 'FATAL' in sysbench_prep.stdout:
            raise Exception('Can\'t create test files. Out of space?')
        print('Running fileIO test...')
        sysbench_run = subprocess.run([*AdbHelper.SHELL, Sysbench.PATH, Sysbench.IO_RUN, Sysbench.IO_TOTAL + io_total,
                                       Sysbench.IO_MODE + io_test_mode, Sysbench.IO_FSYNC_FREQ + io_fsync_freq],
                                      capture_output=True, text=True)
        sysbench_cleanup = subprocess.run([*AdbHelper.SHELL, Sysbench.PATH, Sysbench.IO_CLEANUP])
        self.result['FileIO'] = self.parse_result(sysbench_run.stdout)

    def run_all(self):
        self.run_fileio_test()
        self.run_mem_test()
        self.run_threads_test()
        self.run_cpu_test()


class TinymembenchRunner:

    def __init__(self):
        self.result = {}

    def run(self):
        tinymem_run = subprocess.run([*AdbHelper.SHELL, Tinymembench.PATH], capture_output=True, text=True)
        self.result = self.parse_result(tinymem_run.stdout)
        self.result['timestamp'] = int(time.time())

    def save_json(self):
        with open('tinybench_' + str(int(time.time())) + '.json', 'w', encoding='utf-8') as f:
            json.dump(self.result, f, ensure_ascii=False, indent=4)

    def parse_result(self, text):
        self.result = {'BANDWIDTH': {}, 'LATENCY': {}}
        counter = 0
        for line in text.splitlines():
            if '=======' in line:
                print('counter is ', counter)
                counter += 1
            if counter == 2 and ':' in line:
                temp_result = {
                    line.split(':')[0].strip().replace('copy ', '').replace(' bytes step', ' ').replace(' byte blocks',
                                                                                                        ''):
                        line.split(':')[1].strip()}
                self.result['BANDWIDTH'].update(temp_result)
            if counter == 4 and ':' in line and 'block' not in line:
                temp_result = {line.split(':')[0].strip(): line.split(':')[1].strip().replace(' ', '').split('/')}
                self.result['LATENCY'].update(temp_result)
        return self.result


class StressNgRunner:
    DEFAULT = object()

    def __init__(self):
        self.result = {}
        self.start_time = int(time.time())

    @staticmethod
    def is_it_num(line):
        try:
            int(line)
            return True
        except:
            return False

    def save_json(self):
        with open('stressng_' + str(self.start_time) + '.json', 'w', encoding='utf-8') as f:
            json.dump(self.result, f, ensure_ascii=False, indent=4)

    def run_cpu_long_stress(self):
        stress_run = subprocess.Popen([*AdbHelper.SHELL, StressNg.PATH, StressNg.TZ, StressNg.T + StressNg.DEFAULT.T,
                                       StressNg.METRICS_BRIEF, StressNg.CPU + StressNg.DEFAULT.CPU,
                                       StressNg.MATRIX + '0', StressNg.MATRIX_SIZE + '64', StressNg.IO + '6',
                                       StressNg.VM + '1',
                                       StressNg.VM_BYTES + '100M'],
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.STDOUT, universal_newlines=True)
        freq_watcher = subprocess.Popen([*AdbHelper.WATCH, AdbHelper.CPU_CUR_FREQ],
                                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        cpu_temp_watcher = subprocess.Popen(['adb', 'shell', 'watch -n 1 cat sys/class/thermal/thermal_zone0/temp'],
                                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        while stress_run.poll() is None:

            freq = freq_watcher.stdout.readline()
            cpu = cpu_temp_watcher.stdout.readline()
            if self.is_it_num(freq):
                timestamp = int(time.time()) - self.start_time
                self.result[timestamp] = {}
                self.result[timestamp]['FREQ'] = int(freq)
                self.result[timestamp]['CPUTEMP'] = int(cpu)
                print('\rstressng runned for ', StressNg.DEFAULT.T, 'Currently runned for: ',
                      str(timedelta(seconds=(time.time() - self.start_time))),
                      'FREQ:', freq, 'TEMP:', cpu, end='')
            self.save_json()
        print('Successfully finished')
        print(stress_run.stdout.read())



class AdbPusher:

    @staticmethod
    def push_file(filename):
        push = subprocess.run([*AdbHelper.PUSH, Settings.BINARY_PATH + filename, Settings.DEFAULT_PATH],
                              capture_output=True, text=True)
        print(*AdbHelper.CHMOD, '+x', Settings.DEFAULT_PATH + filename)
        chmod = subprocess.run([*AdbHelper.CHMOD, '+x', Settings.DEFAULT_PATH + filename])
        print(push.stdout)
        if '0 skipped' in push.stdout:
            return
        else:
            raise Exception('File not transferred')



adb = AdbPusher()
# adb.push_file('sysbench')
# adb.push_file('stress-ng')
# adb.push_file('tinymembench')
# adb.push_file('cpuburn')
#
sysbench = SysbenchRunner()
# sysbench.run_cpu_test()
# sysbench.run_mem_test()
# sysbench.run_fileio_test()
# sysbench.run_threads_test()
# sysbench.save_json()
stress = StressNgRunner()
# stress.run_cpu_long_stress()