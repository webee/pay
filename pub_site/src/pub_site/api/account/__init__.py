# coding=utf-8
from ..utils import SubBlueprint
from .. import api_mod

account_mod = SubBlueprint('account', api_mod, '/account')


from . import views