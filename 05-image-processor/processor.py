
"""
Batch Image Processor
Process multiple images at once: resize, convert, compress, watermark
Requires: pip install Pillow
"""

import argparse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import os

class ImageProcessor:
    def __init__(self, input_dir, output_dir=None):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir) if output_dir else self.input_dir / 'processed'
        self.supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp', '.tiff'}
        self.processed_count = 0
    
    def get_images(self):
        """Get list of image files"""
        images = []
        for file_path in self.input_dir.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in self.supported_formats:
                images.append(file_path)
        return images
    
    def resize_images(self, width=None, height=None, maintain_aspect=True):
        """Resize images to specified dimensions"""
        if not self.input_dir.exists():
            print(f"❌ Input directory '{self.input_dir}' does not exist!")
            return
        
        images = self.get_images()
        if not images:
            print("❌ No images found!")
            return
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"🖼️  Resizing {len(images)} image(s)...")
        print(f"Target size: {width or 'auto'}x{height or 'auto'}")
        print(f"Maintain aspect ratio: {maintain_aspect}\n")
        
        for img_path in images:
            try:
                with Image.open(img_path) as img:
                    original_size = img.size
                    
                    if maintain_aspect:
                        # Calculate new size maintaining aspect ratio
                        if width and not height:
                            ratio = width / img.width
                            new_size = (width, int(img.height * ratio))
                        elif height and not width:
                            ratio = height / img.height
                            new_size = (int(img.width * ratio), height)
                        elif width and height:
                            img.thumbnail((width, height), Image.Resampling.LANCZOS)
                            new_size = img.size
                        else:
                            print(f"⚠️  Skipping {img_path.name}: No dimensions specified")
                            continue
                    else:
                        new_size = (width or img.width, height or img.height)
                    
                    if maintain_aspect and (width and not height or height and not width):
                        resized = img.resize(new_size, Image.Resampling.LANCZOS)
                    else:
                        resized = img
                    
                    output_path = self.output_dir / img_path.name
                    resized.save(output_path, quality=95)
                    
                    print(f"✅ {img_path.name}: {original_size} → {new_size}")
                    self.processed_count += 1
                    
            except Exception as e:
                print(f"❌ Error processing {img_path.name}: {e}")
        
        print(f"\n✨ Processed {self.processed_count} image(s)")
        print(f"📁 Output directory: {self.output_dir}")
    
    def convert_format(self, output_format):
        """Convert images to different format"""
        if not self.input_dir.exists():
            print(f"❌ Input directory '{self.input_dir}' does not exist!")
            return
        
        images = self.get_images()
        if not images:
            print("❌ No images found!")
            return
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        output_format = output_format.lower().replace('.', '')
        
        print(f"🔄 Converting {len(images)} image(s) to {output_format.upper()}...\n")
        
        for img_path in images:
            try:
                with Image.open(img_path) as img:
                    # Convert RGBA to RGB for JPEG
                    if output_format in ['jpg', 'jpeg'] and img.mode in ['RGBA', 'LA', 'P']:
                        rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                        if img.mode == 'P':
                            img = img.convert('RGBA')
                        rgb_img.paste(img, mask=img.split()[-1] if img.mode in ['RGBA', 'LA'] else None)
                        img = rgb_img
                    
                    output_name = img_path.stem + f'.{output_format}'
                    output_path = self.output_dir / output_name
                    
                    img.save(output_path, quality=95)
                    
                    print(f"✅ {img_path.name} → {output_name}")
                    self.processed_count += 1
                    
            except Exception as e:
                print(f"❌ Error converting {img_path.name}: {e}")
        
        print(f"\n✨ Converted {self.processed_count} image(s)")
        print(f"📁 Output directory: {self.output_dir}")
    
    def compress_images(self, quality=85):
        """Compress images to reduce file size"""
        if not self.input_dir.exists():
            print(f"❌ Input directory '{self.input_dir}' does not exist!")
            return
        
        images = self.get_images()
        if not images:
            print("❌ No images found!")
            return
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"📦 Compressing {len(images)} image(s) with quality {quality}%...\n")
        
        total_original_size = 0
        total_compressed_size = 0
        
        for img_path in images:
            try:
                original_size = img_path.stat().st_size
                total_original_size += original_size
                
                with Image.open(img_path) as img:
                    output_path = self.output_dir / img_path.name
                    
                    # Optimize based on format
                    if img_path.suffix.lower() in ['.jpg', '.jpeg']:
                        img.save(output_path, 'JPEG', quality=quality, optimize=True)
                    elif img_path.suffix.lower() == '.png':
                        img.save(output_path, 'PNG', optimize=True)
                    else:
                        img.save(output_path, quality=quality, optimize=True)
                    
                    compressed_size = output_path.stat().st_size
                    total_compressed_size += compressed_size
                    
                    reduction = ((original_size - compressed_size) / original_size) * 100
                    
                    print(f"✅ {img_path.name}: {self._format_size(original_size)} → "
                          f"{self._format_size(compressed_size)} (-{reduction:.1f}%)")
                    self.processed_count += 1
                    
            except Exception as e:
                print(f"❌ Error compressing {img_path.name}: {e}")
        
        total_reduction = ((total_original_size - total_compressed_size) / total_original_size) * 100
        
        print(f"\n✨ Compressed {self.processed_count} image(s)")
        print(f"💾 Total saved: {self._format_size(total_original_size - total_compressed_size)} "
              f"(-{total_reduction:.1f}%)")
        print(f"📁 Output directory: {self.output_dir}")
    
    def add_watermark(self, text, position='bottom-right', opacity=128):
        """Add text watermark to images"""
        if not self.input_dir.exists():
            print(f"❌ Input directory '{self.input_dir}' does not exist!")
            return
        
        images = self.get_images()
        if not images:
            print("❌ No images found!")
            return
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"💧 Adding watermark '{text}' to {len(images)} image(s)...\n")
        
        for img_path in images:
            try:
                with Image.open(img_path) as img:
                    # Convert to RGBA if necessary
                    if img.mode != 'RGBA':
                        img = img.convert('RGBA')
                    
                    # Create watermark layer
                    watermark = Image.new('RGBA', img.size, (0, 0, 0, 0))
                    draw = ImageDraw.Draw(watermark)
                    
                    # Try to use a nice font, fall back to default
                    try:
                        font_size = max(20, img.height // 30)
                        font = ImageFont.truetype("arial.ttf", font_size)
                    except:
                        font = ImageFont.load_default()
                    
                    # Get text bounding box
                    bbox = draw.textbbox((0, 0), text, font=font)
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]
                    
                    # Calculate position
                    margin = 10
                    if position == 'bottom-right':
                        x = img.width - text_width - margin
                        y = img.height - text_height - margin
                    elif position == 'bottom-left':
                        x = margin
                        y = img.height - text_height - margin
                    elif position == 'top-right':
                        x = img.width - text_width - margin
                        y = margin
                    elif position == 'top-left':
                        x = margin
                        y = margin
                    elif position == 'center':
                        x = (img.width - text_width) // 2
                        y = (img.height - text_height) // 2
                    else:
                        x = img.width - text_width - margin
                        y = img.height - text_height - margin
                    
                    # Draw text with semi-transparency
                    draw.text((x, y), text, fill=(255, 255, 255, opacity), font=font)
                    
                    # Composite watermark onto image
                    watermarked = Image.alpha_composite(img, watermark)
                    
                    # Convert back to original mode if needed
                    if img_path.suffix.lower() in ['.jpg', '.jpeg']:
                        watermarked = watermarked.convert('RGB')
                    
                    output_path = self.output_dir / img_path.name
                    watermarked.save(output_path, quality=95)
                    
                    print(f"✅ {img_path.name}")
                    self.processed_count += 1
                    
            except Exception as e:
                print(f"❌ Error watermarking {img_path.name}: {e}")
        
        print(f"\n✨ Watermarked {self.processed_count} image(s)")
        print(f"📁 Output directory: {self.output_dir}")
    
    def _format_size(self, size):
        """Format file size in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} TB"


def main():
    parser = argparse.ArgumentParser(
        description='Batch process images: resize, convert, compress, watermark',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python processor.py ./images --resize 800
  python processor.py ./photos --resize 1920 1080 --no-aspect
  python processor.py ./pics --convert jpg
  python processor.py ./images --compress 75
  python processor.py ./photos --watermark "© 2024" --position bottom-right
  python processor.py ./images --resize 1000 --output ./processed
        """
    )
    
    parser.add_argument('input_dir', help='Input directory containing images')
    parser.add_argument('--output', '-o', help='Output directory (default: input_dir/processed)')
    
    # Resize options
    parser.add_argument('--resize', nargs='+', type=int, metavar=('WIDTH', 'HEIGHT'),
                       help='Resize images (provide width and/or height)')
    parser.add_argument('--no-aspect', action='store_true', help='Do not maintain aspect ratio')
    
    # Convert options
    parser.add_argument('--convert', choices=['jpg', 'jpeg', 'png', 'webp', 'bmp'],
                       help='Convert images to format')
    
    # Compress options
    parser.add_argument('--compress', type=int, metavar='QUALITY',
                       help='Compress images (quality 1-100, default: 85)')
    
    # Watermark options
    parser.add_argument('--watermark', metavar='TEXT', help='Add text watermark')
    parser.add_argument('--position', choices=['top-left', 'top-right', 'bottom-left', 
                                               'bottom-right', 'center'],
                       default='bottom-right', help='Watermark position')
    parser.add_argument('--opacity', type=int, default=128,
                       help='Watermark opacity (0-255, default: 128)')
    
    args = parser.parse_args()
    
    processor = ImageProcessor(args.input_dir, args.output)
    
    # Process images based on options
    if args.resize:
        if len(args.resize) == 1:
            width = args.resize[0]
            height = None
        elif len(args.resize) == 2:
            width, height = args.resize
        else:
            print("❌ --resize takes 1 or 2 arguments (width and/or height)")
            return
        
        processor.resize_images(width, height, not args.no_aspect)
    
    elif args.convert:
        processor.convert_format(args.convert)
    
    elif args.compress is not None:
        quality = max(1, min(100, args.compress))  # Clamp to 1-100
        processor.compress_images(quality)
    
    elif args.watermark:
        processor.add_watermark(args.watermark, args.position, args.opacity)
    
    else:
        print("❌ Please specify an operation: --resize, --convert, --compress, or --watermark")
        print("Use --help for more information")


if __name__ == "__main__":
    main()