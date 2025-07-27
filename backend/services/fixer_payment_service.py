from sqlalchemy import Column, String, DateTime, Float, Boolean, ForeignKey, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
import uuid

Base = declarative_base()

class FixerPayment(Base):
    __tablename__ = "fixer_payments"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    fixer_id = Column(String, ForeignKey("fixers.id"), nullable=False)
    job_id = Column(String, ForeignKey("jobs.id"), nullable=False)
    amount = Column(Float, nullable=False, default=20.0)  # R20 per completed job
    payment_type = Column(String, nullable=False, default="service_fee")  # service_fee, fine, bonus
    due_date = Column(DateTime, nullable=False)
    paid_date = Column(DateTime, nullable=True)
    status = Column(String, nullable=False, default="pending")  # pending, paid, overdue
    payment_method = Column(String, nullable=True)  # eft, airtime, cash, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class FixerBalance(Base):
    __tablename__ = "fixer_balances"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    fixer_id = Column(String, ForeignKey("fixers.id"), nullable=False, unique=True)
    current_balance = Column(Float, nullable=False, default=0.0)  # Negative = owes money
    total_earned = Column(Float, nullable=False, default=0.0)
    total_fees_paid = Column(Float, nullable=False, default=0.0)
    jobs_completed = Column(Integer, nullable=False, default=0)
    last_payment_date = Column(DateTime, nullable=True)
    is_blocked = Column(Boolean, nullable=False, default=False)  # Blocked from getting jobs
    blocked_reason = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class FixerPaymentService:
    def __init__(self, db_session):
        self.db = db_session
        
    def create_service_fee(self, fixer_id: str, job_id: str, amount: float = 20.0):
        """
        Create a service fee when a job is completed.
        """
        # Set due date to 7 days from now
        due_date = datetime.utcnow() + timedelta(days=7)
        
        payment = FixerPayment(
            fixer_id=fixer_id,
            job_id=job_id,
            amount=amount,
            payment_type="service_fee",
            due_date=due_date,
            status="pending"
        )
        
        self.db.add(payment)
        self.db.commit()
        
        # Update fixer balance
        self._update_fixer_balance(fixer_id, -amount)
        
        return payment
    
    def record_payment(self, payment_id: str, payment_method: str):
        """
        Record a payment as paid.
        """
        payment = self.db.query(FixerPayment).filter(FixerPayment.id == payment_id).first()
        
        if payment:
            payment.paid_date = datetime.utcnow()
            payment.status = "paid"
            payment.payment_method = payment_method
            
            # Update fixer balance
            self._update_fixer_balance(payment.fixer_id, payment.amount)
            
            self.db.commit()
            
            # Check if fixer can be unblocked
            self._check_and_unblock_fixer(payment.fixer_id)
            
            return payment
        
        return None
    
    def check_fixer_eligibility(self, fixer_id: str) -> dict:
        """
        Check if a fixer is eligible for new jobs.
        """
        balance = self.db.query(FixerBalance).filter(FixerBalance.fixer_id == fixer_id).first()
        
        if not balance:
            # Create new balance record
            balance = FixerBalance(fixer_id=fixer_id)
            self.db.add(balance)
            self.db.commit()
            
        # Check for overdue payments
        overdue_payments = self.db.query(FixerPayment).filter(
            FixerPayment.fixer_id == fixer_id,
            FixerPayment.status == "pending",
            FixerPayment.due_date < datetime.utcnow()
        ).all()
        
        if overdue_payments:
            # Mark as overdue
            for payment in overdue_payments:
                payment.status = "overdue"
            
            # Block fixer
            balance.is_blocked = True
            balance.blocked_reason = f"Outstanding payment of R{sum(p.amount for p in overdue_payments):.2f}"
            
            self.db.commit()
        
        return {
            "eligible": not balance.is_blocked,
            "current_balance": balance.current_balance,
            "blocked_reason": balance.blocked_reason if balance.is_blocked else None,
            "overdue_payments": len(overdue_payments)
        }
    
    def get_fixer_payment_history(self, fixer_id: str, limit: int = 50):
        """
        Get payment history for a fixer.
        """
        payments = self.db.query(FixerPayment).filter(
            FixerPayment.fixer_id == fixer_id
        ).order_by(FixerPayment.created_at.desc()).limit(limit).all()
        
        return payments
    
    def get_pending_payments(self, fixer_id: str):
        """
        Get all pending payments for a fixer.
        """
        payments = self.db.query(FixerPayment).filter(
            FixerPayment.fixer_id == fixer_id,
            FixerPayment.status.in_(["pending", "overdue"])
        ).order_by(FixerPayment.due_date.asc()).all()
        
        return payments
    
    def get_payment_summary(self, fixer_id: str):
        """
        Get payment summary for a fixer.
        """
        balance = self.db.query(FixerBalance).filter(FixerBalance.fixer_id == fixer_id).first()
        
        if not balance:
            return {
                "current_balance": 0.0,
                "total_earned": 0.0,
                "total_fees_paid": 0.0,
                "jobs_completed": 0,
                "pending_amount": 0.0,
                "is_blocked": False
            }
        
        pending_amount = sum(
            payment.amount for payment in 
            self.db.query(FixerPayment).filter(
                FixerPayment.fixer_id == fixer_id,
                FixerPayment.status.in_(["pending", "overdue"])
            ).all()
        )
        
        return {
            "current_balance": balance.current_balance,
            "total_earned": balance.total_earned,
            "total_fees_paid": balance.total_fees_paid,
            "jobs_completed": balance.jobs_completed,
            "pending_amount": pending_amount,
            "is_blocked": balance.is_blocked,
            "blocked_reason": balance.blocked_reason
        }
    
    def process_bulk_payment(self, fixer_id: str, amount: float, payment_method: str):
        """
        Process bulk payment for multiple pending payments.
        """
        pending_payments = self.get_pending_payments(fixer_id)
        
        remaining_amount = amount
        processed_payments = []
        
        for payment in pending_payments:
            if remaining_amount >= payment.amount:
                # Full payment
                self.record_payment(payment.id, payment_method)
                remaining_amount -= payment.amount
                processed_payments.append(payment)
            else:
                # Partial payment - not supported for now
                break
        
        return {
            "processed_payments": processed_payments,
            "remaining_amount": remaining_amount,
            "total_processed": len(processed_payments)
        }
    
    def _update_fixer_balance(self, fixer_id: str, amount: float):
        """
        Update fixer balance.
        """
        balance = self.db.query(FixerBalance).filter(FixerBalance.fixer_id == fixer_id).first()
        
        if not balance:
            balance = FixerBalance(fixer_id=fixer_id)
            self.db.add(balance)
        
        balance.current_balance += amount
        
        if amount > 0:
            balance.total_fees_paid += amount
        
        balance.updated_at = datetime.utcnow()
        
        self.db.commit()
    
    def _check_and_unblock_fixer(self, fixer_id: str):
        """
        Check if fixer can be unblocked after payment.
        """
        pending_payments = self.get_pending_payments(fixer_id)
        
        if not pending_payments:
            # No pending payments, unblock fixer
            balance = self.db.query(FixerBalance).filter(FixerBalance.fixer_id == fixer_id).first()
            if balance:
                balance.is_blocked = False
                balance.blocked_reason = None
                balance.last_payment_date = datetime.utcnow()
                self.db.commit()
    
    def get_system_payment_stats(self):
        """
        Get system-wide payment statistics.
        """
        total_pending = self.db.query(FixerPayment).filter(
            FixerPayment.status == "pending"
        ).count()
        
        total_overdue = self.db.query(FixerPayment).filter(
            FixerPayment.status == "overdue"
        ).count()
        
        blocked_fixers = self.db.query(FixerBalance).filter(
            FixerBalance.is_blocked == True
        ).count()
        
        total_revenue = self.db.query(FixerPayment).filter(
            FixerPayment.status == "paid"
        ).with_entities(FixerPayment.amount).all()
        
        total_revenue_amount = sum(payment.amount for payment in total_revenue)
        
        return {
            "total_pending_payments": total_pending,
            "total_overdue_payments": total_overdue,
            "blocked_fixers": blocked_fixers,
            "total_revenue": total_revenue_amount,
            "average_fee": 20.0
        }
    
    def generate_payment_reminder(self, fixer_id: str):
        """
        Generate payment reminder message.
        """
        pending_payments = self.get_pending_payments(fixer_id)
        
        if not pending_payments:
            return None
        
        total_amount = sum(payment.amount for payment in pending_payments)
        overdue_count = sum(1 for payment in pending_payments if payment.status == "overdue")
        
        if overdue_count > 0:
            message = f"URGENT: You have {overdue_count} overdue payment(s) totaling R{total_amount:.2f}. " \
                     f"Pay now to continue receiving jobs. Visit the app to pay."
        else:
            due_soon = [p for p in pending_payments if (p.due_date - datetime.utcnow()).days <= 3]
            if due_soon:
                message = f"Reminder: R{total_amount:.2f} due soon. Pay before {due_soon[0].due_date.strftime('%Y-%m-%d')} " \
                         f"to avoid service interruption."
            else:
                message = f"You have R{total_amount:.2f} in pending payments. Visit the app to pay."
        
        return message

    def mark_job_completed_and_create_fee(self, job_id: str, fixer_id: str):
        """
        Mark job as completed and create service fee.
        """
        # Create service fee
        fee = self.create_service_fee(fixer_id, job_id)
        
        # Update fixer balance
        balance = self.db.query(FixerBalance).filter(FixerBalance.fixer_id == fixer_id).first()
        if balance:
            balance.jobs_completed += 1
        
        self.db.commit()
        
        return fee