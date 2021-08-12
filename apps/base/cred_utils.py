from google.cloud import secretmanager

def get_credentials(secret_id):
    try:
        from .credentials import keys
        return keys[secret_id]
    except:
        client = secretmanager.SecretManagerServiceClient()
        request = {'name':f'projects/873382916416/secrets/{secret_id}/versions/latest'}
        response = client.access_secret_version(request)
        return response.payload.data.decode("utf-8")