from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from encrypted_model_fields.fields import EncryptedCharField

class EncryptedEmailField(EncryptedCharField):
    description = "An encrypted email field"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validators.append(validate_email)

    def to_python(self, value):
        value = super().to_python(value)
        if value is not None:
            try:
                validate_email(value)
            except ValidationError:
                raise ValidationError("Invalid email format.")
        return value
