# About
A simple LINE bot that automatically reply a sticker according to the message content. <br />
This is the source code of my presentation's demo at [【AWS×BOT】TechTalk #3](http://lig.connpass.com/event/41826/). <br />
Slides can be found here: http://www.slideshare.net/vanhuyz/tensorflowline-botaws-lambda (Japanese)

# Environment
* Python 2.7
* TensorFlow r0.11
* SQLite 3

# Installation

## Install MeCab

```bash
# Ubuntu 14.04:
$ sudo apt-get install -y mecab mecab-ipadic-utf8 libmecab-dev
```

## (Optional) Install mecab-ipadic-neologd dictionary
See https://github.com/neologd/mecab-ipadic-neologd for more detailed information.

## Install requirements

* Install pip if it is not already installed
* Run install

```bash
$ pip install -r requirements.txt
# or
$ make init
```

# Usages
## Start streaming data from Twitter

```bash
$ make stream
```

## Preprocessing
* Clean tweets then save to Sequence table

```bash
$ make sequence
```

* Build dictionaries

```bash
$ make dict
```

## Training

* Configure hyperparameters in app/common/settings.py if needed

* Without Docker

```bash
$ make train
```

* With Docker (currently only has GPU Support version)
```bash
$ make docker-train
```
