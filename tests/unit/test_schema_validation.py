from src.ingestion_api.api.routes.schemas import validate_schema
from src.ingestion_api.models.contracts import SchemaValidationRequest, FieldDefinition

def test_schema_validation_valid():
    request = SchemaValidationRequest(
        supplier_code="TEST_1",
        schema_version="1.0.1",
        fields=[
            FieldDefinition(name="temperature_c", type="float", required=True),
            FieldDefinition(name="pressure_psi", type="float", required=True),
            FieldDefinition(name="new_optional_field", type="string", required=False)
        ]
    )
    result = validate_schema(request)
    assert result.is_compatible is True
    assert "new_optional_field" in result.added_fields
    assert len(result.errors) == 0

def test_schema_validation_breaking_remove_required():
    request = SchemaValidationRequest(
        supplier_code="TEST_1",
        schema_version="1.0.1",
        fields=[
            FieldDefinition(name="temperature_c", type="float", required=True),
        ]
    )
    result = validate_schema(request)
    assert result.is_compatible is False
    assert "pressure_psi" in result.removed_fields
    assert any("Removed required field" in e for e in result.errors)

def test_schema_validation_breaking_type_change():
    request = SchemaValidationRequest(
        supplier_code="TEST_1",
        schema_version="1.0.1",
        fields=[
            FieldDefinition(name="temperature_c", type="string", required=True),
            FieldDefinition(name="pressure_psi", type="float", required=True)
        ]
    )
    result = validate_schema(request)
    assert result.is_compatible is False
    assert any("Type changed for temperature_c" in e for e in result.errors)
