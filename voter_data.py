import os
import json
from cryptography.fernet import Fernet

class VotersData:
    def __init__(self, data_file="database/voters.enc", key_file="database/secret.key"):
        self.data_file = data_file
        self.key_file = key_file
        self.key = self.load_or_create_key()
        self.fernet = Fernet(self.key)

    def load_or_create_key(self):
        if os.path.exists(self.key_file):
            with open(self.key_file, "rb") as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(self.key_file, "wb") as f:
                f.write(key)
            return key

    def load_voters(self):
        """
        Memuat data voter dari file terenkripsi.
        Jika file tidak ada atau rusak, mengembalikan list kosong.
        """
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "rb") as f:
                    encrypted_data = f.read()
                if encrypted_data:  # Jika file tidak kosong
                    data = self.fernet.decrypt(encrypted_data)
                    return json.loads(data.decode())
            except Exception as e:
                print(f"Error saat memuat voter: {e}")
        # Jika file tidak ada atau rusak, kembalikan list kosong
        return []

    def save_voters(self, voters):
        """
        Menyimpan data voter ke file terenkripsi.
        :param voters: List data voter
        """
        try:
            data = json.dumps(voters).encode()
            encrypted_data = self.fernet.encrypt(data)

            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            with open(self.data_file, "wb") as f:
                f.write(encrypted_data)
        except Exception as e:
            print(f"Error saat menyimpan voter: {e}")

    def save_private_key(self, voter_id, private_key):
        encrypted_key = self.fernet.encrypt(private_key.encode())
        file_path = f"database/private_keys/{voter_id}.key"
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(encrypted_key)
