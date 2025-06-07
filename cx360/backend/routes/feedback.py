from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

# Database and session
from cx360.backend.database import get_db

# Models and Schemas
from cx360.backend.models.feedback import Feedback, FeedbackCreate, FeedbackUpdate, FeedbackResponse
from cx360.backend.models.user import User as UserModel # SQLAlchemy User model
# Auth dependencies
from cx360.backend.routes.auth import get_current_active_user # Adjusted import path

router = APIRouter(
    prefix="/feedback",
    tags=["Feedback"],
    # dependencies=[Depends(get_current_active_user)] # Optional: protect all feedback routes
)

# Placeholder for CRUD operations / helper functions
# These can be moved to a separate crud_feedback.py file later for better organization

def db_create_feedback(db: Session, feedback_in: FeedbackCreate, user_id: Optional[int] = None) -> Feedback:
    db_feedback = Feedback(**feedback_in.model_dump(exclude_unset=True)) # Use model_dump for Pydantic v2
    if user_id:
        db_feedback.user_id = user_id
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    return db_feedback

def db_get_feedback(db: Session, feedback_id: int) -> Optional[Feedback]:
    return db.query(Feedback).filter(Feedback.id == feedback_id).first()

def db_get_all_feedback(db: Session, skip: int = 0, limit: int = 100) -> List[Feedback]:
    return db.query(Feedback).offset(skip).limit(limit).all()

def db_update_feedback(db: Session, feedback_id: int, feedback_in: FeedbackUpdate, current_user: UserModel) -> Optional[Feedback]:
    db_feedback = db_get_feedback(db, feedback_id)
    if not db_feedback:
        return None

    # Authorization check: Only owner or admin can update (Example)
    # For this, you might need to define roles in your User model and check current_user.role
    # For now, let's assume if user_id is present, only that user can update.
    # This is a simplified check. A more robust system would involve roles/permissions.
    if db_feedback.user_id is not None and db_feedback.user_id != current_user.id:
         # Or if current_user.role != "admin" (pseudo-code for role check)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this feedback")

    update_data = feedback_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_feedback, key, value)

    db.commit()
    db.refresh(db_feedback)
    return db_feedback

def db_delete_feedback(db: Session, feedback_id: int, current_user: UserModel) -> Optional[Feedback]:
    db_feedback = db_get_feedback(db, feedback_id)
    if not db_feedback:
        return None

    # Authorization check (similar to update)
    if db_feedback.user_id is not None and db_feedback.user_id != current_user.id:
        # Or if current_user.role != "admin"
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this feedback")

    db.delete(db_feedback)
    db.commit()
    return db_feedback # Return the deleted object for confirmation, or just True


# --- CSV Upload Endpoint ---
import csv
import io
from fastapi import File, UploadFile # Ensure File and UploadFile are imported from fastapi
from pydantic import BaseModel, ValidationError # Ensure ValidationError is available for more specific error handling
from datetime import datetime # Ensure datetime is available

# Import the Pydantic model for CSV row validation
from cx360.backend.models.feedback import FeedbackCsvRow
# FeedbackSQLModel is already imported as 'Feedback' in this file

class CsvImportErrorDetail(BaseModel):
    row_number: int
    error_message: str
    row_data: dict

class CsvImportResponse(BaseModel):
    successful_imports: int
    failed_rows: int
    errors: List[CsvImportErrorDetail]


