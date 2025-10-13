from django.core.management.base import BaseCommand
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
import base64


class Command(BaseCommand):
    help = 'Generate VAPID keys for web push notifications'

    def handle(self, *args, **options):
        private_key = ec.generate_private_key(ec.SECP256R1())

        private_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )

        public_key = private_key.public_key()
        public_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.X962,
            format=serialization.PublicFormat.UncompressedPoint
        )

        public_key_b64 = base64.urlsafe_b64encode(public_bytes).strip(b'=').decode()
        private_key_pem = private_bytes.decode()

        self.stdout.write(self.style.SUCCESS('\nVAPID keys generated successfully!\n'))
        self.stdout.write('Add these to your .env file:\n')
        self.stdout.write(f'VAPID_PUBLIC_KEY={public_key_b64}\n')
        self.stdout.write(f'VAPID_PRIVATE_KEY="{private_key_pem}"\n')
        self.stdout.write('\nFor Fly.io deployment, run:\n')
        self.stdout.write(f'fly secrets set VAPID_PUBLIC_KEY="{public_key_b64}" -a nid\n')
        self.stdout.write('fly secrets set VAPID_PRIVATE_KEY="<copy-private-key-from-above>" -a nid\n')
