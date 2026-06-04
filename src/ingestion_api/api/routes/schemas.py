from fastapi import APIRouter
from src.ingestion_api.models.contracts import SchemaValidationRequest, SchemaCompatibilityResult

router = APIRouter()

MASTER_SCHEMA = {
    "temperature_c": {"type": "float", "required": True},
    "pressure_psi": {"type": "float", "required": True},
}

@router.post("/validate", response_model=SchemaCompatibilityResult)
def validate_schema(request: SchemaValidationRequest):
    is_compatible = True
    added_fields = []
    removed_fields = []
    type_changes = []
    warnings = []
    errors = []
    
    proposed_fields = {f.name: f for f in request.fields}
    
    for name, current_field in MASTER_SCHEMA.items():
        if name not in proposed_fields:
            if current_field["required"]:
                is_compatible = False
                errors.append(f"Removed required field: {name}")
            else:
                warnings.append(f"Removed optional field: {name}")
            removed_fields.append(name)
        else:
            proposed_field = proposed_fields[name]
            if proposed_field.type != current_field["type"]:
                is_compatible = False
                errors.append(f"Type changed for {name} from {current_field['type']} to {proposed_field.type}")
                type_changes.append({name: f"{current_field['type']} -> {proposed_field.type}"})
                
    for name, proposed_field in proposed_fields.items():
        if name not in MASTER_SCHEMA:
            added_fields.append(name)
            if proposed_field.required:
                is_compatible = False
                errors.append(f"Added required field without default: {name}")

    return SchemaCompatibilityResult(
        is_compatible=is_compatible,
        added_fields=added_fields,
        removed_fields=removed_fields,
        type_changes=type_changes,
        warnings=warnings,
        errors=errors
    )

@router.get("/master")
def get_master_schema():
    return {"version": "1.0.0", "fields": MASTER_SCHEMA}

@router.post("/approve")
def approve_schema():
    return {"status": "approved"}
