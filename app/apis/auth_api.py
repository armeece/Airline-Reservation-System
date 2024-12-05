from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from bson.objectid import ObjectId
from app import mongo_db

# ===================================
# Blueprint for Authentication APIs
# ===================================
auth_blueprint = Blueprint('auth_api', __name__)

# ===================================
# Utility to Enforce RBAC
# ===================================
def role_required(role_name):
    """Decorator to restrict access to users with a specific role."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            user_roles = current_user.role if isinstance(current_user.role, list) else [current_user.role]
            if role_name not in user_roles:
                return jsonify({"error": f"Access denied: {role_name} role required"}), 403
            return func(*args, **kwargs)
        wrapper.__name__ = f"{func.__name__}_{role_name}"  # Ensure unique function names
        return wrapper
    return decorator

# ===================================
# Role Management Endpoints
# ===================================
@auth_blueprint.route('/create-role', methods=['POST'], endpoint='create_role')
@login_required
@role_required('admin')
def create_role():
    """Create a new role."""
    data = request.get_json()
    role_name = data.get('name')
    description = data.get('description', '')

    if not role_name:
        return jsonify({'error': 'Role name is required'}), 400

    roles_collection = mongo_db.get_collection('roles')
    if roles_collection.find_one({"name": role_name}):
        return jsonify({'error': f'Role {role_name} already exists'}), 400

    roles_collection.insert_one({"name": role_name, "description": description})
    return jsonify({'message': f'Role {role_name} created successfully!'}), 201

@auth_blueprint.route('/assign-role', methods=['POST'], endpoint='assign_role')
@login_required
@role_required('admin')
def assign_role():
    """Assign a role to a user."""
    data = request.get_json()
    user_id = data.get('user_id')
    role_name = data.get('role_name')

    if not user_id or not role_name:
        return jsonify({'error': 'User ID and role name are required'}), 400

    users_collection = mongo_db.get_collection('users')
    roles_collection = mongo_db.get_collection('roles')

    user = users_collection.find_one({"_id": ObjectId(user_id)})
    role = roles_collection.find_one({"name": role_name})

    if not user or not role:
        return jsonify({'error': 'User or role not found'}), 404

    if role_name in user.get("roles", []):
        return jsonify({'error': f'User already has role {role_name}'}), 400

    users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$addToSet": {"roles": role_name}}
    )
    return jsonify({'message': f'Role {role_name} assigned to user {user["email"]}'}), 200

@auth_blueprint.route('/check-role', methods=['GET'], endpoint='check_role')
@login_required
def check_role():
    """Check if the current user has a specific role."""
    role_name = request.args.get('role_name')

    if not role_name:
        return jsonify({'error': 'Role name is required'}), 400

    has_role = role_name in current_user.role if isinstance(current_user.role, list) else current_user.role == role_name
    return jsonify({'has_role': has_role}), 200

# ===================================
# Permission Management Endpoints
# ===================================
@auth_blueprint.route('/create-permission', methods=['POST'], endpoint='create_permission')
@login_required
@role_required('admin')
def create_permission():
    """Create a new permission."""
    data = request.get_json()
    permission_name = data.get('name')
    description = data.get('description', '')

    if not permission_name:
        return jsonify({'error': 'Permission name is required'}), 400

    permissions_collection = mongo_db.get_collection('permissions')
    if permissions_collection.find_one({"name": permission_name}):
        return jsonify({'error': f'Permission {permission_name} already exists'}), 400

    permissions_collection.insert_one({"name": permission_name, "description": description})
    return jsonify({'message': f'Permission {permission_name} created successfully!'}), 201

@auth_blueprint.route('/assign-permission', methods=['POST'], endpoint='assign_permission')
@login_required
@role_required('admin')
def assign_permission():
    """Assign a permission to a role."""
    data = request.get_json()
    role_name = data.get('role_name')
    permission_name = data.get('permission_name')

    if not role_name or not permission_name:
        return jsonify({'error': 'Role name and permission name are required'}), 400

    roles_collection = mongo_db.get_collection('roles')
    permissions_collection = mongo_db.get_collection('permissions')

    role = roles_collection.find_one({"name": role_name})
    permission = permissions_collection.find_one({"name": permission_name})

    if not role or not permission:
        return jsonify({'error': 'Role or permission not found'}), 404

    if permission_name in role.get("permissions", []):
        return jsonify({'error': f'Role already has permission {permission_name}'}), 400

    roles_collection.update_one(
        {"name": role_name},
        {"$addToSet": {"permissions": permission_name}}
    )
    return jsonify({'message': f'Permission {permission_name} assigned to role {role_name}'}), 200