@router.post("/upload-csv", response_model=CsvImportResponse, status_code=status.HTTP_201_CREATED)
async def upload_feedback_csv(
    csv_file: UploadFile = File(...), # Use File(...) for UploadFile
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user) # UserModel is already imported as User
):
    if not csv_file.filename.endswith('.csv'):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid file type. Please upload a CSV file.")

    content = await csv_file.read()
    try:
        text_content = content.decode('utf-8')
    except UnicodeDecodeError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid file encoding. Please use UTF-8.")

    reader = csv.DictReader(io.StringIO(text_content))

    successful_imports = 0
    failed_rows_count = 0
    errors_list: List[CsvImportErrorDetail] = [] # Use the Pydantic model for errors list

    # Define expected headers for better error messaging if needed, though DictReader handles it.
    # Minimum required headers for FeedbackCsvRow are 'rating' and 'feedback_text'.
    if not reader.fieldnames or not ('rating' in reader.fieldnames and 'feedback_text' in reader.fieldnames):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CSV headers are missing or incorrect. Essential headers are 'rating' and 'feedback_text'."
        )

    for i, row_data in enumerate(reader):
        row_number = i + 2 # Account for header row (1-based) and DictReader's first data row

        # Clean row_data: remove None values or empty strings for optional fields
        # to prevent Pydantic from trying to validate them if they are truly optional.
        # Also, ensure keys passed to Pydantic model are only those defined in FeedbackCsvRow.
        processed_row_data = {
            k: v for k, v in row_data.items()
            if k in FeedbackCsvRow.model_fields and v is not None and v != ""
        }

        try:
            # Pydantic will attempt to parse 'rating' to int and 'created_at' to datetime
            # based on FeedbackCsvRow type hints.
            csv_row_model = FeedbackCsvRow(**processed_row_data)

            # Create SQLAlchemy model instance
            # Note: csv_row_model.created_at will be a datetime object if parsing succeeded.
            # FeedbackSQLModel expects datetime object for created_at.
            feedback_db_entry = Feedback( # Assuming Feedback is the SQLAlchemy model alias
                **csv_row_model.model_dump(exclude_unset=True),
                user_id=current_user.id # Associate with the uploader
            )
            db.add(feedback_db_entry)
            successful_imports += 1

        except ValidationError as ve: # Catch Pydantic's validation errors
            failed_rows_count += 1
            # Extract more user-friendly error messages from ve.errors()
            error_messages = "; ".join([f"{err['loc'][0]}: {err['msg']}" for err in ve.errors()])
            errors_list.append(CsvImportErrorDetail(
                row_number=row_number,
                error_message=error_messages,
                row_data=row_data
            ))
        except Exception as e: # Catch other errors like type conversion during manual parsing (if any)
            failed_rows_count += 1
            errors_list.append(CsvImportErrorDetail(
                row_number=row_number,
                error_message=f"Unexpected error: {str(e)}",
                row_data=row_data
            ))

    if successful_imports > 0:
        try:
            db.commit()
        except Exception as e: # Handle potential commit errors (e.g. database constraints if not caught by Pydantic)
            db.rollback()
            # This is tricky: some might have been valid, some caused DB error.
            # For simplicity here, we'll treat commit failure as a general error.
            # A more robust solution might try to save valid ones in batches or individually.
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database commit error: {str(e)}")


    # If there were failures, the status code could be 207 Multi-Status,
    # but 201 is also acceptable if some records were created.
    # For simplicity, keeping 201 if any import was successful.
    # If all failed, perhaps return 400 or 422 based on type of common error.

    return CsvImportResponse(
        successful_imports=successful_imports,
        failed_rows=failed_rows_count,
        errors=errors_list
    )

# --- CSV Export Endpoint ---
from fastapi.responses import StreamingResponse # Add this import
# `csv`, `io`, `datetime` are already imported for the upload endpoint or standard library.
# `UserModel` (SQLAlchemy User model) is imported as `User` at the top of the file.
# `Feedback` (SQLAlchemy Feedback model) is also already imported.

