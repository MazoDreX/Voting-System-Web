from phe import paillier

class PaillierEVoting:
    def __init__(self):
        # Generate key pair
        self.public_key, self.private_key = paillier.generate_paillier_keypair()

    def encrypt_vote(self, vote):
        return self.public_key.encrypt(vote)

    def decrypt_vote(self, encrypted_vote):
        return self.private_key.decrypt(encrypted_vote)

    def aggregate_votes(self, encrypted_votes):
        aggregated_vote = encrypted_votes[0]
        for vote in encrypted_votes[1:]:
            aggregated_vote += vote
        return aggregated_vote