#!/usr/bin/env python3
"""
Job Manager Module

Handles G-code job management, including file upload, job control, and status tracking.
"""

import os
import time
import json
import logging
import threading
import uuid
from typing import Dict, List, Optional, Any, BinaryIO
from datetime import datetime
from flask import current_app
from werkzeug.utils import secure_filename

logger = logging.getLogger(__name__)

class Job:
    """Represents a G-code job."""
    
    def __init__(self, job_id: str, filename: str, file_path: str):
        """
        Initialize a job.
        
        Args:
            job_id: Unique job ID
            filename: Original filename
            file_path: Path to the G-code file
        """
        self.job_id = job_id
        self.filename = filename
        self.file_path = file_path
        self.status = "ready"  # ready, running, paused, completed, failed
        self.progress = 0.0
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.current_line = 0
        self.total_lines = 0
        self.error: Optional[str] = None
        
        # Count lines in the file
        try:
            with open(file_path, 'r') as f:
                self.total_lines = sum(1 for _ in f)
        except Exception as e:
            logger.error(f"Error counting lines in file: {e}")
            self.total_lines = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert job to dictionary.
        
        Returns:
            dict: Job data
        """
        # Get file size if file exists
        file_size = 0
        if os.path.exists(self.file_path):
            file_size = os.path.getsize(self.file_path)
            
        return {
            "job_id": self.job_id,
            "filename": self.filename,
            "status": self.status,
            "progress": self.progress,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "current_line": self.current_line,
            "total_lines": self.total_lines,
            "error": self.error,
            "size": file_size,
            "upload_date": os.path.getctime(self.file_path) if os.path.exists(self.file_path) else None,
            "duration": round(time.time() - (self.start_time or time.time())) if self.start_time and not self.end_time else None,
            "completed_duration": round((self.end_time or 0) - (self.start_time or 0)) if self.start_time and self.end_time else None
        }

class JobManager:
    """Manages G-code jobs."""
    
    def __init__(self, upload_folder: str, duet_client):
        """
        Initialize the job manager.
        
        Args:
            upload_folder: Folder for storing uploaded files
            duet_client: Duet client instance
        """
        self.upload_folder = upload_folder
        self.duet_client = duet_client
        self.jobs: Dict[str, Job] = {}
        self.current_job: Optional[Job] = None
        self.job_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        
        # Create upload folder if it doesn't exist
        os.makedirs(self.upload_folder, exist_ok=True)
        
        # Load existing jobs from upload folder
        self._load_existing_jobs()
    
    def _load_existing_jobs(self) -> None:
        """Load existing jobs from the upload folder."""
        try:
            for filename in os.listdir(self.upload_folder):
                if filename.endswith('.gcode'):
                    job_id = str(uuid.uuid4())
                    file_path = os.path.join(self.upload_folder, filename)
                    job = Job(job_id, filename, file_path)
                    self.jobs[job_id] = job
            
            logger.info(f"Loaded {len(self.jobs)} existing jobs")
        except Exception as e:
            logger.error(f"Error loading existing jobs: {e}")
    
    def list_files(self) -> List[Dict[str, Any]]:
        """
        List available G-code files.
        
        Returns:
            list: List of files with metadata
        """
        file_list = []
        for job_id, job in self.jobs.items():
            job_dict = job.to_dict()
            job_dict["id"] = job_id  # Add job_id as id for frontend compatibility
            file_list.append(job_dict)
        return file_list
    
    def upload_file(self, file: BinaryIO) -> Dict[str, Any]:
        """
        Upload a G-code file.
        
        Args:
            file: File object from request
            
        Returns:
            dict: Response with status and job ID
        """
        try:
            filename = secure_filename(file.filename)
            job_id = str(uuid.uuid4())
            file_path = os.path.join(self.upload_folder, filename)
            
            # Save file
            file.save(file_path)
            
            # Create job
            job = Job(job_id, filename, file_path)
            self.jobs[job_id] = job
            
            logger.info(f"Uploaded file {filename} as job {job_id}")
            return {
                "status": "success",
                "job_id": job_id,
                "filename": filename,
                "message": f"File {filename} uploaded successfully"
            }
        
        except Exception as e:
            logger.error(f"Error uploading file: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_job(self, job_id: str) -> Optional[Job]:
        """
        Get a job by ID.
        
        Args:
            job_id: Job ID
            
        Returns:
            Job: Job instance or None if not found
        """
        return self.jobs.get(job_id)
    
    def delete_job(self, job_id: str) -> Dict[str, Any]:
        """
        Delete a job.
        
        Args:
            job_id: Job ID
            
        Returns:
            dict: Response with status and message
        """
        job = self.get_job(job_id)
        if not job:
            return {"status": "error", "message": f"Job {job_id} not found"}
        
        if job.status == "running":
            return {"status": "error", "message": "Cannot delete a running job"}
        
        try:
            # Remove file
            if os.path.exists(job.file_path):
                os.remove(job.file_path)
            
            # Remove job
            del self.jobs[job_id]
            
            logger.info(f"Deleted job {job_id}")
            return {"status": "success", "message": f"Job {job_id} deleted"}
        
        except Exception as e:
            logger.error(f"Error deleting job {job_id}: {e}")
            return {"status": "error", "message": str(e)}
    
    def start_job(self, job_id: str) -> Dict[str, Any]:
        """
        Start a job.
        
        Args:
            job_id: Job ID
            
        Returns:
            dict: Response with status and message
        """
        job = self.get_job(job_id)
        if not job:
            return {"status": "error", "message": f"Job {job_id} not found"}
        
        if self.current_job and self.current_job.status == "running":
            return {"status": "error", "message": "Another job is already running"}
        
        # Reset job state
        job.status = "running"
        job.progress = 0.0
        job.start_time = time.time()
        job.end_time = None
        job.current_line = 0
        job.error = None
        
        self.current_job = job
        
        # Start job thread
        self.stop_event.clear()
        self.job_thread = threading.Thread(target=self._run_job, args=(job,))
        self.job_thread.daemon = True
        self.job_thread.start()
        
        logger.info(f"Started job {job_id}")
        return {"status": "success", "message": f"Job {job_id} started"}
    
    def pause_job(self) -> Dict[str, Any]:
        """
        Pause the current job.
        
        Returns:
            dict: Response with status and message
        """
        if not self.current_job or self.current_job.status != "running":
            return {"status": "error", "message": "No job is running"}
        
        # Send pause command to Duet
        result = self.duet_client.send_command("M25")
        
        if result.get("status") == "success":
            self.current_job.status = "paused"
            logger.info(f"Paused job {self.current_job.job_id}")
            return {"status": "success", "message": "Job paused"}
        else:
            logger.error(f"Failed to pause job: {result.get('message')}")
            return {"status": "error", "message": result.get("message")}
    
    def resume_job(self) -> Dict[str, Any]:
        """
        Resume the current job.
        
        Returns:
            dict: Response with status and message
        """
        if not self.current_job or self.current_job.status != "paused":
            return {"status": "error", "message": "No job is paused"}
        
        # Send resume command to Duet
        result = self.duet_client.send_command("M24")
        
        if result.get("status") == "success":
            self.current_job.status = "running"
            logger.info(f"Resumed job {self.current_job.job_id}")
            return {"status": "success", "message": "Job resumed"}
        else:
            logger.error(f"Failed to resume job: {result.get('message')}")
            return {"status": "error", "message": result.get("message")}
    
    def stop_job(self) -> Dict[str, Any]:
        """
        Stop the current job.
        
        Returns:
            dict: Response with status and message
        """
        if not self.current_job or (self.current_job.status != "running" and self.current_job.status != "paused"):
            return {"status": "error", "message": "No job is running or paused"}
        
        # Send stop command to Duet
        result = self.duet_client.send_command("M0")
        
        # Set stop event to terminate job thread
        self.stop_event.set()
        
        if self.job_thread and self.job_thread.is_alive():
            self.job_thread.join(timeout=5)
        
        if result.get("status") == "success":
            self.current_job.status = "stopped"
            self.current_job.end_time = time.time()
            logger.info(f"Stopped job {self.current_job.job_id}")
            return {"status": "success", "message": "Job stopped"}
        else:
            logger.error(f"Failed to stop job: {result.get('message')}")
            return {"status": "error", "message": result.get("message")}
    
    def _run_job(self, job: Job) -> None:
        """
        Run a job in a separate thread.
        
        Args:
            job: Job to run
        """
        try:
            # Send job start commands
            self.duet_client.send_command("M110 N0")  # Reset line numbers
            self.duet_client.send_command("G21")      # Set units to mm
            self.duet_client.send_command("G90")      # Use absolute coordinates
            
            # Open and process G-code file
            with open(job.file_path, 'r') as f:
                lines = f.readlines()
                
                for i, line in enumerate(lines):
                    if self.stop_event.is_set():
                        logger.info(f"Job {job.job_id} stopped")
                        break
                    
                    # Skip empty lines and comments
                    line = line.strip()
                    if not line or line.startswith(';'):
                        continue
                    
                    # Send command to Duet
                    result = self.duet_client.send_command(line)
                    
                    if result.get("status") != "success":
                        job.error = f"Error at line {i+1}: {result.get('message')}"
                        job.status = "failed"
                        logger.error(f"Job {job.job_id} failed: {job.error}")
                        break
                    
                    # Update progress
                    job.current_line = i + 1
                    job.progress = min(100.0, (job.current_line / job.total_lines) * 100) if job.total_lines > 0 else 0
                    
                    # Wait if job is paused
                    while job.status == "paused" and not self.stop_event.is_set():
                        time.sleep(0.5)
            
            # Job completed successfully if not stopped or failed
            if job.status == "running":
                job.status = "completed"
                job.progress = 100.0
                job.end_time = time.time()
                logger.info(f"Job {job.job_id} completed")
        
        except Exception as e:
            job.error = str(e)
            job.status = "failed"
            job.end_time = time.time()
            logger.error(f"Error running job {job.job_id}: {e}")
        
        finally:
            # Send job end commands
            self.duet_client.send_command("M400")  # Wait for moves to complete
            
            # Clear current job if this is still the current job
            if self.current_job and self.current_job.job_id == job.job_id:
                self.current_job = None 