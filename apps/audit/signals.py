import decimal
import datetime

from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver

from .registry import is_audited, get_building_field
from .threadlocal import get_current_user

# فیلدهایی که هیچ‌وقت نباید توی AuditLog چاپ بشن (حساس/بی‌فایده)
EXCLUDED_FIELDS = {'password', 'updated_at'}


def _serialize(value):
    if isinstance(value, decimal.Decimal):
        return str(value)
    if isinstance(value, (datetime.date, datetime.datetime)):
        return value.isoformat()
    return value


def _field_values(instance):
    """مقادیر همه‌ی فیلدهای concrete (نه reverse/m2m) رو به شکل قابل-JSON برمی‌گردونه."""
    values = {}
    for field in instance._meta.concrete_fields:
        if field.name in EXCLUDED_FIELDS:
            continue
        raw = field.value_from_object(instance)
        if field.get_internal_type() in ('FileField', 'ImageField'):
            # FieldFile: فایل واقعی رو ذخیره نمی‌کنیم، فقط مسیرش رو (.name هیچ‌وقت exception نمی‌ده)
            values[field.name] = raw.name or None
        else:
            values[field.name] = _serialize(raw)
    return values


def _resolve_building(instance):
    path = get_building_field(instance.__class__)
    if not path:
        return None
    if path == 'self':
        return instance
    obj = instance
    try:
        for part in path.split('__'):
            obj = getattr(obj, part)
            if obj is None:
                return None
        return obj
    except Exception:
        return None


@receiver(pre_save)
def _stash_old_values(sender, instance, **kwargs):
    if not is_audited(sender):
        return
    if not instance.pk:
        instance._audit_old_values = None
        return
    manager = getattr(sender, 'all_objects', sender.objects)
    try:
        old = manager.get(pk=instance.pk)
    except sender.DoesNotExist:
        old = None
    instance._audit_old_values = _field_values(old) if old else None


@receiver(post_save)
def _log_save(sender, instance, created, **kwargs):
    if not is_audited(sender):
        return

    new_values = _field_values(instance)
    old_values = getattr(instance, '_audit_old_values', None)

    if created or old_values is None:
        action = _get_audit_log_model().Action.CREATE
        changes = {field: [None, value] for field, value in new_values.items()}
    else:
        diff = {
            field: [old_values.get(field), value]
            for field, value in new_values.items()
            if old_values.get(field) != value
        }
        if not diff:
            return  # save بدون تغییر واقعی (مثلاً فقط updated_at) — لاگ نکن
        action = _get_audit_log_model().Action.UPDATE
        changes = diff

    _create_log(instance, action, changes)


@receiver(post_delete)
def _log_delete(sender, instance, **kwargs):
    if not is_audited(sender):
        return
    _create_log(instance, _get_audit_log_model().Action.DELETE, _field_values(instance))


def _get_audit_log_model():
    from .models import AuditLog
    return AuditLog


def _create_log(instance, action, changes):
    AuditLog = _get_audit_log_model()
    AuditLog.objects.create(
        actor=get_current_user(),
        action=action,
        content_type=ContentType.objects.get_for_model(instance.__class__),
        object_id=str(instance.pk),
        object_repr=str(instance)[:255],
        building=_resolve_building(instance),
        changes=changes,
    )
