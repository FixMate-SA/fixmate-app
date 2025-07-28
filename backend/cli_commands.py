#!/usr/bin/env python3
"""
FixMate-SA CLI Commands
Admin commands for managing users, fixers, jobs, and system data.
"""

import click
import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from database import get_db
from models import User, Fixer, Job, Review, DataInsight
from services.whatsapp_service import whatsapp_service
from services.ai_service import ai_service
from services.conversation_service import conversation_service
from sqlalchemy.orm import Session

# Get database session
db = next(get_db())

@click.group()
def cli():
    """FixMate-SA Admin Command Line Interface"""
    pass

def format_phone_number(phone: str) -> str:
    """Format phone number to WhatsApp format."""
    if phone.startswith('0') and len(phone) == 10:
        return f"whatsapp:+27{phone[1:]}"
    elif phone.startswith('+') and len(phone) == 12:
        return f"whatsapp:{phone}"
    else:
        raise ValueError("Invalid phone number format. Use 10-digit (0821234567) or international (+27821234567) format.")

@cli.command("add-fixer")
@click.argument("name")
@click.argument("phone")
@click.argument("skills")
def add_fixer(name, phone, skills):
    """Add a new fixer to the system."""
    try:
        formatted_phone = format_phone_number(phone)
        
        # Check if fixer already exists
        existing_fixer = db.query(Fixer).filter(Fixer.phone == formatted_phone).first()
        if existing_fixer:
            click.echo(f"Error: Fixer with phone number {formatted_phone} already exists.")
            return
        
        # Create or get user
        user = db.query(User).filter(User.phone == formatted_phone).first()
        if not user:
            user = User(
                phone=formatted_phone,
                first_name=name.split()[0] if name.split() else name,
                last_name=" ".join(name.split()[1:]) if len(name.split()) > 1 else "User",
                id_number="",
                town="Unknown",
                role="fixer"
            )
            db.add(user)
            db.commit()
        
        # Create fixer
        fixer = Fixer(
            user_id=user.id,
            phone=formatted_phone,
            name=name,
            services=skills,
            location="Unknown",
            skills=skills,
            is_active=True,
            is_approved=True,
            vetting_status="approved"
        )
        
        db.add(fixer)
        db.commit()
        
        click.echo(f"Successfully added fixer: '{name}' with number {formatted_phone}")
        
    except ValueError as e:
        click.echo(f"Error: {e}")
    except Exception as e:
        click.echo(f"Error adding fixer: {e}")

@cli.command("promote-admin")
@click.argument("phone")
def promote_admin(phone):
    """Promote a user to admin status."""
    try:
        if not (phone.startswith('0') and len(phone) == 10):
            click.echo("Error: Please provide a valid 10-digit SA number (e.g., 0821234567).")
            return
        
        formatted_phone = format_phone_number(phone)
        
        user = db.query(User).filter(User.phone == formatted_phone).first()
        if not user:
            click.echo(f"User not found. Creating new admin user for {formatted_phone}...")
            user = User(
                phone=formatted_phone,
                first_name="Admin",
                last_name="User",
                id_number="",
                town="Unknown",
                role="admin"
            )
            db.add(user)
            db.commit()
            click.echo(f"Successfully created and promoted new admin: {user.phone}")
        else:
            user.role = "admin"
            db.commit()
            click.echo(f"Successfully promoted existing user '{user.full_name}' to admin.")
            
    except Exception as e:
        click.echo(f"Error promoting admin: {e}")

@cli.command("demote-admin")
@click.argument("phone")
def demote_admin(phone):
    """Demote an admin to regular client status."""
    try:
        if not (phone.startswith('0') and len(phone) == 10):
            click.echo("Error: Please provide a valid 10-digit SA number (e.g., 0821234567).")
            return
        
        formatted_phone = format_phone_number(phone)
        
        user = db.query(User).filter(User.phone == formatted_phone).first()
        if not user:
            click.echo(f"Error: User with phone number {formatted_phone} not found.")
            return
        
        user.role = "client"
        db.commit()
        click.echo(f"Successfully demoted '{user.full_name}'. They are now a regular client.")
        
    except Exception as e:
        click.echo(f"Error demoting admin: {e}")

@cli.command("remove-fixer")
@click.argument("phone")
def remove_fixer(phone):
    """Remove a fixer from the system."""
    try:
        formatted_phone = format_phone_number(phone)
        
        fixer = db.query(Fixer).filter(Fixer.phone == formatted_phone).first()
        if not fixer:
            click.echo(f"Error: Fixer with phone number {formatted_phone} not found.")
            return
        
        if click.confirm(f"Are you sure you want to delete fixer '{fixer.name}' ({fixer.phone})? This cannot be undone."):
            db.delete(fixer)
            db.commit()
            click.echo(f"Successfully deleted fixer: {fixer.name}")
            
    except Exception as e:
        click.echo(f"Error removing fixer: {e}")

