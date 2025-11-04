#!/usr/bin/env python3
"""
Bulk File Renamer
Rename multiple files at once using patterns, regex, or sequential numbering
"""

import os
import re
import argparse
from pathlib import Path
import json

class BulkRenamer:
    def __init__(self, directory, dry_run=False):
        self.directory = Path(directory)
        self.dry_run = dry_run
        self.operations = []
    
    def rename_with_pattern(self, pattern, extensions=None, start=1):
        """Rename files with a pattern (e.g., 'photo_{num}')"""
        if not self.directory.exists():
            print(f"❌ Directory '{self.directory}' does not exist!")
            return
        
        print(f"📝 Renaming files in: {self.directory}")
        print(f"Pattern: {pattern}")
        print(f"{'🔍 DRY RUN MODE' if self.dry_run else '✅ Renaming files...'}\n")
        
        # Get files to rename
        files = self._get_files(extensions)
        files.sort()
        
        counter = start
        renamed_count = 0
        
        for file_path in files:
            # Replace {num} with counter
            new_name = pattern.replace('{num}', str(counter).zfill(3))
            
            # Keep the original extension if not in pattern
            if '{ext}' in new_name:
                new_name = new_name.replace('{ext}', file_path.suffix)
            elif not Path(new_name).suffix:
                new_name = new_name + file_path.suffix
            
            new_path = self.directory / new_name
            
            # Skip if same name
            if file_path == new_path:
                continue
            
            # Handle duplicates
            if new_path.exists():
                new_path = self._get_unique_path(new_path)
            
            self.operations.append({
                'old': str(file_path),
                'new': str(new_path)
            })
            
            print(f"  {file_path.name} → {new_path.name}")
            
            if not self.dry_run:
                file_path.rename(new_path)
            
            counter += 1
            renamed_count += 1
        
        print(f"\n✨ {'Would rename' if self.dry_run else 'Renamed'} {renamed_count} file(s)")
        
        if not self.dry_run:
            self._save_undo_info()
    
    def rename_with_regex(self, find, replace, extensions=None):
        """Rename files using regex pattern"""
        if not self.directory.exists():
            print(f"❌ Directory '{self.directory}' does not exist!")
            return
        
        print(f"🔍 Renaming files with regex in: {self.directory}")
        print(f"Find: {find}")
        print(f"Replace: {replace}")
        print(f"{'🔍 DRY RUN MODE' if self.dry_run else '✅ Renaming files...'}\n")
        
        files = self._get_files(extensions)
        renamed_count = 0
        
        for file_path in files:
            stem = file_path.stem
            new_stem = re.sub(find, replace, stem)
            
            if new_stem != stem:
                new_name = new_stem + file_path.suffix
                new_path = self.directory / new_name
                
                if new_path.exists():
                    new_path = self._get_unique_path(new_path)
                
                self.operations.append({
                    'old': str(file_path),
                    'new': str(new_path)
                })
                
                print(f"  {file_path.name} → {new_path.name}")
                
                if not self.dry_run:
                    file_path.rename(new_path)
                
                renamed_count += 1
        
        print(f"\n✨ {'Would rename' if self.dry_run else 'Renamed'} {renamed_count} file(s)")
        
        if not self.dry_run:
            self._save_undo_info()
    
    def change_case(self, case_type, extensions=None):
        """Change filename case (upper, lower, title)"""
        if not self.directory.exists():
            print(f"❌ Directory '{self.directory}' does not exist!")
            return
        
        print(f"🔤 Changing case to {case_type} in: {self.directory}")
        print(f"{'🔍 DRY RUN MODE' if self.dry_run else '✅ Renaming files...'}\n")
        
        files = self._get_files(extensions)
        renamed_count = 0
        
        for file_path in files:
            stem = file_path.stem
            
            if case_type == 'upper':
                new_stem = stem.upper()
            elif case_type == 'lower':
                new_stem = stem.lower()
            elif case_type == 'title':
                new_stem = stem.title()
            else:
                continue
            
            if new_stem != stem:
                new_name = new_stem + file_path.suffix
                new_path = self.directory / new_name
                
                if new_path.exists():
                    new_path = self._get_unique_path(new_path)
                
                self.operations.append({
                    'old': str(file_path),
                    'new': str(new_path)
                })
                
                print(f"  {file_path.name} → {new_path.name}")
                
                if not self.dry_run:
                    file_path.rename(new_path)
                
                renamed_count += 1
        
        print(f"\n✨ {'Would rename' if self.dry_run else 'Renamed'} {renamed_count} file(s)")
        
        if not self.dry_run:
            self._save_undo_info()
    
    def add_prefix_suffix(self, prefix='', suffix='', extensions=None):
        """Add prefix and/or suffix to filenames"""
        if not self.directory.exists():
            print(f"❌ Directory '{self.directory}' does not exist!")
            return
        
        print(f"📝 Adding prefix/suffix in: {self.directory}")
        if prefix:
            print(f"Prefix: '{prefix}'")
        if suffix:
            print(f"Suffix: '{suffix}'")
        print(f"{'🔍 DRY RUN MODE' if self.dry_run else '✅ Renaming files...'}\n")
        
        files = self._get_files(extensions)
        renamed_count = 0
        
        for file_path in files:
            stem = file_path.stem
            new_stem = f"{prefix}{stem}{suffix}"
            new_name = new_stem + file_path.suffix
            new_path = self.directory / new_name
            
            if new_path.exists():
                new_path = self._get_unique_path(new_path)
            
            self.operations.append({
                'old': str(file_path),
                'new': str(new_path)
            })
            
            print(f"  {file_path.name} → {new_path.name}")
            
            if not self.dry_run:
                file_path.rename(new_path)
            
            renamed_count += 1
        
        print(f"\n✨ {'Would rename' if self.dry_run else 'Renamed'} {renamed_count} file(s)")
        
        if not self.dry_run:
            self._save_undo_info()
    
    def undo_last_rename(self):
        """Undo the last rename operation"""
        undo_file = self.directory / '.bulk_renamer_undo.json'
        
        if not undo_file.exists():
            print("❌ No undo information found!")
            return
        
        try:
            with open(undo_file, 'r') as f:
                operations = json.load(f)
            
            print(f"↩️  Undoing last rename operation ({len(operations)} files)...\n")
            
            for op in reversed(operations):
                new_path = Path(op['new'])
                old_path = Path(op['old'])
                
                if new_path.exists():
                    new_path.rename(old_path)
                    print(f"  Restored: {new_path.name} → {old_path.name}")
            
            undo_file.unlink()
            print(f"\n✅ Successfully undone last rename operation!")
            
        except Exception as e:
            print(f"❌ Error during undo: {e}")
    
    def _get_files(self, extensions=None):
        """Get list of files to process"""
        files = []
        for file_path in self.directory.iterdir():
            if file_path.is_file():
                if extensions:
                    if file_path.suffix.lower() in extensions:
                        files.append(file_path)
                else:
                    files.append(file_path)
        return files
    
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
        undo_file = self.directory / '.bulk_renamer_undo.json'
        with open(undo_file, 'w') as f:
            json.dump(self.operations, f, indent=2)
        print(f"\n💾 Undo info saved. Run with --undo to reverse this operation.")


