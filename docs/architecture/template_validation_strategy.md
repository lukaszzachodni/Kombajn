# Template Validation & Dual-Mode Strategy

Aby obsłużyć zarówno "Konkretne Wartości" (dane dla renderera), jak i "Szablony" (zmienne `{{...}}`), stosujemy podejście hybrydowe w modelach Pydantic.

## Strategia "Hybrid Models"

1. **Typy Hybrydowe (Union[Type, str])**: Pola, które mają obsługiwać zarówno konkretne wartości (np. `int`), jak i zmienne szablony (`str` z tagami `{{...}}`), są definiowane jako `Union`.
2. **Validator Middleware**: Używamy walidatorów (`AfterValidator`), które sprawdzają obecność tagu `{{...}}`. Jeśli tag istnieje, walidacja typu jest pomijana (pole traktowane jest jako poprawne dla szablonu).
3. **UI Factory**: Warstwa prezentacji (Streamlit) dynamicznie przełącza się między standardowymi polami (np. `number_input`) a polami tekstowymi (`text_input`) w zależności od trybu pracy (`Szablon` vs `Konkret`).

Dzięki temu ten sam model Pydantic służy do:
- Walidacji gotowych manifestów przed wysłaniem do renderowania.
- Wygodnego edytowania szablonów w interfejsie użytkownika.
