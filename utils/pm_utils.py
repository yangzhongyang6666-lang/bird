# utils/pm_utils.py
def to_pygame(p, surface):
    """将 Pymunk 坐标转为 Pygame 坐标"""
    return int(p.x), int(surface.get_height() - p.y)

def to_pymunk(x, y, surface):
    """将 Pygame 坐标转为 Pymunk 坐标"""
    return x, surface.get_height() - y