# KOMBAJN AI – Desant: Color Book Generator (TODO)
(Updated: 2026-04-04 14:45:00)

## 📦 1. Migration "Na Pałę"
- [x] Create git branch `feature/colorbook-integration`.
- [x] Copy source files from `color_book_generator` and `colorbook_binding`.
- [x] Merge `requirements.txt`.
- [ ] **Fix Imports**: Ensure internal relative imports work in `backend/app/modules/color_book/`.

## 🚀 2. API Integration
- [ ] **Create Module Router**: `backend/app/api/color_book.py`.
- [ ] **Endpoint "Pomysł"**: Implement POST `/idea` to trigger generator logic.
- [ ] **Endpoint "Binding"**: Implement POST `/bind` to trigger PDF generation.
- [ ] **Global Router**: Register `color_book_router` in `backend/app/main.py`.

## 🛡️ 3. Docker & Runtime
- [ ] **Verify ENV**: Ensure `.env` in `Kombajn/` includes Gemini/Google Cloud keys.
- [ ] **Volumes**: Check if Docker needs access to `color_book/binding/assets` or `data`.
- [ ] **Test Run**: Attempt to trigger generation via cURL from inside container.

## 🎨 4. Front-end (Streamlit)
- [ ] Add simple "Color Book" tab to the main dashboard for quick testing.
