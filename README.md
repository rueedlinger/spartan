# Spartan

## Project Setup
```bash
pyenv install 3.11.0
pyenv virtualenv 3.11.0 py3.11-spartan
pyenv activate py3.11-spartan
```

## Infrastructure

```bash
docker compose up
```

urls:
- mongo-express: http://localhost:8081
- minio: http://localhost:9090/

### MongoDB
```bash
export SPARTAN_MONGODB_URL="mongodb://root:example@localhost:27017/spartan?authSource=admin"
export SPARTAN_S3_ENDPOINT="minio:9000"
export SPARTAN_S3_ACCESS_KEY="root"
export SPARTAN_S3_SECRET_KEY="secret-key"
export SPARTAN_S3_SECURE="true"
```

Setup replica set

```
mongosh mongodb://localhost:27017/ -u root -p example
```

```
rs.initiate({
    _id: 'spartan-change-streams',
    members: [{ _id : 0, host : '127.0.0.1:27017'}]
});

rs.status();
```



## Data (spartan-core)
```bash
cd spartan-core
uvicorn data.main:app --reload --log-config=conf/log_conf.yaml
```
urls:
- docs: http://127.0.0.1:8000/docs
- redoc: http://127.0.0.1:8000/redoc

## UI
tbd

## Connectors
tbd





