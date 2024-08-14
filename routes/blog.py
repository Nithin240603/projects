from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from config.config import blogs_collection, comments_collection
from bson import ObjectId
import logging
import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the Blog and Comment models using Pydantic
class BlogModel(BaseModel):
    title: str
    content: str
    author_id: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class UpdateBlogModel(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    author_id: Optional[str] = None
    updated_at: Optional[str] = None

class CommentModel(BaseModel):
    post_id: str
    content: str
    author_id: str
    created_at: Optional[str] = None

class UpdateCommentModel(BaseModel):
    content: Optional[str] = None
    author_id: Optional[str] = None

# Define the serializers for blog and comment data
def decode_blog(doc):
    if doc is None:
        return None
    return {
        "id": str(doc["_id"]),
        "title": doc.get("title"),
        "content": doc.get("content"),
        "author_id": str(doc.get("author_id")),
        "created_at": doc.get("created_at"),
        "updated_at": doc.get("updated_at"),
    }

def decode_blogs(docs):
    return [decode_blog(doc) for doc in docs]

def decode_comment(doc):
    if doc is None:
        return None
    return {
        "id": str(doc["_id"]),
        "post_id": str(doc.get("post_id")),
        "content": doc.get("content"),
        "author_id": str(doc.get("author_id")),
        "created_at": doc.get("created_at"),
    }

def decode_comments(docs):
    return [decode_comment(doc) for doc in docs]

blog_root = APIRouter()

# Blog Post Endpoints

@blog_root.post("/posts", response_model=dict)
def create_post(blog: BlogModel):
    try:
        blog_dict = blog.dict(exclude_unset=True)
        if 'created_at' not in blog_dict:
            blog_dict['created_at'] = datetime.datetime.utcnow().isoformat()
        blog_dict['updated_at'] = blog_dict.get('updated_at', blog_dict['created_at'])

        res = blogs_collection.insert_one(blog_dict)
        blog_id = str(res.inserted_id)

        return {
            "status": "success",
            "message": "Post created successfully",
            "data": {
                "id": blog_id,
                "title": blog_dict["title"],
                "content": blog_dict["content"],
                "author_id": blog_dict["author_id"],
                "created_at": blog_dict["created_at"],
                "updated_at": blog_dict["updated_at"]
            }
        }
    except Exception as e:
        logger.error(f"Error creating post: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@blog_root.get("/posts", response_model=dict)
def read_posts():
    try:
        cursor = blogs_collection.find()
        documents = list(cursor)
        decoded_data = decode_blogs(documents)

        return {
            "status": "success",
            "data": decoded_data
        }
    except Exception as e:
        logger.error(f"Error retrieving posts: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@blog_root.get("/posts/{id}", response_model=dict)
def read_single_post(id: str):
    try:
        obj_id = ObjectId(id)
        res = blogs_collection.find_one({"_id": obj_id})

        if res is None:
            raise HTTPException(status_code=404, detail="Post not found")

        decoded_blog = decode_blog(res)

        return {
            "status": "success",
            "data": decoded_blog
        }
    except Exception as e:
        logger.error(f"Error retrieving post with id {id}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@blog_root.put("/posts/{id}", response_model=dict)
def update_post(id: str, updated_blog: UpdateBlogModel):
    try:
        obj_id = ObjectId(id)
        updated_blog_dict = updated_blog.dict(exclude_unset=True)
        if 'updated_at' not in updated_blog_dict:
            updated_blog_dict['updated_at'] = datetime.datetime.utcnow().isoformat()

        result = blogs_collection.update_one({"_id": obj_id}, {"$set": updated_blog_dict})

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Post not found")

        if result.modified_count == 0:
            raise HTTPException(status_code=400, detail="No changes were made")

        updated_document = blogs_collection.find_one({"_id": obj_id})
        if updated_document is None:
            raise HTTPException(status_code=404, detail="Post not found after update")

        decoded_blog = decode_blog(updated_document)

        return {
            "status": "success",
            "data": decoded_blog
        }
    except Exception as e:
        logger.error(f"Error updating post with id {id}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@blog_root.delete("/posts/{id}", response_model=dict)
def delete_post(id: str):
    try:
        obj_id = ObjectId(id)
        result = blogs_collection.delete_one({"_id": obj_id})

        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Post not found")

        return {
            "status": "success",
            "message": "Post deleted successfully"
        }
    except Exception as e:
        logger.error(f"Error deleting post with id {id}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

# Comment Endpoints

@blog_root.post("/comments", response_model=dict)
def create_comment(comment: CommentModel):
    try:
        comment_dict = comment.dict(exclude_unset=True)
        if 'created_at' not in comment_dict:
            comment_dict['created_at'] = datetime.datetime.utcnow().isoformat()

        # Verify that the blog exists before adding the comment
        if not blogs_collection.find_one({"_id": ObjectId(comment_dict["post_id"])}):
            raise HTTPException(status_code=404, detail="Blog not found")

        res = comments_collection.insert_one(comment_dict)
        comment_id = str(res.inserted_id)

        return {
            "status": "success",
            "message": "Comment created successfully",
            "data": {
                "id": comment_id,
                "post_id": comment_dict["post_id"],
                "content": comment_dict["content"],
                "author_id": comment_dict["author_id"],
                "created_at": comment_dict["created_at"]
            }
        }
    except Exception as e:
        logger.error(f"Error creating comment: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@blog_root.get("/comments", response_model=dict)
def read_comments(post_id: str):
    try:
        cursor = comments_collection.find({"post_id": post_id})
        documents = list(cursor)
        decoded_data = decode_comments(documents)

        return {
            "status": "success",
            "data": decoded_data
        }
    except Exception as e:
        logger.error(f"Error retrieving comments for post_id {post_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@blog_root.get("/comments/{id}", response_model=dict)
def read_single_comment(id: str):
    try:
        obj_id = ObjectId(id)
        res = comments_collection.find_one({"_id": obj_id})

        if res is None:
            raise HTTPException(status_code=404, detail="Comment not found")

        decoded_comment = decode_comment(res)

        return {
            "status": "success",
            "data": decoded_comment
        }
    except Exception as e:
        logger.error(f"Error retrieving comment with id {id}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@blog_root.put("/comments/{id}", response_model=dict)
def update_comment(id: str, updated_comment: UpdateCommentModel):
    try:
        obj_id = ObjectId(id)
        updated_comment_dict = updated_comment.dict(exclude_unset=True)

        result = comments_collection.update_one({"_id": obj_id}, {"$set": updated_comment_dict})

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Comment not found")

        if result.modified_count == 0:
            raise HTTPException(status_code=400, detail="No changes were made")

        updated_document = comments_collection.find_one({"_id": obj_id})
        if updated_document is None:
            raise HTTPException(status_code=404, detail="Comment not found after update")

        decoded_comment = decode_comment(updated_document)

        return {
            "status": "success",
            "data": decoded_comment
        }
    except Exception as e:
        logger.error(f"Error updating comment with id {id}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@blog_root.delete("/comments/{id}", response_model=dict)
def delete_comment(id: str):
    try:
        obj_id = ObjectId(id)
        result = comments_collection.delete_one({"_id": obj_id})

        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Comment not found")

        return {
            "status": "success",
            "message": "Comment deleted successfully"
        }
    except Exception as e:
        logger.error(f"Error deleting comment with id {id}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
