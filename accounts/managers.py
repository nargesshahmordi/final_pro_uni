from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    """
    یوزرمنیجر سفارشی چون شماره موبایل جایگزین username شده.
    """
    use_in_migrations = True

    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError('شماره موبایل الزامی است')
        phone_number = phone_number.strip()
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('سوپریوزر باید is_staff=True داشته باشه')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('سوپریوزر باید is_superuser=True داشته باشه')

        return self.create_user(phone_number, password, **extra_fields)
