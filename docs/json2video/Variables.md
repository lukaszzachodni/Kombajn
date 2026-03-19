# Variables

Variables are a powerful feature in JSON2Video that allows you to dynamically inject data into your movie scripts. They act as placeholders for values that can be changed without modifying the core structure of your JSON. This makes your templates more reusable and adaptable to different scenarios.

## Key Benefits of Using Variables

* **Reusability:** Create a single template and use it for multiple videos with varying content.
* **Maintainability:** Update values in one place (the `variables` object) instead of scattered throughout the JSON.
* **Dynamic Content:** Integrate with external data sources (e.g., APIs, databases) to populate your videos with real-time information.

## How Variables Work

Variables are defined in the `variables` object at the root level of your `movie` or `scene` JSON. This object contains key-value pairs, where the key is the variable name and the value is the data you want to inject.

**Steps:**

1. **Define Variables:** Create a `variables` object at the root level of your `movie` or `scene` JSON.
2. **Use Variables:** Reference variables within your JSON using double curly braces: `{{variable_name}}`. These placeholders will be replaced with their corresponding values during the rendering process.

**Example:**

```json
{
  "resolution": "full-hd",
  "variables": {
    "title": "Summer Sale!",
    "discount_percentage": 20,
    "background_color": "#f0f0f0"
  },
  "scenes": [
    {
      "background-color": "{{background_color}}",
      "elements": [
        {
          "type": "text",
          "text": "{{title}}",
          "style": "001"
        },
        {
          "type": "text",
          "text": "Save {{discount_percentage}}%!",
          "style": "002",
          "start": 3
        }
      ]
    }
  ]
}
```

### Data Types
Variables can hold the following data types:
* `string`, `number`, `boolean`, `array`, `object`

### Scope
* **Movie-Level Variables:** Defined at the root of the `movie` object. Accessible throughout the entire movie.
* **Scene-Level Variables:** Defined within a `scene` object. Accessible only within that specific scene. Scene-level variables override movie-level variables.

### Variable Naming Conventions
* Start with a letter (a-z, A-Z).
* Can contain letters, numbers (0-9), and underscores (_).
* Spaces and special characters are not allowed.

## Example of Overriding Movie-Level Variables with Scene-Level Variables

```json
{
    "variables": {
        "font_color": "#FFFFFF"
    },
    "scenes":[
        {
            "variables": {
                "font_color": "#000000"
            },
            "elements":[
                {
                    "type": "text",
                    "text": "Scene 1",
                    "settings": {
                        "color": "{{font_color}}"
                    }
                }
            ]
        },
         {
            "elements":[
                {
                    "type": "text",
                    "text": "Scene 2",
                    "settings": {
                        "color": "{{font_color}}"
                    }
                }
            ]
        }
    ]
}
```

## Important Considerations
* **Security:** Avoid storing sensitive information (API keys, passwords) directly in variables.
* **Data Validation:** Implement validation on your data sources to ensure variable values are compatible with the expected data types.
* **Performance:** Excessive use of variables and complex expressions may impact rendering performance.