@cli.command("remove-client")
@click.argument("phone")
def remove_client(phone):
    """Remove a client from the system."""
    try:
        formatted_phone = format_phone_number(phone)
        
        user = db.query(User).filter(User.phone == formatted_phone).first()
        if not user:
            click.echo(f"Error: Client with phone number {formatted_phone} not found.")
            return
        
        if click.confirm(f"Are you sure you want to delete client '{user.full_name}'? This cannot be undone."):
            db.delete(user)
            db.commit()
            click.echo(f"Successfully deleted client: {user.full_name}")
            
    except Exception as e:
        click.echo(f"Error removing client: {e}")

@cli.command("analyze-data")
def analyze_data():
    """Analyze job data and generate business insights."""
    try:
        click.echo("Starting data analysis...")
        
        # Get completed jobs
        completed_jobs = db.query(Job).filter(Job.status == 'completed').all()
        
        if not completed_jobs:
            click.echo("No completed jobs found for analysis.")
            return
        
        # Prepare job data for AI analysis
        job_data = [
            {
                "description": job.description,
                "area": job.area,
                "service": job.service,
                "rating": job.rating
            }
            for job in completed_jobs
        ]
        
        # Generate insight using AI
        insight_text = ai_service.generate_business_insight(job_data)
        
        # Save insight to database
        insight = DataInsight(
            insight_text=insight_text,
            insight_type="business",
            generated_by="cli"
        )
        
        db.add(insight)
        db.commit()
        
        click.echo(f"Insight & Action: {insight_text}")
        
    except Exception as e:
        click.echo(f"Error analyzing data: {e}")

@cli.command("stats")
def stats():
    """Display system statistics."""
    try:
        user_count = db.query(User).count()
        fixer_count = db.query(Fixer).count()
        job_count = db.query(Job).count()
        completed_jobs = db.query(Job).filter(Job.status == 'completed').count()
        
        click.echo("--- FixMate-SA System Statistics ---")
        click.echo(f"Total Registered Users: {user_count}")
        click.echo(f"Total Registered Fixers: {fixer_count}")
        click.echo(f"Total Jobs: {job_count}")
        click.echo(f"Completed Jobs: {completed_jobs}")
        click.echo("------------------------------------")
        
    except Exception as e:
        click.echo(f"Error getting statistics: {e}")

@cli.command("list-admins")
def list_admins():
    """List all administrators."""
    try:
        admins = db.query(User).filter(User.role == "admin").all()
        
        if not admins:
            click.echo("No administrators found.")
            return
        
        click.echo("--- Current Administrators ---")
        for admin in admins:
            click.echo(f"- {admin.full_name} ({admin.phone})")
        click.echo("----------------------------")
        
    except Exception as e:
        click.echo(f"Error listing admins: {e}")

@cli.command("toggle-fixer-active")
@click.argument("phone")
def toggle_fixer_active(phone):
    """Toggle fixer active status."""
    try:
        formatted_phone = format_phone_number(phone)
        
        fixer = db.query(Fixer).filter(Fixer.phone == formatted_phone).first()
        if not fixer:
            click.echo(f"Error: Fixer with phone number {formatted_phone} not found.")
            return
        
        fixer.is_active = not fixer.is_active
        db.commit()
        
        status = "ACTIVE" if fixer.is_active else "INACTIVE"
        click.echo(f"Successfully set fixer '{fixer.name}' to {status}.")
        
    except Exception as e:
        click.echo(f"Error toggling fixer status: {e}")

@cli.command("list-jobs")
@click.option('--status', default=None, help='Filter jobs by status (e.g., pending, assigned, completed).')
@click.option('--limit', default=20, help='Number of jobs to display.')
def list_jobs(status, limit):
    """List jobs with optional status filter."""
    try:
        query = db.query(Job)
        
        if status:
            query = query.filter(Job.status == status)
        
        jobs = query.order_by(Job.created_at.desc()).limit(limit).all()
        
        if not jobs:
            click.echo(f"No jobs found" + (f" with status '{status}'." if status else "."))
            return
        
        click.echo(f"--- Jobs" + (f" with status: {status}" if status else "") + " ---")
        for job in jobs:
            client_name = job.user.full_name if job.user else "Unknown"
            fixer_name = job.fixer.name if job.fixer else "N/A"
            click.echo(f"ID: {job.id[:8]}... | Status: {job.status} | Client: {client_name} | Fixer: {fixer_name} | Desc: {job.description[:30]}...")
        click.echo("--------------------")
        
    except Exception as e:
        click.echo(f"Error listing jobs: {e}")

