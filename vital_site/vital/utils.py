import logging
from models import Audit
logger = logging.getLogger(__name__)


def audit(request, obj, action):
    logger.debug('In audit')
    if request.user.id is not None:
        audit_record = Audit(done_by=request.user.id, category=type(obj).__name__, item_id=obj.id, action=action)
    else:
        audit_record = Audit(done_by=0, category=type(obj).__name__, item_id=obj.id, action=action)
        logger.error('An action is being performed without actual user id.')
    audit_record.save()