import os
import json
from cryptography.fernet import Fernet

class CandidateData:
    """
    Class untuk mengelola penyimpanan kandidat dengan enkripsi.
    """
    def __init__(self, data_file="database/candidates.enc", key_file="database/secret.key"):
        self.data_file = data_file
        self.key_file = key_file
        self.key = self.load_or_create_key()
        self.fernet = Fernet(self.key)

    def load_or_create_key(self):
        """
        Membuat atau memuat kunci enkripsi untuk Fernet.
        """
        if os.path.exists(self.key_file):
            with open(self.key_file, "rb") as f:
                key = f.read()
                if len(key) != 44:  # Panjang kunci base64 untuk Fernet harus 44 karakter
                    raise ValueError("Kunci yang ada tidak valid untuk Fernet.")
                return key
        else:
            key = Fernet.generate_key()  # Generate key yang valid
            os.makedirs(os.path.dirname(self.key_file), exist_ok=True)
            with open(self.key_file, "wb") as f:
                f.write(key)
            return key


    def save_candidates(self, candidates):
        try:
            data = json.dumps(candidates).encode()
            encrypted_data = self.fernet.encrypt(data)
            with open(self.data_file, "wb") as f:
                f.write(encrypted_data)
        except Exception as e:
            print(f"Error saat menyimpan kandidat: {e}")

    def load_candidates(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "rb") as f:
                    encrypted_data = f.read()
                if encrypted_data:
                    data = self.fernet.decrypt(encrypted_data)
                    return json.loads(data.decode())
            except Exception as e:
                print(f"Error saat memuat kandidat: {e}")
        default_candidates = ["Alice", "Bob", "Charlie"]
        self.save_candidates(default_candidates)
        return default_candidates
