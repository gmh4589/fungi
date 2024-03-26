1. Open the file in which you want to find a texture or RAW image. For example, let's select the file example1.dat, stored in the example folder in the root of the program
![Screenshot_1](https://github.com/gmh4589/fungi/assets/41452060/5b09eb42-0838-4fe6-829a-21c1a4429190)

2. If the image cannot be recognized automatically, you will see the message “Not enough bytes to image creating!”. This means that you must select the image settings manually.
![Screenshot_2](https://github.com/gmh4589/fungi/assets/41452060/15c24468-a487-4686-b5a2-b9f12d3e7bf5)

3. First, you need to try to find the length and width. You can roughly understand the length and width from the file size, and thanks to the message from the previous paragraph, we can understand that the image is most likely smaller than the default 512x512. We are trying to set the size to 256x256.
Nothing much has changed, but in the process of entering the length and width parameters, you will notice that the contents of the file displayed on the screen do not look much like images, it is just a set of multi-colored ripples. If the codec matched the default RGBA, or was close to it, we would see a distorted image in which the outlines of what we were looking for would be guessed. In this case, we can assume that the codec is very different from RGBA and the like (RGB, BGR, ARGB, and so on). We are trying to set DirectX in the “Bits per pixel” section.
![Screenshot_3](https://github.com/gmh4589/fungi/assets/41452060/a0550afc-f3e9-4915-bc5f-6bcc32b08081)

4. Now something has appeared. On the screen, among the stripes and squares, a distorted image of a mushroom can be discerned, which means we are close to the goal. What else can you notice? At the very beginning of the image, you can see a black stripe. This means that in addition to the image itself, there is some other data at the beginning of the file, most likely these are image parameters. Let's try to open it in a HEX editor.
![Screenshot_4](https://github.com/gmh4589/fungi/assets/41452060/4210e35d-0d9a-48d0-ba32-32b695d8baad)

5. You can notice that from byte 0x70, something similar to a description of pixels begins, and above it, we see mostly zeros. Most likely, 0x70 is the beginning of the image data. Enter this value in the “HEX offset” field.
![Screenshot_5](https://github.com/gmh4589/fungi/assets/41452060/6e2d3ad1-f698-4f34-ab9d-7cbb71d06678)

6. The black stripe is gone! Let's now try to select a codec.
![Screenshot_6](https://github.com/gmh4589/fungi/assets/41452060/70849778-b6b7-4b51-9de1-f7a699da81da)

7. By simple search, we can understand that the codec we are looking for is BC3_UNORM.
![Screenshot_7](https://github.com/gmh4589/fungi/assets/41452060/f9fd328e-bf0d-4f25-90ad-c312f7f7d655)

8. Now, you can click on the “SAVE” button and save the image in a format convenient for you.

Now try to determine the file format example2.dat and example3.dat yourself
Hint: You will also need to use the “Convert” option to search for the image in example2.dat so that the image you are looking for is not upside down.
The output should be this image:
![craiyon_164519_fantastic_forest_with_giant_fungus](https://github.com/gmh4589/fungi/assets/41452060/1c77ad12-c1a6-4869-9d85-3e8ab8cbac30)

In order to get an image from the example3.dat file, you will already need to determine the data compression method. To do this, you need to start entering the name of the compression algorithms in the “ZIP method” field. Since it is almost impossible to understand which of the almost 1000 algorithms a file was compressed without some information about the compression method, I will tell you that this file is compressed using a method whose name begins with the Latin P.
In the third example, the compressed file is a regular BMP file, therefore, as soon as the compression method is correctly determined, the program itself will receive all other parameters from the desired image.
