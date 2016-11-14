# Install requirements
init:
	pip install -r requirements.txt

# Get tweets through Streaming API
stream:
	python -m app.twitter.stream_listener

# Clean tweets then save as Sequence
sequence:
	python -m app.twitter.tweet_cleaner

# Build dictionaries
dict:
	python -m app.tensorflow.dictionary_builder

# Train RNN (without Docker)
train:
	rm -rf tensorboard/*
	python -m app.tensorflow.train

# Train RNN (via Docker)
docker-train:
	rm -rf tensorboard/*
	docker-compose stop
	docker-compose build
	docker-compose up -d train tensorboard

# Show docker logs
log:
	docker-compose logs -f --tail 10 train

# Stop docker
stop:
	docker-compose stop