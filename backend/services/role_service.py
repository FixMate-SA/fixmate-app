from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from models import User, Fixer

class RoleService:
    def __init__(self):
        self.admin_phones = [
            "+27821234567",  # Default admin phone - you can change this
            "+27123456789",  # Additional admin phone
        ]
    
    def determine_user_role(self, phone: str, db: Session) -> Dict[str, Any]:
        """
        Determine user role based on phone number and database records
        Priority: admin > fixer > client
        """
        try:
            # Check if phone is in admin list
            if phone in self.admin_phones:
                return {
                    "role": "admin",
                    "is_fixer": False,
                    "fixer_data": None,
                    "permissions": self.get_permissions("admin")
                }
            
            # Check if user exists as a fixer
            fixer = db.query(Fixer).filter(Fixer.phone == phone).first()
            if fixer:
                return {
                    "role": "fixer", 
                    "is_fixer": True,
                    "fixer_data": {
                        "id": fixer.id,
                        "services": fixer.services,
                        "location": fixer.location,
                        "rating": fixer.rating,
                        "total_jobs": fixer.total_jobs,
                        "is_active": fixer.is_active,
                        "payment_status": fixer.payment_status
                    },
                    "permissions": self.get_permissions("fixer")
                }
            
            # Default to client
            return {
                "role": "client",
                "is_fixer": False, 
                "fixer_data": None,
                "permissions": self.get_permissions("client")
            }
            
        except Exception as e:
            print(f"Error determining role: {str(e)}")
            return {
                "role": "client",
                "is_fixer": False,
                "fixer_data": None,
                "permissions": self.get_permissions("client")
            }
    
    def get_permissions(self, role: str) -> Dict[str, bool]:
        """
        Get permissions based on role
        """
        permissions = {
            "client": {
                "can_create_jobs": True,
                "can_hire_fixers": True,
                "can_leave_reviews": True,
                "can_view_fixers": True,
                "can_manage_profile": True,
                "can_access_sms": True,
                "can_access_learning": True,
                "can_access_payments": False,
                "can_access_admin": False,
                "can_verify_fixers": False,
                "can_settle_payments": False
            },
            "fixer": {
                "can_create_jobs": True,  # Fixers can also create jobs as clients
                "can_hire_fixers": True,
                "can_leave_reviews": True,
                "can_view_fixers": True,
                "can_manage_profile": True,
                "can_access_sms": True,
                "can_access_learning": True,
                "can_access_payments": True,
                "can_view_job_assignments": True,
                "can_manage_fixer_profile": True,
                "can_upload_verification": True,
                "can_access_admin": False,
                "can_verify_fixers": False,
                "can_settle_payments": False
            },
            "admin": {
                "can_create_jobs": True,
                "can_hire_fixers": True,
                "can_leave_reviews": True,
                "can_view_fixers": True,
                "can_manage_profile": True,
                "can_access_sms": True,
                "can_access_learning": True,
                "can_access_payments": True,
                "can_view_job_assignments": True,
                "can_access_admin": True,
                "can_verify_fixers": True,
                "can_settle_payments": True,
                "can_manage_all_users": True,
                "can_view_analytics": True,
                "can_update_payment_status": True
            }
        }
        
        return permissions.get(role, permissions["client"])
    
    def create_or_update_user(self, phone: str, name: str, email: str, db: Session) -> User:
        """
        Create or update user with appropriate role
        """
        try:
            # Get role information
            role_info = self.determine_user_role(phone, db)
            
            # Check if user exists
            user = db.query(User).filter(User.phone == phone).first()
            
            if user:
                # Update existing user
                user.name = name
                user.email = email
                user.role = role_info["role"]
                user.is_active = True
            else:
                # Create new user
                user = User(
                    phone=phone,
                    name=name,
                    email=email,
                    role=role_info["role"],
                    is_active=True
                )
                db.add(user)
            
            db.commit()
            db.refresh(user)
            return user
            
        except Exception as e:
            db.rollback()
            print(f"Error creating/updating user: {str(e)}")
            raise e
    
    def get_user_profile_data(self, user: User, db: Session) -> Dict[str, Any]:
        """
        Get complete user profile data including role-specific information
        """
        try:
            role_info = self.determine_user_role(user.phone, db)
            
            profile_data = {
                "user": {
                    "id": user.id,
                    "phone": user.phone,
                    "name": user.name,
                    "email": user.email,
                    "address": user.address,
                    "role": user.role,
                    "is_active": user.is_active,
                    "created_at": user.created_at.isoformat()
                },
                "role_info": role_info,
                "display_name": self.get_display_name(user.name, user.role),
                "welcome_message": self.get_welcome_message(user.name, user.role)
            }
            
            return profile_data
            
        except Exception as e:
            print(f"Error getting profile data: {str(e)}")
            return {}
    
    def get_display_name(self, name: str, role: str) -> str:
        """
        Get display name with role prefix
        """
        role_prefixes = {
            "admin": "Admin",
            "fixer": "Fixer", 
            "client": ""
        }
        
        prefix = role_prefixes.get(role, "")
        return f"{prefix} {name}".strip()
    
    def get_welcome_message(self, name: str, role: str) -> str:
        """
        Get personalized welcome message based on role
        """
        if role == "admin":
            return f"Welcome Admin {name}"
        elif role == "fixer":
            return f"Welcome Fixer {name}"
        else:
            return f"Welcome {name}"
    
    def has_permission(self, user_role: str, permission: str) -> bool:
        """
        Check if user role has specific permission
        """
        permissions = self.get_permissions(user_role)
        return permissions.get(permission, False)

# Global instance
role_service = RoleService()