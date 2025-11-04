#!/usr/bin/env python3
"""
File Organizer
Automatically organize files in a directory by type, date, or custom rules
"""

import os
import shutil
import argparse
from pathlib import Path
from datetime import datetime
import json

class FileOrganizer:
    def __init__(self, directory, dry_run=False):
        self.directory = Path(directory)
        self.dry_run = dry_run
        self.operations = []
        
        # File type categories
        self.categories = {
            'Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.ico'],
            'Documents': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.xls', '.xlsx', '.ppt', '.pptx'],
            'Videos': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm'],
            'Audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a'],
            'Archives': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'],
            'Code': ['.py', '.js', '.html', '.css', '.java', '.cpp', '.c', '.h', '.json', '.xml', '.sql'],
            'Executables': ['.exe', '.msi', '.app', '.deb', '.rpm'],
        }
    
    def organize_by_type(self):
        """Organize files by their extension type"""
        if not self.directory.exists():
            print(f"❌ Directory '{self.directory}' does not exist!")
            return
        
        print(f"📂 Organizing files in: {self.directory}")
        print(f"{'🔍 DRY RUN MODE - No files will be moved' if self.dry_run else '✅ Moving files...'}\n")
        
        files_moved = 0
        
        for file_path in self.directory.iterdir():
            if file_path.is_file():
                category = self._get_category(file_path.suffix.lower())
                
                if category:
                    dest_folder = self.directory / category
                    dest_path = dest_folder / file_path.name
                    
                    # Handle duplicate names
                    if dest_path.exists():
                        dest_path = self._get_unique_path(dest_path)
                    
                    self.operations.append({
                        'source': str(file_path),
                        'destination': str(dest_path),
                        'category': category
                    })
                    
                    if not self.dry_run:
                        dest_folder.mkdir(exist_ok=True)
                        shutil.move(str(file_path), str(dest_path))
                    
                    print(f"  {file_path.name} → {category}/")
                    files_moved += 1
        
        print(f"\n✨ {'Would move' if self.dry_run else 'Moved'} {files_moved} file(s)")
        
        if self.dry_run:
            print("\n💡 Run without --dry-run to actually move files")
        else:
            self._save_undo_info()
    
    def organize_by_date(self):
        """Organize files by creation/modification date"""
        if not self.directory.exists():
            print(f"❌ Directory '{self.directory}' does not exist!")
            return
        
        print(f"📅 Organizing files by date in: {self.directory}")
        print(f"{'🔍 DRY RUN MODE' if self.dry_run else '✅ Moving files...'}\n")
        
        files_moved = 0
        
        for file_path in self.directory.iterdir():
            if file_path.is_file():
                # Get modification time
                mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                year_month = mtime.strftime('%Y-%m')
                
                dest_folder = self.directory / year_month
                dest_path = dest_folder / file_path.name
                
                if dest_path.exists():
                    dest_path = self._get_unique_path(dest_path)
                
                self.operations.append({
                    'source': str(file_path),
                    'destination': str(dest_path),
                    'category': year_month
                })
                
                if not self.dry_run:
                    dest_folder.mkdir(exist_ok=True)
                    shutil.move(str(file_path), str(dest_path))
                
                print(f"  {file_path.name} → {year_month}/")
                files_moved += 1
        
        print(f"\n✨ {'Would move' if self.dry_run else 'Moved'} {files_moved} file(s)")
        
        if not self.dry_run:
            self._save_undo_info()
    
    def undo_last_organization(self):
        """Undo the last organization operation"""
        undo_file = self.directory / '.file_organizer_undo.json'
        
        if not undo_file.exists():
            print("❌ No undo information found!")
            return
        
        try:
            with open(undo_file, 'r') as f:
                operations = json.load(f)
            
            print(f"↩️  Undoing last organization ({len(operations)} operations)...\n")
            
            for op in reversed(operations):
                src = Path(op['destination'])
                dest = Path(op['source'])
                
                if src.exists():
                    shutil.move(str(src), str(dest))
                    print(f"  Restored: {src.name}")
            
            # Remove empty folders
            for item in self.directory.iterdir():
                if item.is_dir() and not any(item.iterdir()):
                    item.rmdir()
                    print(f"  Removed empty folder: {item.name}")
            
            undo_file.unlink()
            print(f"\n✅ Successfully undone last organization!")
            
        except Exception as e:
            print(f"❌ Error during undo: {e}")
    
    def _get_category(self, extension):
        """Get category for a file extension"""
        for category, extensions in self.categories.items():
            if extension in extensions:
                return category
        return 'Others'
    
    def _get_unique_path(self, path):
        """Generate a unique path if file already exists"""
        path = Path(path)
        counter = 1
        while path.exists():
            new_name = f"{path.stem}_{counter}{path.suffix}"
            path = path.parent / new_name
            counter += 1
        return path
    
    def _save_undo_info(self):
        """Save operations for undo functionality"""
        undo_file = self.directory / '.file_organizer_undo.json'
        with open(undo_file, 'w') as f:
            json.dump(self.operations, f, indent=2)
        print(f"\n💾 Undo info saved. Run with --undo to reverse this operation.")


def main():
    parser = argparse.ArgumentParser(
        description='Organize files in a directory automatically',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python organizer.py ~/Downloads --by-type
  python organizer.py ~/Documents --by-date --dry-run
  python organizer.py ~/Desktop --undo
        """
    )
    
    parser.add_argument('directory', help='Directory to organize')
    parser.add_argument('--by-type', action='store_true', help='Organize by file type')
    parser.add_argument('--by-date', action='store_true', help='Organize by date')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without moving files')
    parser.add_argument('--undo', action='store_true', help='Undo last organization')
    
    args = parser.parse_args()
    
    organizer = FileOrganizer(args.directory, args.dry_run)
    
    if args.undo:
        organizer.undo_last_organization()
    elif args.by_date:
        organizer.organize_by_date()
    elif args.by_type:
        organizer.organize_by_type()
    else:
        print("❌ Please specify --by-type or --by-date")
        print("Use --help for more information")


if __name__ == "__main__":
    main()