def main():
    parser = argparse.ArgumentParser(
        description='Bulk rename files with patterns, regex, or case changes',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python renamer.py ./photos --pattern "vacation_{num}" --start 1
  python renamer.py ./docs --regex "draft" "final"
  python renamer.py ./files --case lower
  python renamer.py ./images --prefix "IMG_" --ext .jpg
  python renamer.py ./folder --undo
        """
    )
    
    parser.add_argument('directory', help='Directory containing files to rename')
    parser.add_argument('--pattern', help='Rename pattern (use {num} for number, {ext} for extension)')
    parser.add_argument('--start', type=int, default=1, help='Starting number for pattern (default: 1)')
    parser.add_argument('--regex', nargs=2, metavar=('FIND', 'REPLACE'), help='Regex find and replace')
    parser.add_argument('--case', choices=['upper', 'lower', 'title'], help='Change case')
    parser.add_argument('--prefix', help='Add prefix to filenames')
    parser.add_argument('--suffix', help='Add suffix to filenames')
    parser.add_argument('--ext', nargs='+', help='Only process files with these extensions')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without renaming')
    parser.add_argument('--undo', action='store_true', help='Undo last rename operation')
    
    args = parser.parse_args()
    
    renamer = BulkRenamer(args.directory, args.dry_run)
    
    # Process extensions
    extensions = None
    if args.ext:
        extensions = [ext if ext.startswith('.') else f'.{ext}' for ext in args.ext]
    
    if args.undo:
        renamer.undo_last_rename()
    elif args.pattern:
        renamer.rename_with_pattern(args.pattern, extensions, args.start)
    elif args.regex:
        renamer.rename_with_regex(args.regex[0], args.regex[1], extensions)
    elif args.case:
        renamer.change_case(args.case, extensions)
    elif args.prefix or args.suffix:
        renamer.add_prefix_suffix(args.prefix or '', args.suffix or '', extensions)
    else:
        print("❌ Please specify a rename operation")
        print("Use --help for more information")


if __name__ == "__main__":
    main()