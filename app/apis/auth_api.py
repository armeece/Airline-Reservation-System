from flask import Blueprint, request, jsonify
from app import db
from app.models import User, Role, Permission
from flask_login import login_required, current_user

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
            if role_name not in [role.name for role in current_user.roles]:
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
    description = data.get('description')

    if not role_name:
        return jsonify({'error': 'Role name is required'}), 400

    role = Role(name=role_name)
    if description:
        role.description = description

    db.session.add(role)
    db.session.commit()
    return jsonify({'message': f'Role {role_name} created successfully!'}), 201

@auth_blueprint.route('/assign-role', methods=['POST'], endpoint='assign_role')
@login_required
@role_required('admin')
def assign_role():
    """Assign a role to a user."""
    data = request.get_json()
    user_id = data.get('user_id')
    role_name = data.get('role_name')

    user = User.query.get(user_id)
    role = Role.query.filter_by(name=role_name).first()

    if not user or not role:
        return jsonify({'error': 'User or role not found'}), 404

    if role not in user.roles:
        user.roles.append(role)
        db.session.commit()
        return jsonify({'message': f'Role {role_name} assigned to user {user.username}'}), 200

    return jsonify({'error': f'User already has role {role_name}'}), 400

@auth_blueprint.route('/check-role', methods=['GET'], endpoint='check_role')
@login_required
def check_role():
    """Check if the current user has a specific role."""
    role_name = request.args.get('role_name')

    if not role_name:
        return jsonify({'error': 'Role name is required'}), 400

    has_role = any(role.name == role_name for role in current_user.roles)
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
    description = data.get('description')

    if not permission_name:
        return jsonify({'error': 'Permission name is required'}), 400

    permission = Permission(name=permission_name)
    if description:
        permission.description = description

    db.session.add(permission)
    db.session.commit()
    return jsonify({'message': f'Permission {permission_name} created successfully!'}), 201

@auth_blueprint.route('/assign-permission', methods=['POST'], endpoint='assign_permission')
@login_required
@role_required('admin')
def assign_permission():
    """Assign a permission to a role."""
    data = request.get_json()
    role_name = data.get('role_name')
    permission_name = data.get('permission_name')

    role = Role.query.filter_by(name=role_name).first()
    permission = Permission.query.filter_by(name=permission_name).first()

    if not role or not permission:
        return jsonify({'error': 'Role or permission not found'}), 404

    if permission not in role.permissions:
        role.permissions.append(permission)
        db.session.commit()
        return jsonify({'message': f'Permission {permission_name} assigned to role {role.name}'}), 200

    return jsonify({'error': f'Role already has permission {permission_name}'}), 400