@cli.command("reassign-job")
@click.argument("job_id")
@click.argument("fixer_phone")
def reassign_job(job_id, fixer_phone):
    """Reassign a job to a different fixer."""
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            click.echo(f"Error: Job with ID {job_id} not found.")
            return
        
        formatted_phone = format_phone_number(fixer_phone)
        
        new_fixer = db.query(Fixer).filter(Fixer.phone == formatted_phone).first()
        if not new_fixer:
            click.echo(f"Error: Fixer with phone number {formatted_phone} not found.")
            return
        
        if new_fixer.vetting_status != 'approved':
            click.echo(f"Error: Fixer '{new_fixer.name}' is not approved and cannot be assigned jobs.")
            return
        
        old_fixer_name = job.fixer.name if job.fixer else "None"
        job.fixer_id = new_fixer.id
        job.status = 'assigned'
        db.commit()
        
        click.echo(f"Success! Job #{job_id[:8]}... has been reassigned from {old_fixer_name} to {new_fixer.name}.")
        
        # Send WhatsApp notification
        job_data = {
            'id': job.id,
            'description': job.description,
            'area': job.area,
            'client_contact': job.client_contact_number
        }
        whatsapp_service.send_job_notification(new_fixer.phone, job_data)
        
    except Exception as e:
        click.echo(f"Error reassigning job: {e}")

@cli.command("remove-all-clients")
def remove_all_clients():
    """Remove all non-admin clients and their associated jobs."""
    try:
        clients_to_delete = db.query(User).filter(User.role == "client").all()
        
        if not clients_to_delete:
            click.echo("There are no non-admin clients to remove.")
            return
        
        client_count = len(clients_to_delete)
        
        if click.confirm(
            f"Are you sure you want to delete {client_count} client(s)? "
            "This will also delete all of their associated jobs and cannot be undone."
        ):
            for client in clients_to_delete:
                db.delete(client)
            
            db.commit()
            click.echo(f"Successfully deleted {client_count} client(s).")
            
    except Exception as e:
        click.echo(f"Error removing clients: {e}")

@cli.command("send-whatsapp")
@click.argument("phone")
@click.argument("message")
def send_whatsapp(phone, message):
    """Send a WhatsApp message to a user."""
    try:
        formatted_phone = format_phone_number(phone)
        
        success = whatsapp_service.send_whatsapp_message(formatted_phone, message)
        
        if success:
            click.echo(f"WhatsApp message sent successfully to {formatted_phone}")
        else:
            click.echo(f"Failed to send WhatsApp message to {formatted_phone}")
            
    except Exception as e:
        click.echo(f"Error sending WhatsApp message: {e}")

@cli.command("generate-insight")
def generate_insight():
    """Generate and display a new business insight."""
    try:
        # Get completed jobs
        completed_jobs = db.query(Job).filter(Job.status == 'completed').limit(100).all()
        
        if not completed_jobs:
            click.echo("No completed jobs found for insight generation.")
            return
        
        # Prepare job data
        job_data = [
            {
                "description": job.description,
                "area": job.area,
                "service": job.service,
                "rating": job.rating
            }
            for job in completed_jobs
        ]
        
        # Generate insight
        insight_text = ai_service.generate_business_insight(job_data)
        
        # Save to database
        insight = DataInsight(
            insight_text=insight_text,
            insight_type="business",
            generated_by="cli"
        )
        
        db.add(insight)
        db.commit()
        
        click.echo("--- Generated Business Insight ---")
        click.echo(insight_text)
        click.echo("----------------------------------")
        
    except Exception as e:
        click.echo(f"Error generating insight: {e}")

@cli.command("list-insights")
@click.option('--limit', default=10, help='Number of insights to display.')
def list_insights(limit):
    """List recent business insights."""
    try:
        insights = db.query(DataInsight).order_by(DataInsight.created_at.desc()).limit(limit).all()
        
        if not insights:
            click.echo("No insights found.")
            return
        
        click.echo("--- Recent Business Insights ---")
        for insight in insights:
            click.echo(f"[{insight.created_at.strftime('%Y-%m-%d %H:%M')}] {insight.insight_text}")
            click.echo("-" * 50)
        
    except Exception as e:
        click.echo(f"Error listing insights: {e}")

@cli.command("backup-data")
@click.argument("output_file")
def backup_data(output_file):
    """Create a backup of system data."""
    try:
        import json
        
        # Get all data
        users = db.query(User).all()
        fixers = db.query(Fixer).all()
        jobs = db.query(Job).all()
        
        backup_data = {
            "users": [
                {
                    "id": user.id,
                    "phone": user.phone,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "role": user.role,
                    "created_at": user.created_at.isoformat()
                }
                for user in users
            ],
            "fixers": [
                {
                    "id": fixer.id,
                    "phone": fixer.phone,
                    "name": fixer.name,
                    "services": fixer.services,
                    "is_active": fixer.is_active,
                    "created_at": fixer.created_at.isoformat()
                }
                for fixer in fixers
            ],
            "jobs": [
                {
                    "id": job.id,
                    "description": job.description,
                    "status": job.status,
                    "service": job.service,
                    "created_at": job.created_at.isoformat()
                }
                for job in jobs
            ]
        }
        
        with open(output_file, 'w') as f:
            json.dump(backup_data, f, indent=2)
        
        click.echo(f"Backup created successfully: {output_file}")
        
    except Exception as e:
        click.echo(f"Error creating backup: {e}")

if __name__ == "__main__":
    cli()