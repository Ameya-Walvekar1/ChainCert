from .models import Role, Permission
ROLE_PERMISSIONS={
 Role.PLATFORM_ADMIN:set(Permission),
 Role.INSTITUTION_ADMIN:{Permission.PUBLIC_VERIFY,Permission.ISSUE_CERTIFICATE,Permission.CORRECT_CERTIFICATE,
  Permission.BATCH_ADMINISTRATION,Permission.REVOKE_CERTIFICATE,Permission.MANAGE_INSTITUTION_USERS},
 Role.ISSUER:{Permission.PUBLIC_VERIFY,Permission.ISSUE_CERTIFICATE},
 Role.STUDENT:{Permission.PUBLIC_VERIFY},
 Role.PUBLIC_VERIFIER:{Permission.PUBLIC_VERIFY}}
def has_permission(role:Role, permission:Permission)->bool:
 return permission in ROLE_PERMISSIONS.get(role,set())
