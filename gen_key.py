import os
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization

class KeyManager:
    """
    Class untuk mengelola pembuatan, penyimpanan, dan pengambilan kunci public-private ECC.
    """
    def __init__(self, key_dir="database/keys"):
        self.key_dir = key_dir
        if not os.path.exists(self.key_dir):
            os.makedirs(self.key_dir)

    def generate_keys(self, voter_id):
        """
        Membuat pasangan kunci ECC dan menyimpannya ke file.
        :param voter_id: ID unik untuk voter (digunakan untuk menamai file kunci).
        """
        # Generate private key
        private_key = ec.generate_private_key(ec.SECP256R1())

        # Serialize private key
        private_key_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )

        # Generate public key
        public_key = private_key.public_key()

        # Serialize public key
        public_key_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

        # Save keys to files
        private_key_path = os.path.join(self.key_dir, f"{voter_id}_private_key.pem")
        public_key_path = os.path.join(self.key_dir, f"{voter_id}_public_key.pem")

        with open(private_key_path, "wb") as priv_file:
            priv_file.write(private_key_pem)

        with open(public_key_path, "wb") as pub_file:
            pub_file.write(public_key_pem)

        print(f"Kunci ECC untuk voter {voter_id} telah dibuat dan disimpan.")
        return private_key_path, public_key_path

    def load_keys(self, voter_id):
        """
        Memuat pasangan kunci dari file.
        :param voter_id: ID unik untuk voter.
        :return: Tuple (private_key, public_key) dalam format objek.
        """
        private_key_path = os.path.join(self.key_dir, f"{voter_id}_private_key.pem")
        public_key_path = os.path.join(self.key_dir, f"{voter_id}_public_key.pem")

        if not os.path.exists(private_key_path) or not os.path.exists(public_key_path):
            raise FileNotFoundError(f"Kunci untuk voter {voter_id} tidak ditemukan.")

        # Load private key
        with open(private_key_path, "rb") as priv_file:
            private_key = serialization.load_pem_private_key(
                priv_file.read(),
                password=None,
            )

        # Load public key
        with open(public_key_path, "rb") as pub_file:
            public_key = serialization.load_pem_public_key(pub_file.read())

        return private_key, public_key

    def get_public_key_pem(self, voter_id):
        """
        Mengembalikan public key dalam format PEM (untuk dibagikan sebagai QR code).
        :param voter_id: ID unik untuk voter.
        :return: Public key dalam format string PEM.
        """
        public_key_path = os.path.join(self.key_dir, f"{voter_id}_public_key.pem")
        if not os.path.exists(public_key_path):
            raise FileNotFoundError(f"Public key untuk voter {voter_id} tidak ditemukan.")

        with open(public_key_path, "rb") as pub_file:
            public_key_pem = pub_file.read()

        return public_key_pem.decode()

    def get_private_key_pem(self, voter_id):
        """
        Mengembalikan private key dalam format PEM.
        :param voter_id: ID unik untuk voter.
        :return: Private key dalam format string PEM.
        """
        private_key_path = os.path.join(self.key_dir, f"{voter_id}_private_key.pem")
        if not os.path.exists(private_key_path):
            raise FileNotFoundError(f"Private key untuk voter {voter_id} tidak ditemukan.")

        with open(private_key_path, "rb") as priv_file:
            private_key_pem = priv_file.read()

        return private_key_pem.decode()

    def load_public_key(self, voter_id):
        """
        Memuat kunci publik dari file.
        :param voter_id: ID unik untuk voter.
        :return: Public key dalam format objek.
        """
        public_key_path = os.path.join(self.key_dir, f"{voter_id}_public_key.pem")

        if not os.path.exists(public_key_path):
            raise FileNotFoundError(f"Kunci publik untuk voter {voter_id} tidak ditemukan.")

        # Load public key
        with open(public_key_path, "rb") as pub_file:
            public_key = serialization.load_pem_public_key(pub_file.read())

        return public_key