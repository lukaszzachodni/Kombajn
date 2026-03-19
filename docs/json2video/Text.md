# Text element

**Type:** object

Defines a text element that allows you to overlay a text on top of your video. Depending on the style selected, the text can include different text animations like word-by-word, character-by-character, or jumping letters.

### Related links
* [Text Styles](https://json2video.com/docs/resources/text/)

## Customizing the Text element

The **Text element** can be customized to include a variety of text styles, fonts, and colors. You must use the `settings` object to customize the text element.

Example:

```json
{
  "type": "text",
  "text": "Hello, world!",
  "settings": {
    "font-family": "Roboto",
    "font-size": "48px",
    "font-weight": "700",
    "font-color": "#000000",
    "background-color": "#FFFFFF",
    "text-align": "center"
  }
}
```

Most of the CSS properties are supported in the `settings` object.

## Available font families

### Google Fonts

You can use any [Google Font](https://fonts.google.com/) in the `font-family` property just by providing the font name.

Examples:
* `Roboto`, `Lato`, `Montserrat`, `Open Sans`, `Poppins`, `Raleway`

In some cases, Google Fonts don't use the same font name as the one used in the `font-family` property. This is the case for some of the Noto fonts that support different languages.

Common Noto font families:
* `Noto Sans`, `Noto Serif`, `Noto Sans JP`, `Noto Sans SC`, `Noto Sans TC`, `Noto Sans KR`, `Noto Sans Thai`, `Noto Sans Hebrew`, `Noto Sans Arabic`

### Custom fonts

You can use any custom font in the `font-family` property by providing a URL to the font file. TrueType fonts (.ttf) and OpenType fonts (.otf) are supported.

```json
{
  "type": "text",
  "text": "Hello, world!",
  "settings": {
   "font-family": "https://example.com/fonts/custom-font.ttf"
  }
}
```

> **NOTE:** Be aware that the custom fonts in the `subtitles` element use the `font-url` property instead of the `font-family` property.

## Positioning the Text element

The **Text element** is structured to provide flexibility in positioning text within your video. It consists of two main concepts:

1. **Text Element Canvas Area**:
    * This is the outer area that can occupy the full size of the video canvas. It serves as the boundary within which the text box is placed. The canvas can be adjusted to fit the full video size or a custom size.
2. **Textbox Inside the Canvas**:
    * Within the text element canvas, there is a textbox that can be aligned both vertically and horizontally. This alignment feature ensures that regardless of the text length, the textbox can be positioned accurately within the canvas.

To position the textbox inside the canvas, you must use the `vertical-position` (`top`, `center`, `bottom`) and `horizontal-position` (`left`, `center`, `right`) properties in the `settings` object.

## Properties

The following properties are required:
* `text`
* `type`

### cache
If `true`, the system will attempt to retrieve and use a previously rendered (cached) version of this element. The default value is `true`.

| | |
|---|---|
| **Type** | boolean |
| **Required** | No |
| **Default Value** | `true` |

### chroma-key
Allows you to define a color or a range of colors within the element that will be rendered as transparent.

| | |
|---|---|
| **Type** | object |
| **Required** | No |

### comment
A field for adding descriptive notes or internal memos related to the element.

| | |
|---|---|
| **Type** | string |
| **Required** | No |

### condition
An expression that determines whether the element will be rendered.

| | |
|---|---|
| **Type** | string |
| **Required** | No |

### correction
Defines image and video correction settings (contrast, brightness, saturation, gamma).

| | |
|---|---|
| **Type** | object |
| **Required** | No |

### crop
Defines the cropping area of the element.

| | |
|---|---|
| **Type** | object |
| **Required** | No |

### duration
Defines the duration of the text element in seconds. The default value is -2 (matches container).

| | |
|---|---|
| **Type** | number |
| **Required** | No |
| **Default Value** | `-2` |

### extra-time
The amount of time, in seconds, to extend the element's duration beyond its natural length.

| | |
|---|---|
| **Type** | number |
| **Required** | No |
| **Default Value** | `0` |

### fade-in / fade-out
The duration, in seconds, of the fade effect.

| | |
|---|---|
| **Type** | number |
| **Required** | No |
| **Minimum Value** | 0 |

### flip-horizontal / flip-vertical
If `true`, flips the element. Default is `false`.

| | |
|---|---|
| **Type** | boolean |
| **Required** | No |
| **Default Value** | `false` |

### height / width
Sets the height/width of the element in pixels. The default is -1 (original aspect ratio).

| | |
|---|---|
| **Type** | integer |
| **Required** | No |
| **Default Value** | `-1` |

### id
A unique identifier for the element.

| | |
|---|---|
| **Type** | string |
| **Required** | No |
| **Default Value** | `@randomString` |

### mask
URL to a PNG or video file that defines a mask, controlling the transparency of the element.

| | |
|---|---|
| **Type** | string |
| **Required** | No |

### pan / pan-crop / pan-distance
Configures panning effect.

| | |
|---|---|
| **Type** | string/boolean/number |
| **Required** | No |

### position
Specifies the position of the element within the movie canvas.

| | |
|---|---|
| **Type** | string |
| **Required** | No |
| **Default Value** | `custom` |

### resize
Defines how the element should be resized to fit within the movie canvas.

| | |
|---|---|
| **Type** | string |
| **Required** | No |

### rotate
Defines rotation properties (angle, speed).

| | |
|---|---|
| **Type** | object |
| **Required** | No |

### settings
Text formatting settings (CSS properties).

| | |
|---|---|
| **Type** | object |
| **Required** | No |
| **Default Value** | `{}` |

### start
The element's start time, in seconds.

| | |
|---|---|
| **Type** | number |
| **Required** | No |
| **Default Value** | `0` |

### style
The style of the text element. Default is "001".

| | |
|---|---|
| **Type** | string |
| **Required** | No |
| **Default Value** | `001` |

### text
The text content to be displayed.

| | |
|---|---|
| **Type** | string |
| **Required** | Yes |

### type
Must be set to `text`.

| | |
|---|---|
| **Type** | string |
| **Required** | Yes |
| **Enum Values** | `text` |

### variables
Local variables specific to this element.

| | |
|---|---|
| **Type** | object |
| **Required** | No |
| **Default Value** | `{}` |

### z-index
Determines the stacking order.

| | |
|---|---|
| **Type** | number |
| **Required** | No |
| **Default Value** | `0` |

### zoom
Zooms the element.

| | |
|---|---|
| **Type** | integer |
| **Required** | No |
