from hermes.providers.clients.openai_compatible import OpenAICompatibleClient


class CloudflareClient(OpenAICompatibleClient):

    base_url = "https://api.cloudflare.com/client/v4"