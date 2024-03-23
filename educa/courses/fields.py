from typing import Any
from django.db import models
from django.core.exceptions import ObjectDoesNotExist


class OrderField(models.PositiveIntegerField):
    def __init__(self, *args: Any, for_fields: list[str] = None, **kwargs: Any) -> None:
        self.for_fields: list[str] = for_fields
        super().__init__(*args, **kwargs)

    def pre_save(self, model_instance: models.Model, add: bool) -> Any:
        if getattr(model_instance, self.attname) is None:
            try:
                qs = self.model.objects.all()
                if self.for_fields:
                    query = {field: getattr(model_instance, field) for field in self.for_fields}
                    qs = qs.filter(**query)

                # Get the order of the last item
                last_item = qs.latest(self.attname)
                value = getattr(last_item, self.attname) + 1

            except ObjectDoesNotExist:
                value = 0

            setattr(model_instance, self.attname, value)
            return value

        return super().pre_save(model_instance, add)
