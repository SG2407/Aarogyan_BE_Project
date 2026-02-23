from fastapi import APIRouter, HTTPException, status, Depends

from app.schemas.auth import (
    UserRegister, UserLogin, AuthResponse, Token, 
    UserResponse, TokenRefresh
)
from app.schemas.user import UserUpdate
from app.core.database import get_supabase
from app.core.security import (
    get_password_hash, verify_password,
    create_access_token, create_refresh_token, decode_token
)
from app.api.dependencies import get_current_user
from datetime import datetime
import uuid

router = APIRouter()

@router.put("/me", response_model=UserResponse)
async def update_profile(
    update: UserUpdate,
    supabase = Depends(get_supabase),
    current_user = Depends(get_current_user)
):
    """
    Update current user's profile (name, age, gender, phone, emergency_contact)
    - Requires authentication
    - Returns updated user info
    """
    update_data = update.dict(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No data to update")

    # Update user in Supabase
    response = supabase.table("profiles").update(update_data).eq("id", current_user["id"]).execute()
    if not response.data:
        raise HTTPException(status_code=500, detail="Failed to update profile")
    updated_user = response.data[0]
    return UserResponse(
        id=updated_user["id"],
        email=updated_user["email"],
        name=updated_user["name"],
        age=updated_user.get("age"),
        gender=updated_user.get("gender"),
        phone=updated_user.get("phone"),
        emergency_contact=updated_user.get("emergency_contact"),
        created_at=updated_user["created_at"]
    )


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, supabase = Depends(get_supabase)):
    """
    Register a new user
    
    - Creates user account with email and password
    - Stores user profile information
    - Returns JWT tokens for authentication
    """
    
    # Check if user already exists
    existing_user = supabase.table("profiles").select("email").eq("email", user_data.email).execute()
    
    if existing_user.data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password
    hashed_password = get_password_hash(user_data.password)
    
    # Generate user ID
    user_id = str(uuid.uuid4())
    
    # Create user profile
    profile_data = {
        "id": user_id,
        "email": user_data.email,
        "password_hash": hashed_password,
        "name": user_data.name,
        "age": user_data.age,
        "gender": user_data.gender,
        "phone": user_data.phone,
        "emergency_contact": user_data.emergency_contact,
        "created_at": datetime.utcnow().isoformat()
    }
    
    try:
        response = supabase.table("profiles").insert(profile_data).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user"
            )
        
        created_user = response.data[0]
        
        # Generate tokens
        access_token = create_access_token(data={"sub": user_id, "email": user_data.email})
        refresh_token = create_refresh_token(data={"sub": user_id})
        
        # Prepare response
        user_response = UserResponse(
            id=created_user["id"],
            email=created_user["email"],
            name=created_user["name"],
            age=created_user.get("age"),
            gender=created_user.get("gender"),
            phone=created_user.get("phone"),
            emergency_contact=created_user.get("emergency_contact"),
            created_at=created_user["created_at"]
        )
        
        token_response = Token(
            access_token=access_token,
            refresh_token=refresh_token
        )
        
        return AuthResponse(user=user_response, token=token_response)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/login", response_model=AuthResponse)
async def login(credentials: UserLogin, supabase = Depends(get_supabase)):
    """
    Login with email and password
    
    - Verifies credentials
    - Returns JWT tokens for authentication
    """
    
    # Get user by email
    response = supabase.table("profiles").select("*").eq("email", credentials.email).execute()
    
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    user = response.data[0]
    
    # Verify password
    if not verify_password(credentials.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Generate tokens
    access_token = create_access_token(data={"sub": user["id"], "email": user["email"]})
    refresh_token = create_refresh_token(data={"sub": user["id"]})
    
    # Prepare response
    user_response = UserResponse(
        id=user["id"],
        email=user["email"],
        name=user["name"],
        age=user.get("age"),
        gender=user.get("gender"),
        phone=user.get("phone"),
        emergency_contact=user.get("emergency_contact"),
        created_at=user["created_at"]
    )
    
    token_response = Token(
        access_token=access_token,
        refresh_token=refresh_token
    )
    
    return AuthResponse(user=user_response, token=token_response)


@router.post("/refresh", response_model=Token)
async def refresh_token(token_data: TokenRefresh, supabase = Depends(get_supabase)):
    """
    Refresh access token using refresh token
    
    - Validates refresh token
    - Issues new access token
    """
    
    payload = decode_token(token_data.refresh_token)
    
    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user_id = payload.get("sub")
    
    # Verify user still exists
    response = supabase.table("profiles").select("email").eq("id", user_id).execute()
    
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user = response.data[0]
    
    # Generate new tokens
    access_token = create_access_token(data={"sub": user_id, "email": user["email"]})
    new_refresh_token = create_refresh_token(data={"sub": user_id})
    
    return Token(
        access_token=access_token,
        refresh_token=new_refresh_token
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(supabase = Depends(get_supabase), current_user = Depends(get_current_user)):
    """
    Get current user profile
    
    - Requires authentication
    - Returns user information
    """
    
    return UserResponse(
        id=current_user["id"],
        email=current_user["email"],
        name=current_user["name"],
        age=current_user.get("age"),
        gender=current_user.get("gender"),
        phone=current_user.get("phone"),
        emergency_contact=current_user.get("emergency_contact"),
        created_at=current_user["created_at"]
    )
