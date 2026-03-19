# Voice element

**Type:** object

Creates a voiceover element by converting the provided text into synthesized speech. The text to be spoken is specified using the `text` property. The `voice` property determines the voice to use, and the `model` property allows specifying which speech synthesis model to employ. Optionally, a `connection` ID can be provided to utilize your own API key for voice generation, otherwise the JSON2Video API keys will be used.

## Working with the Voice element

The Voice element uses AI models to generate a voiceover for your video.

You can choose from the following models:
* **Microsoft Azure** (`azure`): The Azure model is a powerful and flexible option that supports a wide range of voices and languages.
* **ElevenLabs** (`elevenlabs`): Popular choice for its high quality voices.
* **ElevenLabs Flash V2.5** (`elevenlabs-flash-v2-5`): Fast and efficient option.

*Note: The `azure` model is the default model.*

### Voice generation costs

Generating a voiceover with AI is expensive.

| Model | Credits per minute |
|---|---|
| Azure | 0 credits |
| ElevenLabs | 60 credits |
| ElevenLabs Flash V2.5 | 60 credits |

Azure model cost is included in all JSON2Video plans. Voiceovers are **cached** to avoid redundant costs. Use `cache: false` to regenerate.

#### Using your own API key
Create a connection in the [Connections](https://json2video.com/dashboard/connections) page, then provide the `connection` ID in the Voice element.

### Choosing the right voice
* **Azure:** `en-US-EmmaMultilingualNeural`. List: [Azure Voices](https://json2video.com/ai-voices/azure/languages/)
* **ElevenLabs:** Use natural names like `Daniel`, `Serena`, `Antoni`, `Bella`, `Nova`, `Shimmer`. List: [ElevenLabs Voices Library](https://elevenlabs.io/app/voice-library).

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

### comment
A field for adding descriptive notes or internal memos.

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

### connection
The ID of your pre-configured connection to use for voice generation.

| | |
|---|---|
| **Type** | string |
| **Required** | No |

### duration
Defines the duration of the element in seconds. Default is -1.

| | |
|---|---|
| **Type** | number |
| **Required** | No |
| **Default Value** | `-1` |

### extra-time
The amount of time, in seconds, to extend the element's duration.

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

### id
A unique identifier for the element.

| | |
|---|---|
| **Type** | string |
| **Required** | No |
| **Default Value** | `@randomString` |

### model
The generative AI model to use for synthesizing the voice.

| | |
|---|---|
| **Type** | string |
| **Required** | No |
| **Enum Values** | `azure`, `elevenlabs`, `elevenlabs-flash-v2-5` |

### muted
If `true`, the audio track will be muted.

| | |
|---|---|
| **Type** | boolean |
| **Required** | No |
| **Default Value** | `false` |

### start
The element's start time, in seconds.

| | |
|---|---|
| **Type** | number |
| **Required** | No |
| **Default Value** | `0` |

### text
The text content to be synthesized into speech.

| | |
|---|---|
| **Type** | string |
| **Required** | Yes |

### type
Must be set to `voice`.

| | |
|---|---|
| **Type** | string |
| **Required** | Yes |
| **Enum Values** | `voice` |

### variables
Local variables specific to this element.

| | |
|---|---|
| **Type** | object |
| **Required** | No |
| **Default Value** | `{}` |

### voice
The name or ID of the voice to be used.

| | |
|---|---|
| **Type** | string |
| **Required** | No |

### volume
Controls the volume gain of the audio track (range 0-10).

| | |
|---|---|
| **Type** | number |
| **Required** | No |
| **Default Value** | `1` |

### z-index
Determines the stacking order.

| | |
|---|---|
| **Type** | number |
| **Required** | No |
| **Default Value** | `0` |

## Examples

### Example: Voiceover using Azure

```json
{
  "resolution": "full-hd",
  "scenes": [
    {
      "elements": [
        {
          "type": "voice",
          "text": "Hello, world!",
          "voice": "en-US-EmmaMultilingualNeural",
          "model": "azure"
        }
      ]
    }
  ]
}
```

### Example: ElevenLabs with custom connection

```json
{
  "resolution": "full-hd",
  "scenes": [
    {
      "elements": [
        {
          "type": "voice",
          "text": "Hello, world!",
          "model": "elevenlabs",
          "voice": "Daniel",
          "connection": "my-connection-id"
        }
      ]
    }
  ]
}
```
