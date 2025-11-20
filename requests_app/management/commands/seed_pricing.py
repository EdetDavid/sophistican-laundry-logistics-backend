from django.core.management.base import BaseCommand
from requests_app.models import PricingItem


DEFAULT_PRICING = [
    { 'slug': 'shirt_ironing', 'label': 'Shirt Ironing', 'price': 3.50, 'description': 'Professional ironing for single shirt', 'icon': '👔' },
    { 'slug': 'trousers_ironing', 'label': 'Trousers Ironing', 'price': 2.50, 'description': 'Professional ironing for single pair of trousers', 'icon': '👖' },
    { 'slug': 'full_ironing', 'label': 'Full Ironing Service', 'price': 15.00, 'description': 'Complete ironing service for entire laundry load', 'icon': '✨' },
    { 'slug': 'suits', 'label': 'Suit Cleaning & Pressing', 'price': 25.00, 'description': 'Professional dry cleaning and pressing for suits', 'icon': '🎩' },
    { 'slug': 'full_home_service', 'label': 'Full Home Service', 'price': 45.00, 'description': 'Complete laundry service including wash, dry, fold & deliver', 'icon': '🏠' },
    { 'slug': 'wash_dry', 'label': 'Wash & Dry', 'price': 8.00, 'description': 'Washing and drying of clothes', 'icon': '🌊' },
    { 'slug': 'hand_wash', 'label': 'Hand Wash', 'price': 12.00, 'description': 'Gentle hand washing for delicate fabrics', 'icon': '✋' },
    { 'slug': 'dry_clean', 'label': 'Dry Clean', 'price': 18.00, 'description': 'Professional dry cleaning service', 'icon': '🧪' },
    { 'slug': 'special_care', 'label': 'Special Care (Delicates)', 'price': 20.00, 'description': 'Extra care for delicate, premium, or special fabrics', 'icon': '💎' },
    { 'slug': 'other', 'label': 'Custom Service', 'price': None, 'description': 'Contact us for custom pricing', 'icon': '🤝' },
]


class Command(BaseCommand):
    help = 'Seed the PricingItem table with default pricing items'

    def handle(self, *args, **options):
        self.stdout.write('Seeding PricingItem table...')
        created = 0
        for idx, item in enumerate(DEFAULT_PRICING):
            obj, was_created = PricingItem.objects.update_or_create(
                slug=item['slug'],
                defaults={
                    'label': item.get('label', ''),
                    'price': item.get('price'),
                    'description': item.get('description', ''),
                    'icon': item.get('icon', ''),
                    'ordering': idx,
                }
            )
            if was_created:
                created += 1

        total = PricingItem.objects.count()
        self.stdout.write(self.style.SUCCESS(f'Seeding complete. {created} new items created. Total pricing items: {total}'))
