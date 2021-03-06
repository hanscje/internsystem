from core.utils import SharedAPIRootRouter

from intern.rest import *

# SharedAPIRootRouter is automatically imported in global urls config
router = SharedAPIRootRouter()
router.register(r'intern/interns', InternViewSet, base_name='interns')
router.register(r'intern/groups', InternGroupViewSet, base_name='interngroups')
router.register(r'intern/accesslevels', AccessLevelViewSet, base_name='accesslevels')
router.register(r'intern/roles', RoleViewSet, base_name='roles')
router.register(r'intern/internroles', InternRoleViewSet, base_name='internroles')
