# product-service/app/consumer.py
import boto3, json, os, logging
from . import db
from .models import Product
 
sqs    = boto3.client('sqs', region_name=os.environ['AWS_REGION'])
QUEUE  = os.environ['SQS_ORDER_QUEUE_URL']
logger = logging.getLogger(__name__)
 
def process_order_placed(message_body):
    """Decrement stock for each item in the order."""
    order = json.loads(message_body)
    with db.app.app_context():
        for item in order['items']:
            product = Product.query.get(item['product_id'])
            if product:
                product.stock = max(0, product.stock - item['quantity'])
        db.session.commit()
    logger.info('Stock updated for order %s', order['order_id'])
 
def poll_queue():
    """Long-poll SQS indefinitely. Runs in background thread."""
    logger.info('SQS consumer started, polling: %s', QUEUE)
    while True:
        try:
            resp = sqs.receive_message(
                QueueUrl            = QUEUE,
                MaxNumberOfMessages = 10,
                WaitTimeSeconds     = 20   # long-poll reduces empty receives
            )
            for msg in resp.get('Messages', []):
                process_order_placed(msg['Body'])
                sqs.delete_message(
                    QueueUrl      = QUEUE,
                    ReceiptHandle = msg['ReceiptHandle']
                )
        except Exception as e:
            logger.error('Consumer error: %s', e)
