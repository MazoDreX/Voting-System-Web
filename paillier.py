from phe import paillier
import os
import json
from candidate_data import CandidateData

candidates = CandidateData()

class PaillierEVoting:
    def __init__(self, key_dir="database/keys_paillier"):
        self.key_dir = key_dir
        if not os.path.exists(self.key_dir):
            os.makedirs(self.key_dir)
        self.public_key, self.private_key = self.load_keys_or_generate()

        self.voter_status = {}
        self.votes = []
        
        self.candidates_name = []
        self.candidate_map = {}


    def load_keys_or_generate(self):
        public_key_path = os.path.join(self.key_dir, "paillier_public_key.pem")
        private_key_path = os.path.join(self.key_dir, "paillier_private_key.pem")
        
        if os.path.exists(public_key_path) and os.path.exists(private_key_path):
            with open(public_key_path, "r") as pub_file:
                public_key_n = int(pub_file.read().strip())
            public_key = paillier.PaillierPublicKey(public_key_n)

            with open(private_key_path, "r") as priv_file:
                private_key_data = priv_file.read().strip().split(",")
                private_key_p = int(private_key_data[0])
                private_key_q = int(private_key_data[1])
            private_key = paillier.PaillierPrivateKey(public_key, private_key_p, private_key_q)
        else:
            public_key, private_key = paillier.generate_paillier_keypair()
            
            with open(public_key_path, "w") as pub_file:
                pub_file.write(str(public_key.n))
            with open(private_key_path, "w") as priv_file:
                priv_file.write(f"{private_key.p},{private_key.q}")
        
        return public_key, private_key

    def encrypt_vote(self, vote):
        return self.public_key.encrypt(vote)

    def decrypt_vote(self, encrypted_vote):
        return self.private_key.decrypt(encrypted_vote)


    def vote(self, voter_id, choice, candidate_map):
        # Cek apakah voter sudah memberikan suara
        if voter_id in self.voter_status and self.voter_status[voter_id]:
            raise ValueError("Voter ini sudah memberikan suara.")

        # Validasi pilihan kandidat
        if choice not in candidate_map:
            raise ValueError(f"Nama kandidat tidak valid: {choice}")

        # Konversi nama kandidat ke ID numerik
        choice_id = candidate_map[choice]
        print(choice_id)

        # Enkripsi suara
        encrypted_vote = self.encrypt_vote(choice_id)

        # Tandai voter sudah memberikan suara
        self.voter_status[voter_id] = True

        # Simpan suara terenkripsi
        self.votes.append(encrypted_vote)

        return encrypted_vote

    
    def tally_votes(self, candidates_name, candidate_map):
        if len(candidates_name) == 0:
            raise ValueError("Tidak ada kandidat untuk dihitung.")

        vote_counts = {candidate['name']: 0 for candidate in candidates_name}

        for encrypted_vote in self.votes:
            decrypted_vote = self.private_key.decrypt(encrypted_vote)

            for candidate_name, candidate_id in candidate_map.items():
                if decrypted_vote == candidate_id:
                    vote_counts[candidate_name] += 1
                    break

        print(f"Hasil Akhir: {vote_counts}")
        return vote_counts