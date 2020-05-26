Connect remarkable with cord, make sure that ~/.config/remt.ini looks good with
the settings/SSH key. Jump into pipenv environment: `pipenv shell`

In bash...
```
remt export "ita" latest_words.pdf
convert -density 500 latest_words.pdf latest_words.jpg
```

in python
```python
from PIL import Image
import pytesseract
t = pytesseract.image_to_string(Image.open("latest_words.jpg"))
```
