# Schema Export Script

This script (`export_schemas.py`) exports all relevant Pydantic models as JSON Schema files for use in validation, documentation, and interoperability.

## Why export JSON Schemas?

- **Validation:** Use JSON Schema to validate config files, API payloads, or event data at boundaries (e.g., with `jsonschema` or external tools).
- **Documentation:** Share schemas with other teams, generate OpenAPI docs, or provide schema contracts for integration partners.
- **Consistency:** Ensures all config and data models are kept in sync between Python code and schema files.

## How does it work?

- The script imports all Pydantic models you care about (config sections, API schemas, etc.).
- It calls `.model_json_schema()` on each model to generate a standards-compliant JSON Schema.
- It writes each schema to `schemas/validation/{model_name}.schema.json`.

## Usage

1. **Edit or add Pydantic models** in `models/config.py` or `models/schemas.py`.
2. **Run the export script:**

python scripts/export_schemas.py

3. **Commit the updated files** in `schemas/validation/` to version control.

## Example Output

After running the script, you'll have files like:
schemas/validation/app_config.schema.json
schemas/validation/routers_config.schema.json
schemas/validation/kafka_config.schema.json
schemas/validation/user.schema.json
…


## Best Practices

- **Never hand-edit JSON Schema files.**  
  Always edit the Pydantic model and rerun the script.
- **Automate this process** in CI (see below) to prevent schema drift.
- **Add new models** to the `EXPORTS` dictionary as your project grows.

## CI Integration

Add a step to your CI pipeline to run this script and check for changes:

	•	name: Export schemas run: python scripts/export_schemas.py
	•	name: Check for schema drift run: git diff –exit-code schemas/validation/

If there are uncommitted changes, the CI will fail, alerting you to update and commit your schemas.

## Dependencies

- Python 3.8+
- [pydantic] (v2+ recommended)

## See Also

- [Pydantic JSON Schema documentation](https://docs.pydantic.dev/latest/concepts/json_schema/)
- [JSON Schema official site](https://json-schema.org/)

---

**Keep your code and schemas in sync for a robust, maintainable, and interoperable platform!**
