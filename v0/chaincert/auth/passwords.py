from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHashError
_hasher=PasswordHasher()
def hash_password(password:str)->str:
 if not isinstance(password,str) or len(password)<12: raise ValueError("Password must be at least 12 characters")
 return _hasher.hash(password)
def verify_password(password:str, encoded_hash:str)->bool:
 try: return _hasher.verify(encoded_hash,password)
 except (VerifyMismatchError,VerificationError,InvalidHashError,TypeError): return False
