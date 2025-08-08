# ANNOUNCEMENT SYSTEM - COMPLETE FILE SET FOR MANUAL DEPLOYMENT

## FILE 1: /app/backend/models.py - ADD TO EXISTING FILE

Add this to the end of your models.py file (after the existing PushSubscription model):

```python
# ======= ANNOUNCEMENT SYSTEM MODELS =======

class Announcement(Base):
    """
    Model for platform announcements that can be targeted to specific user groups
    """
    __tablename__ = "announcements"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Announcement content
    title = Column(String, nullable=False)  # Announcement title
    content = Column(Text, nullable=False)  # Announcement content/message
    
    # Targeting options
    target_audience = Column(String, nullable=False)  # 'clients', 'fixers', 'all'
    
    # Admin information
    created_by = Column(String, ForeignKey("users.id"), nullable=False)  # Admin who created
    
    # Status and visibility
    is_active = Column(Boolean, default=True)  # If announcement is currently active
    is_pinned = Column(Boolean, default=False)  # If announcement should be pinned at top
    priority = Column(String, default="normal")  # 'high', 'normal', 'low'
    
    # Chat settings for this announcement
    chat_enabled = Column(Boolean, default=True)  # If chat/replies are allowed
    admin_only_chat = Column(Boolean, default=False)  # If only admin can respond in chat
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)  # Optional expiration date
    
    # Relationships
    created_by_user = relationship("User", foreign_keys=[created_by])
    chat_messages = relationship("AnnouncementChat", back_populates="announcement", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Announcement(id='{self.id}', title='{self.title}', target='{self.target_audience}')>"

class AnnouncementChat(Base):
    """
    Model for chat messages related to announcements
    """
    __tablename__ = "announcement_chats"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    announcement_id = Column(String, ForeignKey("announcements.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Message content
    message = Column(Text, nullable=False)  # Chat message content
    
    # Message type and context
    message_type = Column(String, default="user")  # 'user', 'admin_response', 'system'
    is_admin_message = Column(Boolean, default=False)  # If message is from admin
    
    # Status
    is_deleted = Column(Boolean, default=False)  # Soft delete for moderation
    is_edited = Column(Boolean, default=False)  # If message was edited
    edited_at = Column(DateTime, nullable=True)  # When message was last edited
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    announcement = relationship("Announcement", back_populates="chat_messages")
    user = relationship("User")
    
    def __repr__(self):
        return f"<AnnouncementChat(id='{self.id}', announcement_id='{self.announcement_id}', user_id='{self.user_id}')>"
```

## FILE 2: /app/backend/server.py - ADD TO IMPORTS

Add `Announcement, AnnouncementChat` to your existing models import:

```python
from models import (
    User, Fixer, Job, Review, FixerPayment, 
    EmergencyAlert, FixerVerification, DataInsight,
    BusinessComplianceRequest, JobDispute, JobPhotoVerification,
    WhatsAppStatistics, FixerApplication, PlatformTerms, UserTermsAcceptance,
    JobAssignmentHistory, JobNotification, FixerAvailability, FixerBehaviorAnalysis,
    PushSubscription, Announcement, AnnouncementChat
)
```

## FILE 3: /app/backend/server.py - ADD API ENDPOINTS

Add this before the final route handlers (before the static file serving):

