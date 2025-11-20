from django.core.management.base import BaseCommand
from users.models import Notification
from requests_app.models import LaundryRequest
import re
from django.db import transaction

class Command(BaseCommand):
    help = 'Sanitize Notification bodies: strip HTML and attach related_request when Request #id is found.'

    def handle(self, *args, **options):
        qs = Notification.objects.all()
        total = qs.count()
        self.stdout.write(f'Found {total} notifications to sanitize')
        updated = 0
        for n in qs:
            changed = False
            body = n.body or ''
            # Strip HTML tags
            if '<' in body and '>' in body:
                plain = re.sub('<[^<]+?>', '', body)
                plain = plain.strip()
                if plain != body:
                    n.body = plain
                    changed = True
            else:
                plain = body
            # Try to find "Request #123" patterns
            m = re.search(r'Request\s*#(\d+)', plain)
            if m and not n.related_request_id:
                rq_id = int(m.group(1))
                try:
                    rq = LaundryRequest.objects.filter(id=rq_id).first()
                    if rq:
                        n.related_request = rq
                        changed = True
                except Exception:
                    pass
            if changed:
                try:
                    with transaction.atomic():
                        n.save()
                        updated += 1
                except Exception as e:
                    self.stderr.write(f'Failed to save notification {n.id}: {e}')
        self.stdout.write(self.style.SUCCESS(f'Sanitized {updated} notifications'))