@router.get("/export-csv", response_class=StreamingResponse)
async def export_feedback_csv(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user) # Ensure only auth users can export
):
    # Query feedback data, joining with User table for submitter's username
    # UserModel is aliased as User in this file.
    feedback_query = (
        db.query(
            Feedback.id,
            Feedback.customer_name,
            Feedback.email,
            Feedback.rating,
            Feedback.feedback_text,
            Feedback.source,
            Feedback.created_at,
            Feedback.user_id, # Keep uploader's user_id
            UserModel.username.label("submitter_username")
        )
        .outerjoin(UserModel, Feedback.user_id == UserModel.id) # outerjoin in case user_id is null
        .order_by(Feedback.created_at.desc())
    )

    all_feedback_records = feedback_query.all()

    output_buffer = io.StringIO()
    csv_writer = csv.writer(output_buffer)

    # Define CSV headers
    headers = [
        "id", "customer_name", "email", "rating", "feedback_text",
        "source", "created_at", "user_id", "submitter_username"
    ]
    csv_writer.writerow(headers)

    for record in all_feedback_records:
        row_data = [
            record.id,
            record.customer_name,
            record.email,
            record.rating,
            record.feedback_text,
            record.source,
            record.created_at.isoformat() if record.created_at else None, # Format datetime
            record.user_id,
            record.submitter_username
        ]
        csv_writer.writerow(row_data)

    output_buffer.seek(0) # Reset buffer position to the beginning

    response_filename = f"feedback_export_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.csv"
    response_headers = {
        "Content-Disposition": f"attachment; filename={response_filename}"
    }

    return StreamingResponse(
        iter([output_buffer.getvalue()]), # StreamingResponse expects an iterator
        media_type="text/csv",
        headers=response_headers
    )

# --- CRUD Endpoints ---

# Create Feedback
@router.post("/", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
def create_feedback(
    feedback_in: FeedbackCreate,
    db: Session = Depends(get_db),
    current_user: Optional[UserModel] = Depends(get_current_active_user) # Make current_user optional
):
    # If current_user is None and feedback_in.user_id is also None, it's anonymous
    # If current_user is provided, we can link the feedback to this user
    user_id_to_set = None
    if current_user:
        user_id_to_set = current_user.id
    elif feedback_in.user_id: # Allow specifying user_id if not logged in (e.g. by admin)
        # Potentially add a check here: only admins can set user_id for others
        user_id_to_set = feedback_in.user_id

    # To ensure feedback_in.user_id (if present in body) is not overriding current_user.id unless intended
    if current_user and feedback_in.user_id and feedback_in.user_id != current_user.id:
        # This case might need clarification: if logged in user specifies different user_id
        # For now, prioritize current_user.id if logged in.
        # Or raise HTTPException if admin role is not present
        pass # Assuming current_user's ID should be authoritative if logged in.

    created_feedback = db_create_feedback(db=db, feedback_in=feedback_in, user_id=user_id_to_set)
    return created_feedback

# Read One Feedback
@router.get("/{feedback_id}", response_model=FeedbackResponse)
def read_feedback(feedback_id: int, db: Session = Depends(get_db)):
    db_feedback = db_get_feedback(db, feedback_id=feedback_id)
    if db_feedback is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feedback not found")
    return db_feedback

# Read Multiple Feedback
@router.get("/", response_model=List[FeedbackResponse])
def read_all_feedback(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    feedbacks = db_get_all_feedback(db, skip=skip, limit=limit)
    return feedbacks

# Update Feedback
@router.put("/{feedback_id}", response_model=FeedbackResponse)
def update_feedback(
    feedback_id: int,
    feedback_in: FeedbackUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user) # Require authentication
):
    updated_feedback = db_update_feedback(db, feedback_id, feedback_in, current_user)
    if updated_feedback is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feedback not found or not authorized to update")
    return updated_feedback

# Delete Feedback
@router.delete("/{feedback_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_feedback(
    feedback_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user) # Require authentication
):
    deleted_feedback = db_delete_feedback(db, feedback_id, current_user)
    if deleted_feedback is None:
        # This means either not found or not authorized by the check in db_delete_feedback
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feedback not found or not authorized to delete")
    return # FastAPI will return 204 No Content
