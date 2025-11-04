"""
Duplicate File Finder
Find and manage duplicate files based on content (MD5/SHA256 hashing)
"""

import os
import hashlib
import argparse
from pathlib import Path
from collections import defaultdict
import shutil

class DuplicateFinder:
    def __init__(self, directory, recursive=False):
        self.directory = Path(directory)
        self.recursive = recursive
        self.duplicates = defaultdict(list)
        self.hash_algorithm = 'md5'
    
    def find_duplicates(self, algorithm='md5'):
        """Find duplicate files using file hashing"""
        self.hash_algorithm = algorithm
        
        if not self.directory.exists():
            print(f"❌ Directory '{self.directory}' does not exist!")
            return
        
        print(f"🔍 Scanning for duplicate files in: {self.directory}")
        print(f"Algorithm: {algorithm.upper()}")
        print(f"{'Recursive: Yes' if self.recursive else 'Recursive: No'}\n")
        
        # First pass: Group by size (optimization)
        size_groups = defaultdict(list)
        files = self._get_files()
        
        print(f"📊 Found {len(files)} file(s) to analyze...")
        
        for file_path in files:
            try:
                size = file_path.stat().st_size
                size_groups[size].append(file_path)
            except Exception as e:
                print(f"⚠️  Error accessing {file_path}: {e}")
        
        # Second pass: Hash files with same size
        print("\n🔐 Computing file hashes...")
        hash_dict = {}
        processed = 0
        
        for size, file_list in size_groups.items():
            if len(file_list) > 1:  # Only hash if multiple files have same size
                for file_path in file_list:
                    try:
                        file_hash = self._hash_file(file_path)
                        
                        if file_hash in hash_dict:
                            self.duplicates[file_hash].append(file_path)
                            if len(self.duplicates[file_hash]) == 1:
                                self.duplicates[file_hash].insert(0, hash_dict[file_hash])
                        else:
                            hash_dict[file_hash] = file_path
                        
                        processed += 1
                        if processed % 10 == 0:
                            print(f"  Processed {processed} files...", end='\r')
                    
                    except Exception as e:
                        print(f"\n⚠️  Error hashing {file_path}: {e}")
        
        print(f"\n✅ Processed {processed} files")
        
        # Remove entries with no duplicates
        self.duplicates = {k: v for k, v in self.duplicates.items() if len(v) > 1}
        
        return self.duplicates
    
    def display_duplicates(self):
        """Display found duplicates"""
        if not self.duplicates:
            print("\n✨ No duplicate files found!")
            return
        
        total_duplicates = sum(len(files) - 1 for files in self.duplicates.values())
        total_waste = 0
        
        print(f"\n{'='*80}")
        print(f"📋 DUPLICATE FILES REPORT")
        print(f"{'='*80}\n")
        
        for i, (file_hash, files) in enumerate(self.duplicates.items(), 1):
            file_size = files[0].stat().st_size
            wasted_space = file_size * (len(files) - 1)
            total_waste += wasted_space
            
            print(f"Group {i} - {len(files)} copies ({self._format_size(file_size)} each)")
            print(f"Hash: {file_hash[:16]}...")
            print(f"Wasted space: {self._format_size(wasted_space)}")
            
            for j, file_path in enumerate(files):
                marker = "🟢 [KEEP]" if j == 0 else "🔴 [DUPLICATE]"
                print(f"  {marker} {file_path}")
            print()
        
        print(f"{'='*80}")
        print(f"Summary:")
        print(f"  Total duplicate files: {total_duplicates}")
        print(f"  Total wasted space: {self._format_size(total_waste)}")
        print(f"{'='*80}\n")
    
    def delete_duplicates(self, interactive=True):
        """Delete duplicate files (keeps first occurrence)"""
        if not self.duplicates:
            print("No duplicates to delete!")
            return
        
        deleted_count = 0
        freed_space = 0
        
        for file_hash, files in self.duplicates.items():
            # Keep first file, delete rest
            for file_path in files[1:]:
                if interactive:
                    response = input(f"Delete {file_path}? (y/n): ").lower()
                    if response != 'y':
                        continue
                
                try:
                    file_size = file_path.stat().st_size
                    file_path.unlink()
                    print(f"🗑️  Deleted: {file_path}")
                    deleted_count += 1
                    freed_space += file_size
                except Exception as e:
                    print(f"❌ Error deleting {file_path}: {e}")
        
        print(f"\n✅ Deleted {deleted_count} duplicate file(s)")
        print(f"💾 Freed {self._format_size(freed_space)} of space")
    
    def move_duplicates(self, destination):
        """Move duplicate files to a separate folder"""
        if not self.duplicates:
            print("No duplicates to move!")
            return
        
        dest_dir = Path(destination)
        dest_dir.mkdir(parents=True, exist_ok=True)
        
        moved_count = 0
        
        print(f"📦 Moving duplicates to: {dest_dir}\n")
        
        for file_hash, files in self.duplicates.items():
            # Move all but first file
            for file_path in files[1:]:
                try:
                    dest_path = dest_dir / file_path.name
                    
                    # Handle name conflicts
                    if dest_path.exists():
                        dest_path = self._get_unique_path(dest_path)
                    
                    shutil.move(str(file_path), str(dest_path))
                    print(f"📦 Moved: {file_path.name}")
                    moved_count += 1
                except Exception as e:
                    print(f"❌ Error moving {file_path}: {e}")
        
        print(f"\n✅ Moved {moved_count} duplicate file(s)")
    
    def generate_report(self, output_file='duplicates_report.txt'):
        """Generate a text report of duplicates"""
        if not self.duplicates:
            print("No duplicates to report!")
            return
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("DUPLICATE FILES REPORT\n")
            f.write("=" * 80 + "\n\n")
            
            for i, (file_hash, files) in enumerate(self.duplicates.items(), 1):
                file_size = files[0].stat().st_size
                
                f.write(f"Group {i} - {len(files)} copies\n")
                f.write(f"Size: {self._format_size(file_size)}\n")
                f.write(f"Hash: {file_hash}\n")
                
                for j, file_path in enumerate(files):
                    status = "ORIGINAL" if j == 0 else "DUPLICATE"
                    f.write(f"  [{status}] {file_path}\n")
                f.write("\n")
            
            total_duplicates = sum(len(files) - 1 for files in self.duplicates.values())
            total_waste = sum(
                files[0].stat().st_size * (len(files) - 1)
                for files in self.duplicates.values()
            )
            
            f.write("=" * 80 + "\n")
            f.write(f"Total duplicate files: {total_duplicates}\n")
            f.write(f"Total wasted space: {self._format_size(total_waste)}\n")
        
        print(f"✅ Report saved to: {output_file}")
    
    def _get_files(self):
        """Get list of files to process"""
        if self.recursive:
            return [p for p in self.directory.rglob('*') if p.is_file()]
        else:
            return [p for p in self.directory.iterdir() if p.is_file()]
    
    def _hash_file(self, file_path, chunk_size=8192):
        """Compute hash of a file"""
        if self.hash_algorithm == 'md5':
            hasher = hashlib.md5()
        elif self.hash_algorithm == 'sha256':
            hasher = hashlib.sha256()
        else:
            hasher = hashlib.md5()
        
        with open(file_path, 'rb') as f:
            while chunk := f.read(chunk_size):
                hasher.update(chunk)
        
        return hasher.hexdigest()
    
    def _format_size(self, size):
        """Format file size in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} PB"
    
    def _get_unique_path(self, path):
        """Generate a unique path if file already exists"""
        path = Path(path)
        counter = 1
        while path.exists():
            new_name = f"{path.stem}_{counter}{path.suffix}"
            path = path.parent / new_name
            counter += 1
        return path


def main():
    parser = argparse.ArgumentParser(
        description='Find and manage duplicate files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python finder.py ~/Downloads
  python finder.py ~/Documents --recursive --algorithm sha256
  python finder.py ~/Photos --delete --interactive
  python finder.py ~/Files --move ./duplicates
  python finder.py ~/Data --report duplicates.txt
        """
    )
    
    parser.add_argument('directory', help='Directory to scan for duplicates')
    parser.add_argument('-r', '--recursive', action='store_true', help='Scan subdirectories')
    parser.add_argument('--algorithm', choices=['md5', 'sha256'], default='md5',
                       help='Hash algorithm (default: md5)')
    parser.add_argument('--delete', action='store_true', help='Delete duplicate files')
    parser.add_argument('--interactive', action='store_true', help='Confirm each deletion')
    parser.add_argument('--move', metavar='DEST', help='Move duplicates to directory')
    parser.add_argument('--report', metavar='FILE', help='Generate report file')
    
    args = parser.parse_args()
    
    finder = DuplicateFinder(args.directory, args.recursive)
    
    # Find duplicates
    finder.find_duplicates(args.algorithm)
    
    # Display results
    finder.display_duplicates()
    
    # Perform actions
    if args.delete:
        if not args.interactive:
            confirm = input("\n⚠️  Delete ALL duplicates without confirmation? (yes/no): ")
            if confirm.lower() != 'yes':
                print("Cancelled.")
                return
        finder.delete_duplicates(args.interactive)
    
    elif args.move:
        finder.move_duplicates(args.move)
    
    elif args.report:
        finder.generate_report(args.report)


if __name__ == "__main__":
    main()