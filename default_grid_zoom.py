# GoogleMapDownloader.py
#A script which when given a longitude, latitude and zoom level downloads a high resolution google map

import urllib.request
from PIL import Image
import os
import math
import pylab as plt


class GoogleMapsLayers:
    ROADMAP = "v"
    TERRAIN = "p"
    ALTERED_ROADMAP = "r"
    SATELLITE = "s"
    TERRAIN_ONLY = "t"
    HYBRID = "y"

class GoogleMapDownloader:
    """
        A class which generates high resolution Google Maps images given
        a longitude, latitude and zoom level
    """

    def __init__(self, lat, lng, zoom=12, layer=GoogleMapsLayers.ROADMAP):
        """
            GoogleMapDownloader Constructor
            Args:
                lat:    The latitude of the location required
                lng:    The longitude of the location required
                zoom:   The zoom level of the location required, ranges from 0 to 23
                        defaults to 12
        """
        self._lat = lat
        self._lng = lng
        self._zoom = zoom
        self._layer = layer

    def getXY(self):
        """
            Generates an X,Y tile coordinate based on the latitude, longitude
            and zoom level
            Returns: An X,Y tile coordinate
        """

        tile_size = 256

        # Use a left shift to get the power of 2
        # i.e. a zoom level of 2 will have 2^2 = 4 tiles
        numTiles = 1 << self._zoom

        # Find the x_point given the longitude
        point_x = (tile_size / 2 + self._lng * tile_size / 360.0) * numTiles // tile_size

        # Convert the latitude to radians and take the sine
        sin_y = math.sin(self._lat * (math.pi / 180.0))

        # Calculate the y coordinate
        point_y = ((tile_size / 2) + 0.5 * math.log((1 + sin_y) / (1 - sin_y)) * -(
                tile_size / (2 * math.pi))) * numTiles // tile_size

        return int(point_x), int(point_y)

    def generateImage(self, **kwargs):
        start_x = kwargs.get('start_x', None)
        start_y = kwargs.get('start_y', None)
        tile_width = kwargs.get('tile_width', 5)
        tile_height = kwargs.get('tile_height', 5)

        # Check that we have x and y tile coordinates
        if start_x is None or start_y is None:
            start_x, start_y = self.getXY()

        # Determine the size of the image
        width, height = 256 * tile_width, 256 * tile_height

        # Create a new image of the size require
        map_img = Image.new('RGB', (width, height))

        for x in range(0, tile_width):
            for y in range(0, tile_height):
                url = f'https://mt0.google.com/vt?lyrs={self._layer}&x=' + str(start_x + x) + '&y=' + str(
                    start_y + y) + '&z=' + str(
                    self._zoom)

                current_tile = str(x) + '-' + str(y)
                urllib.request.urlretrieve(url, current_tile)

                im = Image.open(current_tile)
                map_img.paste(im, (x * 256, y * 256))

                os.remove(current_tile)

        return map_img


def main():
    # Create a new instance of GoogleMap Downloader
    gmd = GoogleMapDownloader(40.047183074030954, -83.12888658878242, 13, GoogleMapsLayers.SATELLITE)

    print("The tile coordinates are {}".format(gmd.getXY()))

    try:
        # Get the high resolution image
        img = gmd.generateImage()
    except IOError:
        print("Unable to generate the image, try adjusting the zoom level and checking your coordinates")
    else:
        # Save the image to disk
        img.save("high_resolution_image.png")
        img = plt.imread("high_resolution_image.png")

        # Grid lines at these intervals (in pixels)
        # dx and dy can be different
        dx, dy = 100, 100

        # Custom (rgb) grid color
        grid_color = [0, 0, 0]

        # Modify the image to include the grid
        img[:, ::dy, :] = grid_color
        img[::dx, :, :] = grid_color

        image = Image.open('high_resolution_image.png')
        # the coordinates for the cropped picture go below
        box = (left, upper, right, lower)
        cropped_image = image.crop(box)
        cropped_image.save('cropped_image.jpg')

        # Print size of cropped image
        print(cropped_image.size)

        # Show the result
        plt.imshow(img)
        plt.show()
        print("Image printed.")


if __name__ == '__main__':  main()
