#!/usr/bin/env python3
"""
Log File Analyzer
Parse and analyze log files to extract insights and generate reports
"""

import re
import argparse
from pathlib import Path
from datetime import datetime
from collections import Counter, defaultdict
import csv
import json

class LogAnalyzer:
    def __init__(self, logfile):
        self.logfile = Path(logfile)
        self.entries = []
        self.stats = {
            'total_lines': 0,
            'log_levels': Counter(),
            'errors': [],
            'warnings': [],
            'time_distribution': defaultdict(int)
        }
        
        # Common log patterns
        self.patterns = {
            'apache': r'(\S+) \S+ \S+ \[(.*?)\] "(\S+) (\S+) (\S+)" (\d+) (\d+)',
            'nginx': r'(\S+) - - \[(.*?)\] "(\S+) (\S+) (\S+)" (\d+) (\d+)',
            'python': r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) - (\w+) - (.*)',
            'generic': r'(\d{4}-\d{2}-\d{2}|\d{2}/\w{3}/\d{4}).*?(ERROR|WARN|INFO|DEBUG).*'
        }
    
    def parse_log(self, log_format='generic'):
        """Parse log file"""
        if not self.logfile.exists():
            print(f"❌ Log file '{self.logfile}' does not exist!")
            return False
        
        print(f"📖 Parsing log file: {self.logfile}")
        print(f"Format: {log_format}\n")
        
        try:
            with open(self.logfile, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    self.stats['total_lines'] += 1
                    line = line.strip()
                    
                    if not line:
                        continue
                    
                    # Extract log level
                    level = self._extract_log_level(line)
                    if level:
                        self.stats['log_levels'][level] += 1
                        
                        entry = {
                            'line_number': line_num,
                            'level': level,
                            'message': line
                        }
                        
                        # Store errors and warnings separately
                        if level == 'ERROR':
                            self.stats['errors'].append(entry)
                        elif level in ['WARN', 'WARNING']:
                            self.stats['warnings'].append(entry)
                        
                        self.entries.append(entry)
                    
                    # Extract timestamp for time distribution
                    timestamp = self._extract_timestamp(line)
                    if timestamp:
                        hour = timestamp.hour
                        self.stats['time_distribution'][hour] += 1
            
            print(f"✅ Parsed {self.stats['total_lines']} lines")
            return True
            
        except Exception as e:
            print(f"❌ Error parsing log file: {e}")
            return False
    
    def display_statistics(self):
        """Display log statistics"""
        print(f"\n{'='*80}")
        print(f"📊 LOG FILE STATISTICS")
        print(f"{'='*80}\n")
        
        print(f"File: {self.logfile.name}")
        print(f"Total lines: {self.stats['total_lines']:,}")
        print(f"Log entries: {len(self.entries):,}\n")
        
        # Log level distribution
        print("📋 Log Level Distribution:")
        if self.stats['log_levels']:
            for level, count in self.stats['log_levels'].most_common():
                percentage = (count / len(self.entries)) * 100
                bar = '█' * int(percentage / 2)
                print(f"  {level:<10} {count:>6} ({percentage:>5.1f}%) {bar}")
        else:
            print("  No log levels detected")
        
        print(f"\n🔴 Errors: {len(self.stats['errors'])}")
        print(f"⚠️  Warnings: {len(self.stats['warnings'])}")
        
        # Time distribution
        if self.stats['time_distribution']:
            print(f"\n⏰ Activity by Hour:")
            for hour in sorted(self.stats['time_distribution'].keys()):
                count = self.stats['time_distribution'][hour]
                bar = '█' * (count // 10)
                print(f"  {hour:02d}:00 {count:>6} {bar}")
    
    def show_errors(self, limit=10):
        """Display recent errors"""
        if not self.stats['errors']:
            print("\n✨ No errors found!")
            return
        
        print(f"\n{'='*80}")
        print(f"🔴 ERROR LOG (showing last {min(limit, len(self.stats['errors']))} errors)")
        print(f"{'='*80}\n")
        
        for entry in self.stats['errors'][-limit:]:
            print(f"Line {entry['line_number']}:")
            print(f"  {entry['message']}\n")
    
    def show_warnings(self, limit=10):
        """Display recent warnings"""
        if not self.stats['warnings']:
            print("\n✨ No warnings found!")
            return
        
        print(f"\n{'='*80}")
        print(f"⚠️  WARNING LOG (showing last {min(limit, len(self.stats['warnings']))} warnings)")
        print(f"{'='*80}\n")
        
        for entry in self.stats['warnings'][-limit:]:
            print(f"Line {entry['line_number']}:")
            print(f"  {entry['message']}\n")
    
    def search_pattern(self, pattern):
        """Search for a pattern in log file"""
        print(f"\n🔍 Searching for pattern: {pattern}\n")
        
        matches = []
        try:
            regex = re.compile(pattern, re.IGNORECASE)
            
            for entry in self.entries:
                if regex.search(entry['message']):
                    matches.append(entry)
            
            if matches:
                print(f"Found {len(matches)} match(es):\n")
                for entry in matches[:20]:  # Show first 20
                    print(f"Line {entry['line_number']} [{entry['level']}]:")
                    print(f"  {entry['message']}\n")
                
                if len(matches) > 20:
                    print(f"... and {len(matches) - 20} more matches")
            else:
                print("No matches found.")
                
        except re.error as e:
            print(f"❌ Invalid regex pattern: {e}")
    
    def export_to_csv(self, output_file='log_analysis.csv'):
        """Export statistics to CSV"""
        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # Write header
                writer.writerow(['Metric', 'Value'])
                
                # Write statistics
                writer.writerow(['Total Lines', self.stats['total_lines']])
                writer.writerow(['Log Entries', len(self.entries)])
                writer.writerow(['Errors', len(self.stats['errors'])])
                writer.writerow(['Warnings', len(self.stats['warnings'])])
                writer.writerow([])
                
                # Write log level distribution
                writer.writerow(['Log Level', 'Count', 'Percentage'])
                for level, count in self.stats['log_levels'].most_common():
                    percentage = (count / len(self.entries)) * 100 if self.entries else 0
                    writer.writerow([level, count, f"{percentage:.2f}%"])
            
            print(f"✅ Statistics exported to: {output_file}")
            
        except Exception as e:
            print(f"❌ Error exporting to CSV: {e}")
    
    def export_to_json(self, output_file='log_analysis.json'):
        """Export full analysis to JSON"""
        try:
            data = {
                'file': str(self.logfile),
                'analyzed_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'statistics': {
                    'total_lines': self.stats['total_lines'],
                    'log_entries': len(self.entries),
                    'errors': len(self.stats['errors']),
                    'warnings': len(self.stats['warnings']),
                    'log_levels': dict(self.stats['log_levels']),
                    'time_distribution': dict(self.stats['time_distribution'])
                },
                'errors': [
                    {'line': e['line_number'], 'message': e['message']}
                    for e in self.stats['errors'][-50:]  # Last 50 errors
                ],
                'warnings': [
                    {'line': w['line_number'], 'message': w['message']}
                    for w in self.stats['warnings'][-50:]  # Last 50 warnings
                ]
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Full analysis exported to: {output_file}")
            
        except Exception as e:
            print(f"❌ Error exporting to JSON: {e}")
    
    def _extract_log_level(self, line):
        """Extract log level from line"""
        levels = ['ERROR', 'FATAL', 'CRITICAL', 'WARNING', 'WARN', 'INFO', 'DEBUG', 'TRACE']
        line_upper = line.upper()
        
        for level in levels:
            if level in line_upper:
                return level
        
        return None
    
    def _extract_timestamp(self, line):
        """Extract timestamp from line"""
        # Common timestamp patterns
        patterns = [
            r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})',
            r'(\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2})',
            r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, line)
            if match:
                try:
                    timestamp_str = match.group(1)
                    # Try different formats
                    for fmt in ['%Y-%m-%d %H:%M:%S', '%d/%b/%Y:%H:%M:%S']:
                        try:
                            return datetime.strptime(timestamp_str, fmt)
                        except ValueError:
                            continue
                except Exception:
                    pass
        
        return None


