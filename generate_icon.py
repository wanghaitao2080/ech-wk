#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成程序图标
支持 Windows (.ico) 和 macOS (.icns)
"""

import sys
from pathlib import Path

try:
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor
    from PyQt5.QtCore import QSize, Qt
except ImportError:
    print("错误: 需要安装 PyQt5")
    print("安装命令: pip install PyQt5")
    sys.exit(1)


def create_matrix_icon_pixmap(size):
    """创建指定尺寸的图标"""
    pixmap = QPixmap(size, size)
    pixmap.fill(QColor(0, 0, 0))  # 黑色背景
    
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    
    # 绘制绿色边框
    painter.setPen(QColor(0, 255, 65))  # 矩阵绿
    painter.setBrush(Qt.NoBrush)
    border_width = max(2, size // 16)
    painter.drawRect(border_width, border_width, size - border_width * 2, size - border_width * 2)
    
    # 绘制内部装饰（矩阵代码风格）
    if size >= 32:
        # 绘制对角线
        if size >= 48:
            painter.setPen(QColor(0, 255, 65))
            margin = size // 8
            painter.drawLine(margin, margin, size - margin, size - margin)
            painter.drawLine(size - margin, margin, margin, size - margin)
        
        # 绘制中心点
        center = size // 2
        painter.setBrush(QColor(0, 255, 65))
        dot_size = max(2, size // 16)
        painter.drawEllipse(center - dot_size, center - dot_size, dot_size * 2, dot_size * 2)
        
        # 绘制一些装饰线条
        if size >= 64:
            # 绘制四个角的装饰
            corner_size = size // 4
            painter.setPen(QColor(0, 200, 50))  # 稍暗的绿色
            margin = size // 16
            # 左上角
            painter.drawLine(margin, margin, corner_size, margin)
            painter.drawLine(margin, margin, margin, corner_size)
            # 右上角
            painter.drawLine(size - margin, margin, size - corner_size, margin)
            painter.drawLine(size - margin, margin, size - margin, corner_size)
            # 左下角
            painter.drawLine(margin, size - margin, corner_size, size - margin)
            painter.drawLine(margin, size - margin, margin, size - corner_size)
            # 右下角
            painter.drawLine(size - margin, size - margin, size - corner_size, size - margin)
            painter.drawLine(size - margin, size - margin, size - margin, size - corner_size)
    
    painter.end()
    return pixmap


def create_ico_file(output_path):
    """创建 Windows .ico 文件"""
    try:
        # 尝试使用 PIL/Pillow 创建 ICO 文件
        from PIL import Image
        
        # 创建多个尺寸的图标
        images = []
        sizes = [16, 32, 48, 64, 128, 256]
        
        for size in sizes:
            pixmap = create_matrix_icon_pixmap(size)
            # 转换为 PIL Image
            qimage = pixmap.toImage()
            width = qimage.width()
            height = qimage.height()
            ptr = qimage.bits()
            ptr.setsize(qimage.byteCount())
            arr = bytes(ptr)
            pil_image = Image.frombuffer('RGBA', (width, height), arr, 'raw', 'BGRA', 0, 1)
            images.append(pil_image)
        
        # 保存为 ICO 文件
        images[0].save(str(output_path), format='ICO', sizes=[(s, s) for s in sizes])
        print(f"✓ 已生成 ICO 图标: {output_path}")
        return True
    except ImportError:
        # 如果没有 PIL，保存为 PNG
        print("警告: 未安装 Pillow，将生成 PNG 文件")
        print("安装 Pillow: pip install Pillow")
        png_path = output_path.with_suffix('.png')
        largest_pixmap = create_matrix_icon_pixmap(256)
        largest_pixmap.save(str(png_path), 'PNG')
        print(f"已生成 PNG 图标: {png_path}")
        print("提示: 可以使用在线工具将 PNG 转换为 ICO 文件")
        return False
    except Exception as e:
        print(f"保存图标失败: {e}")
        return False


def create_icns_file(output_path):
    """创建 macOS .icns 文件"""
    try:
        # macOS 可以使用 PNG，PyInstaller 会自动处理
        # 或者生成 iconset 然后使用 iconutil
        png_path = output_path.with_suffix('.png')
        
        # 生成高分辨率 PNG（1024x1024）
        largest_pixmap = create_matrix_icon_pixmap(1024)
        largest_pixmap.save(str(png_path), 'PNG')
        print(f"✓ 已生成 PNG 图标: {png_path}")
        print("提示: PyInstaller 可以使用 PNG 图标，或使用 iconutil 转换为 .icns")
        
        # 尝试使用 iconutil 生成 .icns（如果可用）
        import subprocess
        import shutil
        
        if shutil.which('iconutil'):
            iconset_dir = output_path.parent / 'app_icon.iconset'
            iconset_dir.mkdir(exist_ok=True)
            
            # 生成不同尺寸的图标
            sizes = {
                'icon_16x16.png': 16,
                'icon_16x16@2x.png': 32,
                'icon_32x32.png': 32,
                'icon_32x32@2x.png': 64,
                'icon_128x128.png': 128,
                'icon_128x128@2x.png': 256,
                'icon_256x256.png': 256,
                'icon_256x256@2x.png': 512,
                'icon_512x512.png': 512,
                'icon_512x512@2x.png': 1024,
            }
            
            for filename, size in sizes.items():
                pixmap = create_matrix_icon_pixmap(size)
                pixmap.save(str(iconset_dir / filename), 'PNG')
            
            # 使用 iconutil 转换为 .icns
            try:
                subprocess.run(['iconutil', '-c', 'icns', str(iconset_dir), '-o', str(output_path)], 
                             check=True, capture_output=True)
                print(f"✓ 已生成 ICNS 图标: {output_path}")
                # 清理临时目录
                import shutil
                shutil.rmtree(iconset_dir, ignore_errors=True)
                return True
            except subprocess.CalledProcessError:
                print("iconutil 转换失败，使用 PNG 图标")
                return False
        else:
            return False
    except Exception as e:
        print(f"生成图标失败: {e}")
        return False


def main():
    """主函数"""
    # 创建 QApplication（必需）
    app = QApplication(sys.argv)
    
    script_dir = Path(__file__).parent
    
    if sys.platform == 'win32':
        # Windows: 生成 .ico 文件
        ico_path = script_dir / 'app_icon.ico'
        print("正在生成 Windows 图标...")
        create_ico_file(ico_path)
    elif sys.platform == 'darwin':
        # macOS: 生成 .icns 文件
        icns_path = script_dir / 'app_icon.icns'
        print("正在生成 macOS 图标...")
        create_icns_file(icns_path)
    else:
        # Linux: 生成 PNG 文件
        png_path = script_dir / 'app_icon.png'
        print("正在生成 Linux 图标...")
        pixmap = create_matrix_icon_pixmap(256)
        pixmap.save(str(png_path), 'PNG')
        print(f"已生成 PNG 图标: {png_path}")


if __name__ == '__main__':
    main()

