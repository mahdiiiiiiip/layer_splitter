# Layer Splitter

Layer Splitter is a small Python utility that separates individual visible
elements from images with transparency. Each detected element is exported as
its own PNG file with a transparent background.

It is useful for preparing transparent artwork, collage assets, illustrations,
and other raster images whose separate elements are already distinguishable
by transparent gaps.

## 1. Requirements

- Python 3.9 or newer
- NumPy
- Pillow
- SciPy

Install the required packages from a terminal:

```bash
python -m pip install -r requirements.txt
```

## 2. Folder structure

Keep the script and folders together:

```text
Layer-Splitter/
├── layer-splitter.py
├── requirements.txt
├── README.md
├── INPUT/
└── OUTPUT/
```

The script creates the `INPUT` and `OUTPUT` folders automatically if they do
not already exist. Put the images you want to process in `INPUT`.

## 3. Supported image formats

The script processes:

- PNG
- WEBP
- TIF
- TIFF

Images are converted to RGBA during processing. The alpha channel is used to
identify visible pixels, so the source images should contain transparency
between separate elements. A fully opaque image will normally be detected as
one large element.

## 4. How to run

1. Install Python if it is not already installed.
2. Open a terminal or command prompt in the project folder.
3. Install dependencies using the command in the Requirements section.
4. Copy your source images into the `INPUT` folder.
5. Run:

   ```bash
   python layer-splitter.py
   ```

6. Open the `OUTPUT` folder to find the exported PNG files.

The script processes every supported image in `INPUT`. Each exported element
is named using the source filename and a three-digit sequence number, for
example `artwork_001.png`, `artwork_002.png`, and `artwork_003.png`.

## 5. Configuration

You can adjust these settings near the top of `layer-splitter.py`:

| Setting | Default | Description |
| --- | ---: | --- |
| `ALPHA_THRESHOLD` | `10` | A pixel is considered visible when its alpha value is greater than this number. Range: 0-254. |
| `MERGE_DISTANCE` | `0` | Expands the detection mask to combine nearby elements. Set to `0` to disable merging. |
| `MIN_AREA` | `20` | Minimum number of visible source pixels required for an element to be exported. Smaller elements are ignored. |
| `PADDING` | `0` | Adds transparent padding around each exported PNG, in pixels. |

### Configuration examples

**Remove faint semi-transparent pixels**

Increase `ALPHA_THRESHOLD`, for example:

```python
ALPHA_THRESHOLD = 30
```

**Join nearby elements**

Set a positive merge distance:

```python
MERGE_DISTANCE = 5
```

A larger value can combine elements that are farther apart. If separate
objects become joined unexpectedly, reduce this value or set it back to `0`.

**Ignore tiny fragments**

Increase the minimum area:

```python
MIN_AREA = 100
```

**Add transparent space around each element**

For a 10-pixel margin:

```python
PADDING = 10
```

## 6. How it works

1. The program opens each supported image and converts it to RGBA.
2. It reads the alpha channel and creates a visibility mask. Pixels whose
   alpha value is above `ALPHA_THRESHOLD` are treated as visible.
3. If `MERGE_DISTANCE` is greater than zero, the mask is expanded using
   morphological dilation. This can connect nearby shapes.
4. Connected-component labeling identifies separate regions. The program
   uses 8-connectivity, so diagonal neighbors are considered connected.
5. Regions with fewer than `MIN_AREA` visible source pixels are ignored.
6. For each remaining region, the program crops its bounding rectangle and
   makes pixels outside that region transparent.
7. Optional transparent padding is added, and the element is saved as a
   numbered PNG in `OUTPUT`.

## 7. Important notes and limitations

- The tool separates elements based on transparency and pixel connectivity.
  It does not recognize objects by their visual meaning.
- If two objects touch or overlap with no transparent gap, they may be
  detected as one element.
- With `MERGE_DISTANCE = 0`, diagonally touching pixels are considered
  connected.
- Increasing `MERGE_DISTANCE` may combine nearby elements. Use it carefully.
- The output is always PNG with an alpha channel, regardless of the input
  format.
- Files with the same base filename but different extensions may produce
  output filenames that overlap. Process such files separately if both need
  to be retained.
- Existing output files with matching names may be overwritten. Move or rename
  previous results before running the tool again if you need to keep them.

## 8. Troubleshooting

**No images are processed**

Make sure your files are inside the `INPUT` folder and use one of the
supported extensions.

**The whole image is exported as one element**

Check that the source image has transparent gaps between the elements.
Opaque backgrounds are treated as visible pixels.

**Small details are missing**

Lower `MIN_AREA` or adjust `ALPHA_THRESHOLD`.

**Nearby objects are combined**

Set `MERGE_DISTANCE = 0` or reduce its value. Also check whether the objects
touch diagonally, since diagonal connections count as connected.

**Too many tiny fragments are exported**

Increase `MIN_AREA` or raise `ALPHA_THRESHOLD` to ignore faint pixels.

## License

No license is specified in this package. Add a license file before
redistributing the project if you want to define permissions and conditions
for reuse.

## Try the Free Online Version

Prefer to use Layer Splitter directly in your browser without installing
Python or setting up a local environment?

Try the free online version:

https://elvoedit.com/layer-splitter/

Use the online tool to split image elements directly in your browser.

If you prefer offline usage, customization, or running the tool locally,
continue with the Python version included in this package