```python
# ======= ANNOUNCEMENT SYSTEM API ENDPOINTS =======

# Admin Announcement Management Endpoints

@api_router.post("/admin/announcements")
async def create_announcement(
    request: dict,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new platform announcement.
    Admin only endpoint.
    """
    try:
        # Verify admin access
        if current_user.get('role') not in ['admin', 'super_admin']:
            raise HTTPException(status_code=403, detail="Admin access required")
        
        # Validate required fields
        required_fields = ['title', 'content', 'target_audience']
        for field in required_fields:
            if field not in request or not request[field]:
                raise HTTPException(status_code=400, detail=f"{field} is required")
        
        # Validate target_audience
        valid_audiences = ['clients', 'fixers', 'all']
        if request['target_audience'] not in valid_audiences:
            raise HTTPException(status_code=400, detail="target_audience must be one of: clients, fixers, all")
        
        # Create announcement
        announcement = Announcement(
            title=request['title'],
            content=request['content'],
            target_audience=request['target_audience'],
            created_by=current_user['user_id'],
            is_pinned=request.get('is_pinned', False),
            priority=request.get('priority', 'normal'),
            chat_enabled=request.get('chat_enabled', True),
            admin_only_chat=request.get('admin_only_chat', False),
            expires_at=request.get('expires_at')
        )
        
        db.add(announcement)
        db.commit()
        db.refresh(announcement)
        
        return {
            "success": True,
            "message": "Announcement created successfully",
            "announcement_id": announcement.id,
            "announcement": {
                "id": announcement.id,
                "title": announcement.title,
                "content": announcement.content,
                "target_audience": announcement.target_audience,
                "is_active": announcement.is_active,
                "is_pinned": announcement.is_pinned,
                "priority": announcement.priority,
                "chat_enabled": announcement.chat_enabled,
                "admin_only_chat": announcement.admin_only_chat,
                "created_at": announcement.created_at.isoformat(),
                "expires_at": announcement.expires_at.isoformat() if announcement.expires_at else None
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating announcement: {str(e)}")

@api_router.get("/admin/announcements")
async def get_all_announcements(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all announcements for admin management.
    Admin only endpoint.
    """
    try:
        # Verify admin access
        if current_user.get('role') not in ['admin', 'super_admin']:
            raise HTTPException(status_code=403, detail="Admin access required")
        
        # Get all announcements with creator info
        announcements = db.query(Announcement)\
            .join(User, Announcement.created_by == User.id)\
            .order_by(Announcement.is_pinned.desc(), Announcement.created_at.desc())\
            .all()
        
        announcement_list = []
        for ann in announcements:
            # Get chat message count
            chat_count = db.query(AnnouncementChat).filter(
                AnnouncementChat.announcement_id == ann.id,
                AnnouncementChat.is_deleted == False
            ).count()
            
            announcement_list.append({
                "id": ann.id,
                "title": ann.title,
                "content": ann.content,
                "target_audience": ann.target_audience,
                "is_active": ann.is_active,
                "is_pinned": ann.is_pinned,
                "priority": ann.priority,
                "chat_enabled": ann.chat_enabled,
                "admin_only_chat": ann.admin_only_chat,
                "created_at": ann.created_at.isoformat(),
                "updated_at": ann.updated_at.isoformat(),
                "expires_at": ann.expires_at.isoformat() if ann.expires_at else None,
                "created_by_name": ann.created_by_user.full_name,
                "chat_message_count": chat_count
            })
        
        return {
            "success": True,
            "announcements": announcement_list,
            "total_count": len(announcement_list)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching announcements: {str(e)}")

@api_router.get("/announcements")
async def get_announcements_for_user(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get active announcements for the current user based on their role.
    """
    try:
        user_role = current_user.get('role', 'client')
        
        # Build query for announcements
        query = db.query(Announcement).filter(
            Announcement.is_active == True
        )
        
        # Filter by target audience
        if user_role == 'admin' or user_role == 'super_admin':
            # Admins see all announcements
            pass
        elif user_role == 'fixer':
            query = query.filter(Announcement.target_audience.in_(['fixers', 'all']))
        else:  # client
            query = query.filter(Announcement.target_audience.in_(['clients', 'all']))
        
        # Check for unexpired announcements
        current_time = datetime.utcnow()
        query = query.filter(
            (Announcement.expires_at.is_(None)) | (Announcement.expires_at > current_time)
        )
        
        # Order by pinned first, then by creation date
        announcements = query.order_by(
            Announcement.is_pinned.desc(),
            Announcement.priority.desc(),
            Announcement.created_at.desc()
        ).all()
        
        announcement_list = []
        for ann in announcements:
            # Get chat message count
            chat_count = db.query(AnnouncementChat).filter(
                AnnouncementChat.announcement_id == ann.id,
                AnnouncementChat.is_deleted == False
            ).count()
            
            # Get recent chat messages (last 3)
            recent_chats = db.query(AnnouncementChat)\
                .filter(
                    AnnouncementChat.announcement_id == ann.id,
                    AnnouncementChat.is_deleted == False
                )\
                .join(User, AnnouncementChat.user_id == User.id)\
                .order_by(AnnouncementChat.created_at.desc())\
                .limit(3).all()
            
            recent_chat_list = []
            for chat in recent_chats:
                recent_chat_list.append({
                    "id": chat.id,
                    "message": chat.message,
                    "user_name": chat.user.first_name,
                    "is_admin": chat.is_admin_message,
                    "created_at": chat.created_at.isoformat()
                })
            
            announcement_list.append({
                "id": ann.id,
                "title": ann.title,
                "content": ann.content,
                "target_audience": ann.target_audience,
                "is_pinned": ann.is_pinned,
                "priority": ann.priority,
                "chat_enabled": ann.chat_enabled,
                "admin_only_chat": ann.admin_only_chat,
                "created_at": ann.created_at.isoformat(),
                "expires_at": ann.expires_at.isoformat() if ann.expires_at else None,
                "chat_message_count": chat_count,
                "recent_chats": recent_chat_list
            })
        
        return {
            "success": True,
            "announcements": announcement_list,
            "user_role": user_role
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching announcements: {str(e)}")

@api_router.get("/announcements/{announcement_id}/chat")
async def get_announcement_chat(
    announcement_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = Query(default=0, description="Number of messages to skip"),
    limit: int = Query(default=50, description="Number of messages to retrieve")
):
    """
    Get chat messages for an announcement.
    """
    try:
        # Check if announcement exists and user can access it
        announcement = db.query(Announcement).filter(Announcement.id == announcement_id).first()
        if not announcement:
            raise HTTPException(status_code=404, detail="Announcement not found")
        
        # Check if user can access this announcement
        user_role = current_user.get('role', 'client')
        if user_role not in ['admin', 'super_admin']:
            if announcement.target_audience not in ['all']:
                if (user_role == 'client' and announcement.target_audience != 'clients') or \
                   (user_role == 'fixer' and announcement.target_audience != 'fixers'):
                    raise HTTPException(status_code=403, detail="Access denied to this announcement")
        
        # Get chat messages
        chat_messages = db.query(AnnouncementChat)\
            .filter(
                AnnouncementChat.announcement_id == announcement_id,
                AnnouncementChat.is_deleted == False
            )\
            .join(User, AnnouncementChat.user_id == User.id)\
            .order_by(AnnouncementChat.created_at.asc())\
            .offset(skip).limit(limit).all()
        
        message_list = []
        for chat in chat_messages:
            message_list.append({
                "id": chat.id,
                "message": chat.message,
                "message_type": chat.message_type,
                "is_admin_message": chat.is_admin_message,
                "user_id": chat.user_id,
                "user_name": chat.user.first_name,
                "user_role": chat.user.role,
                "is_edited": chat.is_edited,
                "edited_at": chat.edited_at.isoformat() if chat.edited_at else None,
                "created_at": chat.created_at.isoformat()
            })
        
        return {
            "success": True,
            "announcement": {
                "id": announcement.id,
                "title": announcement.title,
                "chat_enabled": announcement.chat_enabled,
                "admin_only_chat": announcement.admin_only_chat
            },
            "messages": message_list,
            "total_messages": len(message_list),
            "can_post": announcement.chat_enabled and (
                not announcement.admin_only_chat or user_role in ['admin', 'super_admin']
            )
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching chat messages: {str(e)}")

@api_router.post("/announcements/{announcement_id}/chat")
async def post_chat_message(
    announcement_id: str,
    request: dict,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Post a chat message to an announcement.
    """
    try:
        # Validate message
        if 'message' not in request or not request['message'].strip():
            raise HTTPException(status_code=400, detail="Message is required")
        
        # Check if announcement exists
        announcement = db.query(Announcement).filter(Announcement.id == announcement_id).first()
        if not announcement:
            raise HTTPException(status_code=404, detail="Announcement not found")
        
        # Check if chat is enabled
        if not announcement.chat_enabled:
            raise HTTPException(status_code=403, detail="Chat is disabled for this announcement")
        
        # Check permissions
        user_role = current_user.get('role', 'client')
        
        # Check if user can access this announcement
        if user_role not in ['admin', 'super_admin']:
            if announcement.target_audience not in ['all']:
                if (user_role == 'client' and announcement.target_audience != 'clients') or \
                   (user_role == 'fixer' and announcement.target_audience != 'fixers'):
                    raise HTTPException(status_code=403, detail="Access denied to this announcement")
        
        # Check if only admin can post
        if announcement.admin_only_chat and user_role not in ['admin', 'super_admin']:
            raise HTTPException(status_code=403, detail="Only admin can post messages to this announcement")
        
        # Create chat message
        chat_message = AnnouncementChat(
            announcement_id=announcement_id,
            user_id=current_user['user_id'],
            message=request['message'].strip(),
            message_type='admin_response' if user_role in ['admin', 'super_admin'] else 'user',
            is_admin_message=user_role in ['admin', 'super_admin']
        )
        
        db.add(chat_message)
        db.commit()
        db.refresh(chat_message)
        
        # Get user info for response
        user = db.query(User).filter(User.id == current_user['user_id']).first()
        
        return {
            "success": True,
            "message": "Chat message posted successfully",
            "chat_message": {
                "id": chat_message.id,
                "message": chat_message.message,
                "message_type": chat_message.message_type,
                "is_admin_message": chat_message.is_admin_message,
                "user_name": user.first_name if user else "Unknown",
                "created_at": chat_message.created_at.isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error posting chat message: {str(e)}")

# ======= END ANNOUNCEMENT SYSTEM ENDPOINTS =======
```

## FILES TO CREATE:

1. Create: `/app/frontend/src/components/Admin/AnnouncementManagement.js`
2. Create: `/app/frontend/src/components/Common/AnnouncementDisplay.js`
3. Update: `/app/frontend/src/components/Admin/AdminDashboard.js`
4. Update: `/app/frontend/src/components/Dashboard/Dashboard.js`
5. Update: `/app/frontend/src/services/api.js`

## DEPLOYMENT STEPS:

1. Add all the above changes to your files
2. Run: `python /app/backend/create_announcement_tables.py` (already done)
3. Commit: `git add . && git commit -m "Add announcement system"`
4. Deploy to Heroku with your normal deployment process

The announcement system will then be live!