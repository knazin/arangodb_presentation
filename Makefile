run_db:
	docker-compose up -d arangodb

# get_auth_token:
# 	@curl -X POST \
# 	'http://localhost:8529/_open/auth' \
# 	--header 'Content-Type: application/json' \
# 	--data-raw '{"username": "root", "password": "${PASS}"}'
# 	@printf "\n"

# create_db:
# 	curl -X POST \
# 	'http://localhost:8529/_api/database' \
# 	--header 'Content-Type: application/json' \
# 	--header 'Authorization: Bearer ${TOKEN}' \
# 	--data-raw '{"name": "arango"}'
# 	@printf "\n"

import_data:
	docker-compose exec arangodb arangorestore --server.database IMDB --create-database --include-system-collections

build_app:
	docker build -f ./deployment/Dockerfile -t arango_fastapi_app .

run_all:
	docker-compose up -d



