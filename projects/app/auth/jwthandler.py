import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, Request
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.security import OAuth2
from fastapi.security.utils import get_authorization_scheme_param
from jose import JWTError, jwt

from app.schemas.token import TokenData
from app.auth.users import get_user



SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class OAuth2PasswordBearerCookie(OAuth2):
    """ OAuth class modified to check for jwt token in cookies.
    
    Attributes
    ----------
    token_url: str
        Name of login url
        
    Methods
    -------
    __call__ (request)
        Gets the cookie and checks for 'bearer'
    
    Returns
    -------
    param: dict
        returns jwt cookie
    
    """
    def __init__(
        self,
        token_url: str,
        scheme_name: str = None,
        scopes: dict = None,
        auto_error: bool = True,
    ):
        if not scopes:
            scopes = {}
        flows = OAuthFlowsModel(password={"tokenUrl": token_url, "scopes": scopes})
        super().__init__(flows=flows, scheme_name=scheme_name, auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[str]:
        authorization: str = request.cookies.get("Authorization")
        scheme, param = get_authorization_scheme_param(authorization)

        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=401,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                return None

        return param


security = OAuth2PasswordBearerCookie(token_url="/login")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """ Creates a jwt token.
    
    Paramters
    ---------
    data : dict
        user data to encode in jwt, here username
    
    Returns
    -------
    encoded_jwt : str
        jwt cookie
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    # Add expire time to to encode dict
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


async def get_current_user(token: str = Depends(security)):
    """ Gets user name encoded in cookie i.e. current user.
    
    This is a subdependence so we can use Depends in the function
    
    Parameters
    ----------
    token: str
        Gets username and expdate via param in dependency OAuth2PasswordBearerCookie
    
    Returns
    -------
    user: str
        Returns logged in username
    
    """
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Token is returned from Depends, we decode to get 
        # the {'sub':xxx, 'exp':xxx} dict back
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")

        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    # From the token user, get the db user data
    user = await get_user(token_data.username)

    return user
