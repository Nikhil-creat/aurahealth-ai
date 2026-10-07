"""JWT verification + role-based access control (tokens are issued by the Node user service)."""
import os, jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

_bearer = HTTPBearer()
RANK = {"user": 1, "coach": 2, "admin": 3}

def require(role: str = "user"):
    def dep(c: HTTPAuthorizationCredentials = Depends(_bearer)):
        try: claims = jwt.decode(c.credentials, os.environ["JWT_SECRET"], algorithms=["HS256"])
        except jwt.PyJWTError: raise HTTPException(401, "invalid or expired token")
        if RANK.get(claims.get("role"), 0) < RANK[role]: raise HTTPException(403, "insufficient role")
        return claims
    return dep
