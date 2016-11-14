PROJECT_HOME=$HOME/preprocessing
ZIP_FILE=$PROJECT_HOME/preprocessing.zip

rm ${ZIP_FILE}
zip -r9v ${ZIP_FILE} * -x@exclude.lst
cd $PROJECT_HOME/env/lib/python2.7/dist-packages/
zip -r9v ${ZIP_FILE} .  --exclude \*.pyc
cd $PROJECT_HOME/env/lib64/python2.7/dist-packages/
zip -r9v ${ZIP_FILE} .  --exclude \*.pyc
aws s3 cp ${ZIP_FILE} s3://${S3_BUCKET}/lambda/preprocessing.zip
aws lambda update-function-code --function-name preprocessing --s3-bucket ${S3_BUCKET} --s3-key lambda/preprocessing.zip