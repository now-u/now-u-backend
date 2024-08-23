from unfold.admin import FieldsetsType

def split_release_info(fieldsets: FieldsetsType) -> FieldsetsType:
    current_field: list[str] = fieldsets[0][1]['fields']

    release_fields = ('release_at', 'end_at')
    for field in release_fields:
        current_field.remove(field)

    return [
        (
            None,
            {
                'fields': current_field,
            }
        ),
        (
            'Release Info',
            {
                'fields': release_fields,
            }
        ),
    ]
