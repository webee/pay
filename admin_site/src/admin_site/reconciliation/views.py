# -*- coding: utf-8 -*-
from . import recon_mod as mod
from flask import render_template


@mod.route('/', methods=['GET'])
def list_reconciliation():
    return render_template('reconciliation/list.html', form=form)