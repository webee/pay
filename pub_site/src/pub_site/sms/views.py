# coding=utf-8
from __future__ import unicode_literals

from . import sms_mod as mod
from flask import request, jsonify
from flask.ext.login import current_user
from pub_site.auth.utils import login_required
from pub_site.sms.verification_code_manager import generate_and_send_verification_code
from pytoolbox.util.log import get_logger


logger = get_logger(__name__)


@mod.route('/send_verification_code', methods=['POST'])
@login_required
def send_verification_code():
    source = request.values['source']
    phone_no = current_user.phone_no
    if not phone_no:
        return jsonify(ret=False, code=450, msg='no phone.'), 200
    ret = generate_and_send_verification_code(source, current_user.user_id, phone_no)
    if ret:
        return jsonify(ret=True, phone_no=mask_phone_no(phone_no)), 200
    return jsonify(ret=False, code=400, msg='failed.'), 200


def mask_phone_no(phone_no):
    return u"%s****%s" % (phone_no[:3], phone_no[-4:])
