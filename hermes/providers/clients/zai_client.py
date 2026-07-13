from hermes.providers.clients.openai_compatible import OpenAICompatibleClient


class ZAIClient(OpenAICompatibleClient):

    base_url = "https://open.bigmodel.cn/api/paas/v4"