from sqlalchemy.orm import declarative_base, registry

# db = declarative_base()
mapper_registry = registry()
db = mapper_registry.generate_base()
