class Settings:
    DEFAULT_PATH = '/cache/'
    BINARY_PATH = 'bin/aarch64/'

class Sysbench:
    PATH = Settings.DEFAULT_PATH + 'sysbench'
    CPU_MAX_PRIME = '--cpu-max-prime='
    CPU_THREADS = '--threads='
    CPU_RUN = 'cpu run'
    THREADS_YIELDS = '--thread-yields='
    THREADS_THREADS = '--threads='
    THREADS_LOCKS = '--thread-locks='
    THREADS_RUN = 'threads run'
    MEM_THREADS = '--threads='
    MEM_TOTAL = '--memory-total-size='
    MEM_BLOCK = '--memory-block-size='
    MEM_RUN = 'memory run'
    IO_TOTAL = '--file-total-size='
    IO_MODE = '--file-test-mode='
    IO_FSYNC_FREQ = '--file-fsync-freq='
    IO_PREPARE = 'fileio prepare'
    IO_RUN = 'fileio run'
    IO_CLEANUP = 'fileio cleanup'

    class DEFAULT:
        CPU_MAX_PRIME = '10000'
        CPU_THREADS = '1'
        THREADS_YIELDS = '1000'
        THREADS_LOCKS = '100'
        MEM_TOTAL = '200G'
        MEM_BLOCK = '1M'
        IO_TOTAL = '50M'
        IO_TEST_MODE = 'rndrw'
        IO_FSYNC_FREQ = '100'


class Tinymembench:
    PATH = Settings.DEFAULT_PATH + 'tinymembench'


class StressNg:
    PATH = Settings.DEFAULT_PATH + 'stress-ng'
    MATRIX = '--matrix '
    MATRIX_SIZE = '--matrix-size '
    IO = '--io '
    VM = '--vm '
    VM_BYTES = '--vm-bytes '
    METRICS_BRIEF = '--metrics-brief'
    TZ = '--tz'
    T = '-t '
    CPU = '--cpu '

    class DEFAULT:
        MATRIX = '0'
        MATRIX_SIZE = '64'
        IO = '6'
        VM = '1'
        VM_BYTES = '1000M'
        T = '30h'
        CPU = '0'


class AdbHelper:
    SHELL = 'adb', 'shell'
    PUSH = 'adb', 'push'
    DEVICES = 'adb', 'devices'
    WAIT_FOR_DEVICE = 'adb', 'wait-for-device'
    ROOT_SHELL = *SHELL, 'su'
    CHMOD = *SHELL, 'chmod'
    WATCH = *SHELL, 'watch', '-n 1', 'cat'
    CPU_CUR_FREQ = '/sys/devices/system/cpu/cpufreq/policy0/cpuinfo_cur_freq'
    CPU_CUR_TEMP = '/sys/class/thermal/thermal_zone0/temp'