def main():
    parser = argparse.ArgumentParser(
        description='Analyze log files and generate reports',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python analyzer.py application.log
  python analyzer.py access.log --errors-only
  python analyzer.py system.log --search "timeout"
  python analyzer.py app.log --export-csv stats.csv
  python analyzer.py server.log --export-json report.json
        """
    )
    
    parser.add_argument('logfile', help='Path to log file')
    parser.add_argument('--format', choices=['apache', 'nginx', 'python', 'generic'],
                       default='generic', help='Log format (default: generic)')
    parser.add_argument('--errors-only', action='store_true', help='Show only errors')
    parser.add_argument('--warnings-only', action='store_true', help='Show only warnings')
    parser.add_argument('--search', metavar='PATTERN', help='Search for pattern in logs')
    parser.add_argument('--limit', type=int, default=10, help='Limit results (default: 10)')
    parser.add_argument('--export-csv', metavar='FILE', help='Export statistics to CSV')
    parser.add_argument('--export-json', metavar='FILE', help='Export full analysis to JSON')
    
    args = parser.parse_args()
    
    analyzer = LogAnalyzer(args.logfile)
    
    # Parse log file
    if not analyzer.parse_log(args.format):
        return
    
    # Display results based on options
    if args.errors_only:
        analyzer.show_errors(args.limit)
    elif args.warnings_only:
        analyzer.show_warnings(args.limit)
    elif args.search:
        analyzer.search_pattern(args.search)
    else:
        analyzer.display_statistics()
    
    # Export if requested
    if args.export_csv:
        analyzer.export_to_csv(args.export_csv)
    
    if args.export_json:
        analyzer.export_to_json(args.export_json)


if __name__ == "__main__":
    main()