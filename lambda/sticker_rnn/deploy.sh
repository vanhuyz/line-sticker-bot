PROJECT_HOME=$HOME/sticker_rnn
ZIP_FILE=$PROJECT_HOME/sticker_rnn.zip

rm ${ZIP_FILE}
zip -r9v ${ZIP_FILE} main.py settings.py model.ckpt dicts/reverse_sticker_dictionary.pickle
cd $PROJECT_HOME/lib/python2.7/dist-packages/
zip -r9v ${ZIP_FILE} .  --exclude \*.pyc
cd $PROJECT_HOME/lib64/python2.7/dist-packages/
zip -r9v ${ZIP_FILE} .  --exclude \*.pyc

aws s3 cp ${ZIP_FILE} s3://${S3_BUCKET}/lambda/sticker_rnn.zip
aws lambda update-function-code --function-name stickerRNN --s3-bucket ${S3_BUCKET} --s3-key lambda/sticker_rnn.zip