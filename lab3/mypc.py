import psutil
import platform

def get_size(bytes, suffix="B"):
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor

def system_info():
    print("="*40, "Інформація про Систему", "="*40)
    uname = platform.uname()
    print(f"Система: {uname.system}")
    print(f"Ім'я вузла (PC Name): {uname.node}")
    print(f"Реліз: {uname.release}")
    print(f"Версія: {uname.version}")
    print(f"Архітектура: {uname.machine}")
    print(f"Процесор (сімейство): {uname.processor}")

def cpu_info():
    print("\n" + "="*40, "Інформація про CPU", "="*40)
    print(f"Фізичні ядра: {psutil.cpu_count(logical=False)}")
    print(f"Всього ядер (логічні): {psutil.cpu_count(logical=True)}")

    try:
        cpufreq = psutil.cpu_freq()
        print(f"Максимальна частота: {cpufreq.max:.2f}Mhz")
        print(f"Мінімальна частота: {cpufreq.min:.2f}Mhz")
        print(f"Поточна частота: {cpufreq.current:.2f}Mhz")
    except Exception:
        print("Не вдалося отримати частоту CPU (можливо, обмеження прав доступу або віртуалізація)")

    print(f"Завантаження CPU (загальне): {psutil.cpu_percent()}%")

def memory_info():
    print("\n" + "="*40, "Інформація про Пам'ять (RAM)", "="*40)
    svmem = psutil.virtual_memory()
    print(f"Всього: {get_size(svmem.total)}")
    print(f"Доступно: {get_size(svmem.available)}")
    print(f"Використано: {get_size(svmem.used)}")
    print(f"Відсоток використання: {svmem.percent}%")

    print("\n" + "-"*20, "SWAP (Файл підкачки)", "-"*20)
    swap = psutil.swap_memory()
    print(f"Всього: {get_size(swap.total)}")
    print(f"Вільне: {get_size(swap.free)}")
    print(f"Використано: {get_size(swap.used)}")
    print(f"Відсоток використання: {swap.percent}%")

def disk_info():
    print("\n" + "="*40, "Інформація про Диски", "="*40)
    partitions = psutil.disk_partitions()
    for partition in partitions:
        print(f"=== Диск: {partition.device} ===")
        print(f"  Точка монтування: {partition.mountpoint}")
        print(f"  Тип файлової системи: {partition.fstype}")
        try:
            partition_usage = psutil.disk_usage(partition.mountpoint)
            print(f"  Всього місця: {get_size(partition_usage.total)}")
            print(f"  Використано: {get_size(partition_usage.used)}")
            print(f"  Вільне: {get_size(partition_usage.free)}")
            print(f"  Заповнено: {partition_usage.percent}%")
        except PermissionError:
            print("FATAL")

if __name__ == "__main__":
    system_info()
    cpu_info()
    memory_info()
    disk_info()
