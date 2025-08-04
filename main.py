import psutil
import time
import platform
import os
from rich.table import Table
from rich.console import Console
from rich.panel import Panel

def processes_by_memory():
    processes = [
        p for p in psutil.process_iter(['name', 'memory_info'])
        if p.info['memory_info'] is not None
    ]
    sorted_processes = sorted(
        processes,
        key=lambda p: p.info['memory_info'].rss,
        reverse=True
    )
    return [
        (p.pid, p.info['name'], sum(p.info['memory_info']))
        for p in sorted_processes[:5]
    ]

def processes_by_cpu():
    # Primera llamada para inicializar los contadores
    for p in psutil.process_iter():
        try:
            p.cpu_percent(interval=None)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    time.sleep(1) 

    process_info = []
    for p in psutil.process_iter(['name']):
        try:
            percent = p.cpu_percent(interval=None)
            process_info.append((p.pid, p.info['name'], percent))
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    return sorted(process_info, key=lambda x: x[2], reverse=True)[:5]

def cpu_usage() -> float:
    return psutil.cpu_percent(interval=1)


def ram_memory_usage():
    memory_info = psutil.virtual_memory()
    used_memory = memory_info.used / (1024**3)
    total_memory = memory_info.total / (1024**3)
    memory_percentage = (used_memory / total_memory) * 100
    return [used_memory, total_memory, memory_percentage]

def disk_usage():
    disk_info = psutil.disk_usage('/')
    used_disk = disk_info.used / (1024**3)
    total_disk = disk_info.total / (1024**3)
    disk_usage_percentage = (used_disk / total_disk) * 100
    return [used_disk, total_disk, disk_usage_percentage]

def display_stats():
    console = Console()
    console.clear()

    # Panel de información general
    table = Table.grid()
    table.add_column(justify="right", style="cyan", no_wrap=True)
    table.add_column()

    # Info del sistema
    table.add_row("OS:", f"{platform.system()} {platform.release()}")
    table.add_row("Uptime:", f"{int(time.time() - psutil.boot_time()):.2f} s")
    try:
        load = os.getloadavg()
        table.add_row("Load avg:", f"{load[0]:.2f}, {load[1]:.2f}, {load[2]:.2f}")
    except (AttributeError, OSError):
        table.add_row("Load avg:", "Not available")
    table.add_row("Logged in users:", str(len(psutil.users())))

    # CPU, memoria, disco
    cpu = cpu_usage()
    used_memory, total_memory, memory_percentage = ram_memory_usage()
    used_disk, total_disk, disk_usage_percentage = disk_usage()

    table.add_row("CPU Usage:", f"{cpu:.2f}%")
    table.add_row("Memory:", f"{used_memory:,.2f} GB / {total_memory:,.2f} GB ({memory_percentage:.2f}%)")
    table.add_row("Disk:", f"{used_disk:,.2f} GB / {total_disk:,.2f} GB ({disk_usage_percentage:.2f}%)")

    # Mostrar el panel
    console.print(Panel(table, title="System Stats", border_style="green"))

    # Procesos por CPU
    cpu_table = Table(title="Top 5 Processes by CPU", border_style="blue")
    cpu_table.add_column("PID")
    cpu_table.add_column("Name")
    cpu_table.add_column("CPU")
    for pid, name, percent in processes_by_cpu():
        cpu_table.add_row(str(pid), str(name), f"{str(percent)} %")
    console.print(cpu_table)

    # Procesos por Memoria
    mem_table = Table(title="Top 5 Processes by Memory", border_style="magenta")
    mem_table.add_column("PID")
    mem_table.add_column("Name")
    mem_table.add_column("Memory")
    for pid, name, mem in processes_by_memory():
        mem_table.add_row(
        str(pid),
        str(name),
        f"{mem / (1024**3):,.1f} MB"
    )

    console.print(mem_table)


if __name__ == "__main__":
    try:
        while True:
            display_stats()
            time.sleep(5)
    except KeyboardInterrupt:
        print("\nExiting...")

