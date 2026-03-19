# Video element

**Type:** object

Defines a video element that allows you to incorporate video content into your scenes or movie. Specify the video source using a URL pointing to a video file (MP4, MKV, MOV, etc.). Control playback behavior by defining the number of times the video loops and the starting point within the video using the seek property.

## Required Properties
* `type`

## Properties

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
Defines the duration of the element in seconds. The default value is -1 (automatically calculated).

| | |
|---|---|
| **Type** | number |
| **Required** | No |
| **Default Value** | `-1` |

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

### loop
Specifies the number of times the video will play. Setting this value to -1 results in the video looping indefinitely.

| | |
|---|---|
| **Type** | integer |
| **Required** | No |
| **Minimum Value** | -1 |

### mask
URL to a PNG or video file that defines a mask, controlling the transparency of the element.

| | |
|---|---|
| **Type** | string |
| **Required** | No |

### muted
If `true`, the audio track of the element will be muted.

| | |
|---|---|
| **Type** | boolean |
| **Required** | No |
| **Default Value** | `false` |

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

### seek
Specifies the time, in seconds, at which the video file should start playing.

| | |
|---|---|
| **Type** | number |
| **Required** | No |
| **Default Value** | `0` |

### src
The URL to the video asset file.

| | |
|---|---|
| **Type** | string |
| **Required** | No |

### start
The element's start time, in seconds.

| | |
|---|---|
| **Type** | number |
| **Required** | No |
| **Default Value** | `0` |

### type
Must be set to `video`.

| | |
|---|---|
| **Type** | string |
| **Required** | Yes |
| **Enum Values** | `video` |

### variables
Local variables specific to this element.

| | |
|---|---|
| **Type** | object |
| **Required** | No |
| **Default Value** | `{}` |

### volume
Controls the volume gain of the audio track.

| | |
|---|---|
| **Type** | number |
| **Required** | No |
| **Default Value** | `1` |
| **Minimum Value** | 0 |
| **Maximum Value** | 10 |

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
| **Minimum Value** | -10 |
| **Maximum Value** | 10 |
