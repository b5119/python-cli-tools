# Python CLI Tools & Automation Scripts

A collection of practical command-line tools and automation scripts for everyday tasks. These tools demonstrate file operations, system automation, data processing, and productivity enhancements.

## 🎯 Repository Focus

This repository showcases:
- Command-line argument parsing with argparse
- File system operations and automation
- Text processing and data manipulation
- System utilities and productivity tools
- Error handling and logging

## 📚 Projects

### 1. File Organizer
**Difficulty:** Beginner  
**Concepts:** File operations, os module, shutil, directory management

Automatically organize files in a directory by type, date, or custom rules.

**Features:**
- Organize by file extension
- Organize by creation/modification date
- Undo last organization
- Dry-run mode to preview changes
- Custom folder naming rules

**Usage:** `python file_organizer.py <directory> [options]`

---

### 2. Bulk File Renamer
**Difficulty:** Beginner  
**Concepts:** Regex, file operations, batch processing

Rename multiple files at once using patterns, regex, or sequential numbering.

**Features:**
- Pattern-based renaming
- Regex support
- Sequential numbering
- Case conversion
- Preview mode
- Undo functionality

**Usage:** `python bulk_renamer.py <directory> [options]`

---

### 3. Duplicate File Finder
**Difficulty:** Intermediate  
**Concepts:** Hashing, file comparison, optimization

Find and manage duplicate files based on content (MD5/SHA256 hashing).

**Features:**
- Multiple hash algorithms
- Size-based pre-filtering
- Interactive deletion
- Move duplicates to folder
- Generate duplicate report
- Safe mode with confirmation

**Usage:** `python duplicate_finder.py <directory> [options]`

---

### 4. Log File Analyzer
**Difficulty:** Intermediate  
**Concepts:** Text parsing, regex, data analysis, reporting

Parse and analyze log files to extract insights and generate reports.

**Features:**
- Extract error patterns
- Count log levels (INFO, WARNING, ERROR)
- Time-based analysis
- Export statistics to CSV/JSON
- Filter by date range
- Generate visualizations

**Usage:** `python log_analyzer.py <logfile> [options]`

---

### 5. Batch Image Processor
**Difficulty:** Intermediate  
**Concepts:** Image manipulation, batch processing, Pillow library

Process multiple images at once: resize, convert, compress, watermark.

**Features:**
- Resize images (maintain aspect ratio)
- Format conversion (PNG, JPG, WebP)
- Compression with quality control
- Add watermarks
- Batch processing
- Progress indicators

**Usage:** `python image_processor.py <input_dir> [options]`

---

### 6. System Monitor
**Difficulty:** Advanced  
**Concepts:** System information, psutil, monitoring, alerts

Monitor system resources (CPU, Memory, Disk) and send alerts.

**Features:**
- Real-time CPU/Memory monitoring
- Disk usage tracking
- Process listing
- Alert thresholds
- Export logs
- Dashboard view

**Usage:** `python system_monitor.py [options]`

---

## 🚀 Getting Started

### Prerequisites
```bash
Python 3.8 or higher
```

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/python-cli-tools.git
cd python-cli-tools
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Usage Examples

```bash
# Organize downloads folder
python 01-file-organizer/organizer.py ~/Downloads --by-type

# Rename photos sequentially
python 02-bulk-renamer/renamer.py ./photos --pattern "vacation_{num}" --start 1

# Find duplicate files
python 03-duplicate-finder/finder.py ~/Documents --delete

# Analyze web server logs
python 04-log-analyzer/analyzer.py access.log --errors-only

# Resize all images to 800px width
python 05-image-processor/processor.py ./images --resize 800

# Monitor system with alerts
python 06-system-monitor/monitor.py --alert-cpu 80 --alert-memory 90
```

## 📦 Dependencies

```
Pillow>=10.0.0
psutil>=5.9.0
colorama>=0.4.6
tqdm>=4.65.0
```

Install all dependencies:
```bash
pip install -r requirements.txt
```

## 📁 Project Structure

```
python-cli-tools/
├── README.md
├── requirements.txt
├── 01-file-organizer/
│   └── organizer.py
├── 02-bulk-renamer/
│   └── renamer.py
├── 03-duplicate-finder/
│   └── finder.py
├── 04-log-analyzer/
│   └── analyzer.py
├── 05-image-processor/
│   └── processor.py
└── 06-system-monitor/
    └── monitor.py
```

## 🎓 Learning Objectives

- **Argparse**: Building robust CLI interfaces
- **File Operations**: Reading, writing, moving, copying files
- **Path Handling**: Using pathlib for cross-platform compatibility
- **Error Handling**: Try-except blocks, logging
- **Performance**: Efficient file processing
- **User Experience**: Progress bars, colored output
- **System Programming**: Interacting with OS

## 🛠️ Common Options

Most tools support these common flags:

- `--help, -h` - Show help message
- `--verbose, -v` - Verbose output
- `--dry-run` - Preview changes without executing
- `--recursive, -r` - Process subdirectories
- `--output, -o` - Specify output location

## 💡 Pro Tips

1. **Always use --dry-run first** to preview changes
2. **Backup important files** before bulk operations
3. **Use absolute paths** to avoid confusion
4. **Check permissions** before file operations
5. **Read the help** with `--help` flag

## 🔧 Troubleshooting

### Permission Errors
```bash
# Run with elevated permissions (use cautiously)
sudo python script.py [args]
```

### Module Not Found
```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

### Path Issues
```bash
# Use absolute paths
python script.py /full/path/to/directory
```

## 🤝 Contributing

Contributions are welcome! Ideas for new tools:
- PDF merger/splitter
- Text file diff tool
- Backup automation script
- Database backup tool
- Git automation utilities

## 📄 License

This project is licensed under the MIT License.

## 👤 Author

Frank Bwalya- https://github.com/b5119

## 🌟 Acknowledgments

- Python standard library documentation
- Pillow (PIL) documentation
- psutil documentation

---

⭐ **Star this repository if you find it useful!**

## 📊 Tool Comparison

| Tool | Difficulty | Primary Use | Dependencies |
|------|-----------|-------------|--------------|
| File Organizer | ⭐ Beginner | Clean messy directories | Built-in only |
| Bulk Renamer | ⭐ Beginner | Rename multiple files | Built-in only |
| Duplicate Finder | ⭐⭐ Intermediate | Free up disk space | Built-in only |
| Log Analyzer | ⭐⭐ Intermediate | Debug applications | Built-in only |
| Image Processor | ⭐⭐ Intermediate | Batch image editing | Pillow |
| System Monitor | ⭐⭐⭐ Advanced | System health checks | psutil |
