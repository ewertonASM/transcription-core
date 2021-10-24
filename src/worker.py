import datetime
import json
import logging.config
import os

from deepspeech import Model

from process import dsprocessaudio
from queues import queuewrapper
from util import configreader, exceptionhandler


class Worker:

    def __init__(self, dl_model, dl_scorer):
        self.__logger = logging.getLogger(self.__class__.__name__)

        self.deep_model = self.__instantiate_model(dl_model, dl_scorer)

        self.dsprocessaudio = dsprocessaudio.DeepSpeechAudio()

        self.consumer = queuewrapper.QueueConsumer()
        self.publisher = queuewrapper.QueuePublisher()

        # self.rabbitconnectionrefresh = rabbitconnectionrefresh.RabbitRefreshConnection(self.consumer, self.publisher)
        # self.rabbitconnectionrefresh.start() 


    def __instantiate_model(self, model, scorer):

        try:
            ds = Model(model)
        except:
            logger.info("Invalid model file. Exiting.")
            raise SystemExit(1)

        try:
            ds.enableExternalScorer(scorer)
        except:
            logger.info("Invalid scorer file. Running inference using only model file.")
            
        return(ds)        

    def __reply_message(self, route, message):
        self.__logger.info("Sending response to request.")

        if id is None:
            self.__logger.error("The request don't have correlation_id.")

        if route is None:
            self.__logger.error("The request don't have reply_to route.")
        else:
            self.publisher.publish_to_queue(route, message)


    def __callback(self, _ch, _method, _properties, body):

        tmp_dir = "tmp/"
        message = json.loads(body.decode("utf-8"))

        if not os.path.exists(tmp_dir):
            os.makedirs(tmp_dir)

        self.__logger.info("Processing a new transciption request.")
        split_inferred_text = self.dsprocessaudio.process(ds=self.deep_model, message=message)

        interval = message["interval"]

        timesdelta = []

        timesdelta.append(datetime.timedelta(seconds=float(interval.split("-")[0])))
        timesdelta.append(datetime.timedelta(seconds=float(interval.split("-")[1])))

        formated_interval = []

        for timedelta in timesdelta:
            sep = ','
            if '.' in str(timedelta):
                timestamp = "0" + str(timedelta).split(".")[0] + sep + str(timedelta).split(".")[-1][:3]
            else:
                timestamp = "0" + str(timedelta) + sep + "000"
            
            formated_interval.append(timestamp)

        if split_inferred_text:
            msg = {
                "videoId": message["videoId"],
                "text": split_inferred_text,
                "timeLimits": f'{formated_interval[0]} --> {formated_interval[1]}',
                "snippet": f'{message["snippet"]}',
            }


            payload = json.dumps(msg)

            self.__reply_message(route="subtitle-receive", message=payload)

        for f in os.listdir(tmp_dir):
            os.remove(os.path.join(tmp_dir, f))

    def start(self, queue):
        self.__logger.debug("Starting queue consumer.")
        self.consumer.consume_from_queue(queue, self.__callback)

    def stop(self):
        self.__logger.debug("Stopping queue consumer.")
        self.consumer.close_connection()
        self.__logger.debug("Stopping queue publisher.")
        self.publisher.close_connection()


if __name__ == "__main__":
    logging.config.fileConfig(os.environ.get("LOGGER_CONFIG_FILE", ""))
    logger = logging.getLogger(__name__)

    workercfg = configreader.load_configs("Worker")

    if not workercfg:
        raise SystemExit(1)

    try:
        logger.info("Creating Transcription Worker.")
        worker = Worker(workercfg.get("DLTranscriptionModel", ""), workercfg.get("DLTranscriptionScore", ""))
        logger.info("Starting Transcription Worker.")
        worker.start(workercfg.get("TranscriptionQueue"))

    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt: stopping Transcription Worker.")

    except Exception:
        logger.exception("Unexpected error has occured in Transcription Worker.")

    finally:
        worker.stop()
        raise SystemExit(1)
