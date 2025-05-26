from app.core.security import hash_password, verify_password


# Testes de hash e verificação de senha
class TestPasswordSecurity:

    # Verifica se dois hashes da mesma senha são diferentes
    def test_hash_password_produces_unique_hashes(self):
        password = "senha123"
        hashed1 = hash_password(password)
        hashed2 = hash_password(password)

        assert hashed1 != hashed2
        assert hashed1.startswith("$2b$") or hashed1.startswith("$2a$")
        assert hashed2.startswith("$2b$") or hashed2.startswith("$2a$")

    # Verifica se a verificação de senha funciona corretamente
    def test_verify_password_correct_and_incorrect(self):
        password = "minha_senha_segura"
        hashed_password = hash_password(password)

        assert verify_password(password, hashed_password)  # senha correta
        assert not verify_password("senha_errada", hashed_password)  # senha incorreta
