https://stackoverflow.com/questions/53035896/serving-multiple-tensorflow-models-using-docker

https://medium.com/@mohamed.10592/from-building-to-deploying-deep-learning-models-using-tensorflow-docker-and-heroku-d6ab37e9117d

https://www.tensorflow.org/tfx/serving/serving_config


Working command

nohup tensorflow_model_server --model_config_file=/home/jorgelameira/Desktop/Projects/Dan/Deploying_a_Model/config/models.conf --rest_api_port=8501 >server.log 2>&1

