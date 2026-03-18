# Development & Testing Standards

- **Single Source of Truth**: All J2V manifest tests must use the same JSON schema as the Streamlit frontend.
- **Test-First Consistency**: 
    - Every new feature or fix must be accompanied by a JSON manifest file in `backend/app/tests/manifests/`.
    - The Streamlit frontend "Demo" must load this exact same manifest file to ensure parity between backend unit tests and frontend functional tests.
- **Automated Validation**: Use `J2VMovie(**manifest_data)` within tests to guarantee schema compliance before rendering.
- **Reporting**: If a render fails, the test must log the full JSON manifest used for reproduction.
