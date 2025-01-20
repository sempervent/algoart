import noise
import numpy as np
from PIL import Image, ImageDraw
import random
import colorsys


# Parameter Class
class ParameterSet:
    def __init__(self, **kwargs):
        self.params = kwargs

    def update(self, **kwargs):
        self.params.update(kwargs)

    def get(self, key, default=None):
        return self.params.get(key, default)


# Landscape Generator Class
class LandscapeGenerator:
    def __init__(self, parameters: ParameterSet):
        self.params = parameters

    def generate(self):
        size = self.params.get("size", 512)
        scale = self.params.get("scale", 100.0)
        heightmap = np.zeros((size, size))
        for i in range(size):
            for j in range(size):
                heightmap[i][j] = noise.pnoise2(
                    i / scale,
                    j / scale,
                    octaves=self.params.get("octaves", 6),
                    persistence=self.params.get("persistence", 0.5),
                    lacunarity=self.params.get("lacunarity", 2.0),
                    repeatx=size,
                    repeaty=size,
                    base=self.params.get("base", 0),
                )
        return (heightmap - heightmap.min()) / (heightmap.max() - heightmap.min())  # Normalize


# Color Palette Generator
class ColorPalette:
    def __init__(self, palette_type="random", custom_colors=None):
        self.palette_type = palette_type
        self.custom_colors = custom_colors or []

    def generate(self, num_colors=10):
        if self.palette_type == "random":
            return [self.random_color() for _ in range(num_colors)]
        elif self.palette_type == "gradient":
            return self.gradient_colors()
        elif self.palette_type == "custom":
            return self.custom_colors
        else:
            raise ValueError("Unknown palette type.")

    @staticmethod
    def random_color():
        return tuple(random.randint(50, 255) for _ in range(3))

    def gradient_colors(self):
        start_color = self.random_color()
        end_color = self.random_color()
        return [
            tuple(
                int(start_color[i] + (end_color[i] - start_color[i]) * t)
                for i in range(3)
            )
            for t in np.linspace(0, 1, 10)
        ]


# Overlay Artist Class
class OverlayArtist:
    def __init__(self, parameters: ParameterSet, color_palette: ColorPalette):
        self.params = parameters
        self.palette = color_palette

    def apply_overlay(self, heightmap):
        image = Image.fromarray((heightmap * 255).astype("uint8")).convert("RGB")
        draw = ImageDraw.Draw(image)

        overlay_type = self.params.get("overlay_type", "particles")
        if overlay_type == "particles":
            image = self.particle_overlay(image, draw)
        elif overlay_type == "fractal":
            image = self.fractal_overlay(image, draw)
        elif overlay_type == "cellular":
            image = self.cellular_automata(image)
        else:
            raise ValueError("Unknown overlay type.")
        return image

    def particle_overlay(self, image, draw):
        for _ in range(self.params.get("num_particles", 500)):
            x, y = random.randint(0, image.size[0]), random.randint(0, image.size[1])
            color = random.choice(self.palette.generate())
            radius = random.randint(1, 5)
            draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color)
        return image

    def fractal_overlay(self, image, draw):
        size = image.size[0]
        for x in range(size):
            for y in range(size):
                if random.random() < 0.001:
                    color = random.choice(self.palette.generate())
                    draw.point((x, y), fill=color)
        return image

    def cellular_automata(self, image):
        # Simple cellular automata for abstract art
        pixels = np.array(image)
        for _ in range(self.params.get("iterations", 100)):
            x, y = random.randint(0, pixels.shape[0] - 1), random.randint(0, pixels.shape[1] - 1)
            neighbors = pixels[max(0, x - 1): x + 2, max(0, y - 1): y + 2]
            pixels[x, y] = neighbors.mean(axis=(0, 1)) + random.randint(-10, 10)
        return Image.fromarray(pixels.astype("uint8"))


# Art Project Class
class ArtProject:
    def __init__(self, landscape_params: ParameterSet, overlay_params: ParameterSet, palette: ColorPalette):
        self.landscape_gen = LandscapeGenerator(landscape_params)
        self.overlay_artist = OverlayArtist(overlay_params, palette)

    def create(self):
        heightmap = self.landscape_gen.generate()
        final_image = self.overlay_artist.apply_overlay(heightmap)
        return final_image


# Example Usage
if __name__ == "__main__":
    # Define parameters
    landscape_params = ParameterSet(size=512, scale=200.0, octaves=6, persistence=0.5, lacunarity=2.0)
    overlay_params = ParameterSet(overlay_type="particles", num_particles=1000)
    palette = ColorPalette(palette_type="gradient")

    # Create project
    project = ArtProject(landscape_params, overlay_params, palette)
    art = project.create()
    art.show()
