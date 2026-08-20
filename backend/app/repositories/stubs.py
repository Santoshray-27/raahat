class RepositoryStub:
    async def get_by_id(self, entity_id: str):
        return None
        
    async def save(self, entity):
        return entity
