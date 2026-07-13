"""
رجیستری مدل‌های تحت audit.

چرا decorator به‌جای «همه‌چیز خودکار»؟
چون audit-کردن کورکورانه‌ی همه‌ی مدل‌ها (مثلاً Session یا مدل‌های خود audit)
هم نویز اضافه می‌کنه هم ریسک recursion داره. با این روش، هر مدلی که واقعاً
باید ردیابی بشه (مالی/ساختمانی) صریحاً با یک خط تصمیم می‌گیره، ولی این
تصمیم توی خود audit app زندگی می‌کنه نه پخش‌شده در ویوها.

استفاده در models.py هر app:

    from apps.audit.registry import audit_model

    @audit_model(building_field='building')
    class Invoice(BaseModel):
        ...

building_field می‌تونه مسیر نقطه‌ای هم باشه، مثلاً 'unit__building'.
"""

_registry = {}  # {model_cls: building_field or None}


def audit_model(building_field=None):
    def decorator(model_cls):
        _registry[model_cls] = building_field
        return model_cls
    return decorator


def is_audited(model_cls):
    return model_cls in _registry


def get_building_field(model_cls):
    return _registry.get(model_cls)


def registered_models():
    return list(_registry.keys())
