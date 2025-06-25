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
        self.status_callback = None
        
        # Create upload folder if it doesn't exist
        os.makedirs(self.upload_folder, exist_ok=True)
        
        # Load existing jobs from upload folder
        self._load_existing_jobs()
    
    def set_status_callback(self, callback_function):
        """
        Set a callback function to be called when job status changes.
        
        Args:
            callback_function: Function to call with job data
        """
        self.status_callback = callback_function
        logger.info("Job status callback set")
    
    def _notify_status_change(self, job: Job):
        """
        Notify status change via callback.
        
        Args:
            job: Job that changed status
        """
        if self.status_callback and callable(self.status_callback):
            try:
                self.status_callback(job.to_dict())
            except Exception as e:
                logger.error(f"Error in status callback: {e}")
    
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
        
        if self.current_job:
            return {"status": "error", "message": "A job is already running"}
        
        try:
            # Set job status to running
            job.status = "running"
            job.progress = 0.0
            job.start_time = time.time()
            job.end_time = None
            job.current_line = 0
            job.error = None
            
            # Set as current job
            self.current_job = job
            
            # Reset stop event
            self.stop_event.clear()
            
            # Start job thread
            self.job_thread = threading.Thread(target=self._run_job, args=(job,))
            self.job_thread.daemon = True
            self.job_thread.start()
            
            # Notify status change
            self._notify_status_change(job)
            
            logger.info(f"Started job {job_id}")
            return {"status": "success", "message": f"Job {job_id} started"}
        
        except Exception as e:
            logger.error(f"Error starting job {job_id}: {e}")
            job.status = "failed"
            job.error = str(e)
            
            # Notify status change
            self._notify_status_change(job)
            
            return {"status": "error", "message": str(e)}
    
    def pause_job(self) -> Dict[str, Any]:
        """
        Pause the current job.
        
        Returns:
            dict: Response with status and message
        """
        if not self.current_job:
            return {"status": "error", "message": "No job is running"}
        
        try:
            # Set job status to paused
            self.current_job.status = "paused"
            
            # Notify status change
            self._notify_status_change(self.current_job)
            
            logger.info(f"Paused job {self.current_job.job_id}")
            return {"status": "success", "message": "Job paused"}
        
        except Exception as e:
            logger.error(f"Error pausing job: {e}")
            return {"status": "error", "message": str(e)}
    
    def resume_job(self) -> Dict[str, Any]:
        """
        Resume the current job.
        
        Returns:
            dict: Response with status and message
        """
        if not self.current_job:
            return {"status": "error", "message": "No job is paused"}
        
        if self.current_job.status != "paused":
            return {"status": "error", "message": "Job is not paused"}
        
        try:
            # Set job status to running
            self.current_job.status = "running"
            
            # Notify status change
            self._notify_status_change(self.current_job)
            
            logger.info(f"Resumed job {self.current_job.job_id}")
            return {"status": "success", "message": "Job resumed"}
        
        except Exception as e:
            logger.error(f"Error resuming job: {e}")
            return {"status": "error", "message": str(e)}
    
    def stop_job(self) -> Dict[str, Any]:
        """
        Stop the current job.
        
        Returns:
            dict: Response with status and message
        """
        if not self.current_job:
            return {"status": "error", "message": "No job is running"}
        
        try:
            # Set stop event
            self.stop_event.set()
            
            # Wait for job thread to finish
            if self.job_thread and self.job_thread.is_alive():
                self.job_thread.join(timeout=5)
            
            # Set job status to stopped
            self.current_job.status = "stopped"
            self.current_job.end_time = time.time()
            
            # Notify status change
            self._notify_status_change(self.current_job)
            
            # Clear current job
            job_id = self.current_job.job_id
            self.current_job = None
            
            logger.info(f"Stopped job {job_id}")
            return {"status": "success", "message": "Job stopped"}
        
        except Exception as e:
            logger.error(f"Error stopping job: {e}")
            return {"status": "error", "message": str(e)}
    
    def _run_job(self, job: Job) -> None:
        """
        Run a job in a separate thread.
        
        Args:
            job: Job to run
        """
        try:
            # Open G-code file
            with open(job.file_path, 'r') as f:
                lines = f.readlines()
            
            # Process each line
            for i, line in enumerate(lines):
                # Check if stop event is set
                if self.stop_event.is_set():
                    logger.info(f"Job {job.job_id} stopped")
                    return
                
                # Check if job is paused
                while job.status == "paused" and not self.stop_event.is_set():
                    time.sleep(0.1)
                
                # Skip empty lines and comments
                line = line.strip()
                if not line or line.startswith(';'):
                    continue
                
                # Send G-code command
                try:
                    result = self.duet_client.send_gcode(line)
                    logger.debug(f"Sent command: {line}, result: {result}")
                    
                    # If command is M400 (wait for moves to complete), wait for it
                    if line.startswith('M400'):
                        self.duet_client.wait_for_motion_complete()
                    
                except Exception as e:
                    logger.error(f"Error sending command {line}: {e}")
                    job.error = f"Error at line {i+1}: {str(e)}"
                    job.status = "failed"
                    job.end_time = time.time()
                    
                    # Notify status change
                    self._notify_status_change(job)
                    
                    return
                
                # Update job progress
                job.current_line = i + 1
                job.progress = (i + 1) / len(lines) * 100
                
                # Notify status change every 1% progress change or every 10 lines
                if i % 10 == 0 or int(job.progress) > int((i / len(lines)) * 100):
                    self._notify_status_change(job)
                
                # Small delay to prevent overwhelming the controller
                time.sleep(0.01)
            
            # Job completed successfully
            job.status = "completed"
            job.progress = 100.0
            job.end_time = time.time()
            
            # Notify status change
            self._notify_status_change(job)
            
            logger.info(f"Job {job.job_id} completed")
            
            # Clear current job
            self.current_job = None
            
        except Exception as e:
            logger.error(f"Error running job {job.job_id}: {e}")
            job.status = "failed"
            job.error = str(e)
            job.end_time = time.time()
            
            # Notify status change
            self._notify_status_change(job)
            
            # Clear current job
            self.current_job = None 