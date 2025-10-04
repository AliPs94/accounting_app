"""
Management command to set up production environment
This creates a default superuser if none exists
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import IntegrityError
import os


class Command(BaseCommand):
    help = 'Set up production environment with default superuser'

    def handle(self, *args, **options):
        self.stdout.write('Setting up production environment...')
        
        # Create default superuser if it doesn't exist
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123')
        
        try:
            if not User.objects.filter(username=username).exists():
                User.objects.create_superuser(
                    username=username,
                    email=email,
                    password=password
                )
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Superuser "{username}" created successfully!')
                )
                self.stdout.write(
                    self.style.WARNING(f'  Username: {username}')
                )
                self.stdout.write(
                    self.style.WARNING(f'  Password: {password}')
                )
                self.stdout.write(
                    self.style.WARNING('  Please change this password after first login!')
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Superuser "{username}" already exists')
                )
        except IntegrityError as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Error creating superuser: {e}')
            )
        
        self.stdout.write(self.style.SUCCESS('✓ Production setup complete!'))

