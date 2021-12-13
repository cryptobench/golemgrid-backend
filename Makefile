 
DJANGO   := phillipjensen/golemgrid-backend
LATEST_DJANGO := ${DJANGO}:${GITHUB_SHA}
LATEST_DJANGO2 := ${DJANGO}:latest

CELERY   := phillipjensen/golemgrid-backend-celery
LATEST_CELERY := ${CELERY}:${GITHUB_SHA}

CELERY_BEAT   := phillipjensen/golemgrid-backend-celery-beat
LATEST_CELERY_BEAT := ${CELERY_BEAT}:${GITHUB_SHA}
 
build:
	@docker buildx create --use	
	@docker buildx build --platform=linux/arm64,linux/amd64 --push -t ${LATEST_DJANGO} -t ${DJANGO}:latest -f ./dockerfiles/Django .
	@docker buildx build --platform=linux/arm64,linux/amd64 --push -t ${LATEST_CELERY} -t ${CELERY}:latest -f ./dockerfiles/Celery .
	@docker buildx build --platform=linux/arm64,linux/amd64 --push -t ${LATEST_CELERY_BEAT} -t ${CELERY_BEAT}:latest -f ./dockerfiles/Beat .

 
login:
	@docker login -u ${DOCKER_USER} -p ${DOCKER_PASS}
	