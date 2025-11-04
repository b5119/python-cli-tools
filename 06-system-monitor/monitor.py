#!/usr/bin/env python3
"""
System Monitor
Monitor system resources (CPU, Memory, Disk) and send alerts
Requires: pip install psutil
"""

import psutil
import argparse
import time
from datetime import datetime
import json
import os

class SystemMonitor:
    def __init__(self, alert_cpu=90, alert_memory=90, alert_disk=90):
        self.alert_cpu = alert_cpu
        self.alert_memory = alert_memory
        self.alert_disk = alert_disk
        self.alerts_triggered = []
        self.log_file = 'system_monitor.log'
    
    def get_cpu_info(self):
        """Get CPU usage information"""
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()
        
        return {
            'usage_percent': cpu_percent,
            'cores': cpu_count,
            'frequency': cpu_freq.current if cpu_freq else 0,
            'per_cpu': psutil.cpu_percent(interval=0, percpu=True)
        }
    
    def get_memory_info(self):
        """Get memory usage information"""
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        return {
            'total': memory.total,
            'available': memory.available,
            'used': memory.used,
            'percent': memory.percent,
            'swap_total': swap.total,
            'swap_used': swap.used,
            'swap_percent': swap.percent
        }
    
    def get_disk_info(self):
        """Get disk usage information"""
        disks = []
        
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disks.append({
                    'device': partition.device,
                    'mountpoint': partition.mountpoint,
                    'fstype': partition.fstype,
                    'total': usage.total,
                    'used': usage.used,
                    'free': usage.free,
                    'percent': usage.percent
                })
            except PermissionError:
                continue
        
        return disks
    
    def get_network_info(self):
        """Get network statistics"""
        net_io = psutil.net_io_counters()
        
        return {
            'bytes_sent': net_io.bytes_sent,
            'bytes_recv': net_io.bytes_recv,
            'packets_sent': net_io.packets_sent,
            'packets_recv': net_io.packets_recv
        }
    
    def get_process_info(self, limit=10):
        """Get top processes by CPU and memory usage"""
        processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # Sort by CPU usage
        top_cpu = sorted(processes, key=lambda x: x['cpu_percent'] or 0, reverse=True)[:limit]
        
        # Sort by memory usage
        top_memory = sorted(processes, key=lambda x: x['memory_percent'] or 0, reverse=True)[:limit]
        
        return {
            'top_cpu': top_cpu,
            'top_memory': top_memory,
            'total_processes': len(processes)
        }
    
    def check_alerts(self, cpu_info, memory_info, disk_info):
        """Check if any alerts should be triggered"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        alerts = []
        
        # CPU alert
        if cpu_info['usage_percent'] >= self.alert_cpu:
            alert = f"[{timestamp}] ⚠️  HIGH CPU USAGE: {cpu_info['usage_percent']:.1f}%"
            alerts.append(alert)
        
        # Memory alert
        if memory_info['percent'] >= self.alert_memory:
            alert = f"[{timestamp}] ⚠️  HIGH MEMORY USAGE: {memory_info['percent']:.1f}%"
            alerts.append(alert)
        
        # Disk alerts
        for disk in disk_info:
            if disk['percent'] >= self.alert_disk:
                alert = f"[{timestamp}] ⚠️  HIGH DISK USAGE on {disk['mountpoint']}: {disk['percent']:.1f}%"
                alerts.append(alert)
        
        return alerts
    
    def display_dashboard(self):
        """Display system monitoring dashboard"""
        # Clear screen (cross-platform)
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print("="*80)
        print("🖥️  SYSTEM MONITOR DASHBOARD")
        print("="*80)
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # CPU Information
        cpu_info = self.get_cpu_info()
        print("🔥 CPU")
        print("-" * 80)
        print(f"Overall Usage: {cpu_info['usage_percent']:.1f}%")
        print(f"Cores: {cpu_info['cores']}")
        print(f"Frequency: {cpu_info['frequency']:.2f} MHz")
        
        # Show per-core usage
        print("Per-Core Usage:")
        for i, usage in enumerate(cpu_info['per_cpu']):
            bar = '█' * int(usage / 2)
            print(f"  Core {i}: {usage:>5.1f}% {bar}")
        
        # Memory Information
        memory_info = self.get_memory_info()
        print(f"\n💾 MEMORY")
        print("-" * 80)
        print(f"Total: {self._format_bytes(memory_info['total'])}")
        print(f"Used: {self._format_bytes(memory_info['used'])} ({memory_info['percent']:.1f}%)")
        print(f"Available: {self._format_bytes(memory_info['available'])}")
        
        memory_bar = '█' * int(memory_info['percent'] / 2)
        print(f"Usage: [{memory_bar:<50}] {memory_info['percent']:.1f}%")
        
        if memory_info['swap_total'] > 0:
            print(f"\nSwap: {self._format_bytes(memory_info['swap_used'])} / "
                  f"{self._format_bytes(memory_info['swap_total'])} ({memory_info['swap_percent']:.1f}%)")
            # Disk Information
        disk_info = self.get_disk_info()
        print(f"\n💿 DISK")
        print("-" * 80)
        for disk in disk_info:
            print(f"{disk['mountpoint']} ({disk['fstype']})")
            print(f"  Total: {self._format_bytes(disk['total'])}")
            print(f"  Used: {self._format_bytes(disk['used'])} ({disk['percent']:.1f}%)")
            print(f"  Free: {self._format_bytes(disk['free'])}")
            
            disk_bar = '█' * int(disk['percent'] / 2)
            print(f"  [{disk_bar:<50}] {disk['percent']:.1f}%\n")
        
        # Network Information
        network_info = self.get_network_info()
        print(f"🌐 NETWORK")
        print("-" * 80)
        print(f"Sent: {self._format_bytes(network_info['bytes_sent'])}")
        print(f"Received: {self._format_bytes(network_info['bytes_recv'])}")
        print(f"Packets Sent: {network_info['packets_sent']:,}")
        print(f"Packets Received: {network_info['packets_recv']:,}")
        
        # Process Information
        process_info = self.get_process_info(5)
        print(f"\n⚙️  TOP PROCESSES")
        print("-" * 80)
        print("By CPU:")
        for proc in process_info['top_cpu'][:5]:
            cpu = proc['cpu_percent'] or 0
            print(f"  {proc['name']:<30} PID: {proc['pid']:<8} CPU: {cpu:>5.1f}%")
        
        print("\nBy Memory:")
        for proc in process_info['top_memory'][:5]:
            mem = proc['memory_percent'] or 0
            print(f"  {proc['name']:<30} PID: {proc['pid']:<8} MEM: {mem:>5.1f}%")
        
        # Check for alerts
        alerts = self.check_alerts(cpu_info, memory_info, disk_info)
        if alerts:
            print(f"\n🚨 ALERTS")
            print("-" * 80)
            for alert in alerts:
                print(alert)
                self.alerts_triggered.append(alert)
        
        print("\n" + "="*80)
        print("Press Ctrl+C to stop monitoring")
    
    def monitor_continuous(self, interval=2):
        """Continuously monitor system and display dashboard"""
        print("🚀 Starting system monitor...")
        print(f"Update interval: {interval} seconds")
        print(f"Alert thresholds - CPU: {self.alert_cpu}%, Memory: {self.alert_memory}%, Disk: {self.alert_disk}%\n")
        
        try:
            while True:
                self.display_dashboard()
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n\n👋 Monitoring stopped.")
            
            if self.alerts_triggered:
                print(f"\n📊 Total alerts triggered: {len(self.alerts_triggered)}")
                self.save_alerts_log()
    
    def save_alerts_log(self):
        """Save triggered alerts to log file"""
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                for alert in self.alerts_triggered:
                    f.write(alert + '\n')
            print(f"💾 Alerts saved to: {self.log_file}")
        except Exception as e:
            print(f"❌ Error saving log: {e}")
    
    def generate_report(self, output_file='system_report.json'):
        """Generate a system report"""
        report = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'cpu': self.get_cpu_info(),
            'memory': self.get_memory_info(),
            'disk': self.get_disk_info(),
            'network': self.get_network_info(),
            'processes': self.get_process_info(20)
        }
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, default=str)
            print(f"✅ System report saved to: {output_file}")
        except Exception as e:
            print(f"❌ Error saving report: {e}")
    
    def _format_bytes(self, bytes_value):
        """Format bytes to human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.2f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.2f} PB"


def main():
    parser = argparse.ArgumentParser(
        description='Monitor system resources and generate alerts',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python monitor.py
  python monitor.py --interval 5
  python monitor.py --alert-cpu 80 --alert-memory 85
  python monitor.py --report system_status.json
        """
    )
    
    parser.add_argument('--interval', type=int, default=2,
                       help='Update interval in seconds (default: 2)')
    parser.add_argument('--alert-cpu', type=int, default=90,
                       help='CPU usage alert threshold (default: 90%%)')
    parser.add_argument('--alert-memory', type=int, default=90,
                       help='Memory usage alert threshold (default: 90%%)')
    parser.add_argument('--alert-disk', type=int, default=90,
                       help='Disk usage alert threshold (default: 90%%)')
    parser.add_argument('--report', metavar='FILE',
                       help='Generate one-time report and exit')
    
    args = parser.parse_args()
    
    monitor = SystemMonitor(args.alert_cpu, args.alert_memory, args.alert_disk)
    
    if args.report:
        monitor.generate_report(args.report)
    else:
        monitor.monitor_continuous(args.interval)


if __name__ == "__main__":
    main()