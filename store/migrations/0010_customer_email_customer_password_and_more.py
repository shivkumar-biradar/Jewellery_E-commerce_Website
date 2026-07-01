
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0009_wishlist'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='email',
            field=models.EmailField(default='', max_length=100, unique=True),
        ),
        migrations.AddField(
            model_name='customer',
            name='password',
            field=models.CharField(default='', max_length=255),
        ),
        migrations.AlterField(
            model_name='customer',
            name='mobile',
            field=models.CharField(max_length=15, unique=True),
        ),
    ]
