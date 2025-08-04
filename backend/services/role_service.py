from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from models import User, Fixer

class RoleService:
    def __init__(self):
        self.admin_phones = [
            "+27821234567",  # Default admin phone - you can change this
            "+27123456789",  # Additional admin phone
            "+27800000001",  # Test admin phone for comprehensive testing
            "whatsapp:+27800000001",  # Test admin phone with whatsapp prefix
        ]
    
    def determine_user_role(self, phone: str, db: Session) -> Dict[str, Any]:
        """
        Determine user role based on phone number and database records
        Priority: admin (from database) > fixer > client
        """
        try:
            # First check if user exists in database and has admin role
            user = db.query(User).filter(User.phone == phone).first()
            if user and user.role == "admin":
                return {
                    "role": "admin",
                    "is_fixer": False,
                    "fixer_data": None,
                    "permissions": self.get_permissions("admin")
                }
            
            # Check if phone is in legacy admin list (for backward compatibility)
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
                "can_access_compliance": True,
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
                "can_access_compliance": True,
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
                "can_access_compliance": True,
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
    
    def create_or_update_user(self, user_data: dict, db: Session) -> User:
        """
        Create or update user with comprehensive information
        """
        try:
            # Get role information
            role_info = self.determine_user_role(user_data["phone"], db)
            
            # Check if user exists
            user = db.query(User).filter(User.phone == user_data["phone"]).first()
            
            if user:
                # Update existing user
                user.first_name = user_data["first_name"]
                user.last_name = user_data["last_name"]
                user.email = user_data.get("email")
                user.role = role_info["role"]
                user.is_active = True
                # Don't update id_number and town if already set (security measure)
                if not user.id_number:
                    user.id_number = user_data["id_number"]
                if not user.town:
                    user.town = user_data["town"]
            else:
                # Create new user
                user = User(
                    phone=user_data["phone"],
                    first_name=user_data["first_name"],
                    last_name=user_data["last_name"],
                    id_number=user_data["id_number"],
                    town=user_data["town"],
                    email=user_data.get("email"),
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
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "full_name": user.full_name,
                    "display_name": user.display_name,
                    "id_number": user.id_number,
                    "town": user.town,
                    "email": user.email,
                    "address": user.address,
                    "role": user.role,
                    "is_active": user.is_active,
                    "created_at": user.created_at.isoformat()
                },
                "role_info": role_info,
                "display_name": self.get_display_name_with_role(user, role_info["role"]),
                "welcome_message": self.get_welcome_message_with_role(user, role_info["role"])
            }
            
            return profile_data
            
        except Exception as e:
            print(f"Error getting profile data: {str(e)}")
            return {}
    
    def get_display_name_with_role(self, user, dynamic_role: str) -> str:
        """
        Get display name with role prefix using dynamic role (not database role)
        """
        role_prefixes = {
            "admin": "Admin",
            "fixer": "Fixer", 
            "client": ""
        }
        
        prefix = role_prefixes.get(dynamic_role, "")
        first_name = user.first_name if hasattr(user, 'first_name') else user.display_name
        return f"{prefix} {first_name}".strip()
    
    def get_welcome_message_with_role(self, user, dynamic_role: str) -> str:
        """
        Get personalized welcome message based on dynamic role (not database role)
        """
        first_name = user.first_name if hasattr(user, 'first_name') else user.display_name
        
        if dynamic_role == "admin":
            return f"Welcome Admin {first_name}"
        elif dynamic_role == "fixer":
            return f"Welcome Fixer {first_name}"
        else:
            return f"Welcome {first_name}"
    
    def get_display_name(self, user) -> str:
        """
        Get display name with role prefix using first name
        """
        role_prefixes = {
            "admin": "Admin",
            "fixer": "Fixer", 
            "client": ""
        }
        
        prefix = role_prefixes.get(user.role, "")
        first_name = user.first_name if hasattr(user, 'first_name') else user.display_name
        return f"{prefix} {first_name}".strip()
    
    def get_welcome_message(self, user) -> str:
        """
        Get personalized welcome message based on role using first name
        """
        first_name = user.first_name if hasattr(user, 'first_name') else user.display_name
        
        if user.role == "admin":
            return f"Welcome Admin {first_name}"
        elif user.role == "fixer":
            return f"Welcome Fixer {first_name}"
        else:
            return f"Welcome {first_name}"
    
    def has_permission(self, user_role: str, permission: str) -> bool:
        """
        Check if user role has specific permission
        """
        permissions = self.get_permissions(user_role)
        return permissions.get(permission, False)

# Global instance
role_service = RoleService()