class BasePipe:
    def __init__(self, llm, prompt):
        self.llm = llm
        self.prompt = prompt

    async def run(self, **kwargs):
        prompt = self.prompt.format(**kwargs)
        async for token in self.llm.async_run(prompt):
            yield token
