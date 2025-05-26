import uuid


# Gera um email unico, usado para testes
def generate_unique_email():
    return f"{uuid.uuid4()}@example.com"
