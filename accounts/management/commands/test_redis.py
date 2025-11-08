"""
Create this file: accounts/management/commands/test_redis.py
"""

from django.core.management.base import BaseCommand
from django.core.cache import cache


class Command(BaseCommand):
    help = 'Test Redis connection and caching'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Testing Redis connection...'))
        
        try:
            # Test basic set/get
            cache.set('test_key', 'Hello Redis!', 30)
            value = cache.get('test_key')
            
            if value == 'Hello Redis!':
                self.stdout.write(self.style.SUCCESS('✅ Redis is working!'))
                self.stdout.write(f'   Retrieved value: {value}')
            else:
                self.stdout.write(self.style.ERROR('❌ Redis returned wrong value'))
            
            # Test deletion
            cache.delete('test_key')
            value = cache.get('test_key')
            
            if value is None:
                self.stdout.write(self.style.SUCCESS('✅ Cache deletion works!'))
            else:
                self.stdout.write(self.style.ERROR('❌ Cache deletion failed'))
            
            # Test multiple keys
            cache.set('key1', 'value1', 30)
            cache.set('key2', 'value2', 30)
            cache.set('key3', 'value3', 30)
            
            self.stdout.write(self.style.SUCCESS('✅ Multiple keys stored successfully'))
            
            # Clean up
            cache.delete('key1')
            cache.delete('key2')
            cache.delete('key3')
            
            self.stdout.write(self.style.SUCCESS('\n🎉 All Redis tests passed!'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Redis error: {str(e)}'))
            self.stdout.write(self.style.WARNING('\nMake sure Redis is running:'))
            self.stdout.write('   redis-cli ping')