.PHONY: build runrun remove

build:
	docker build -t tts .

run:
	docker rm -f tts || true
	docker run -p 443:443 --name  tts tts


remove:
	docker rm -f tts || true

dev:
	poetry run dev

start:
	poetry run start