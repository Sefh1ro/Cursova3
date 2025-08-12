from repositories.user_repository import UserRepository
from models.user import User

class UserService:
    @staticmethod
    def get_all_users():
        return UserRepository.get_all()

    @staticmethod
    def create_user(name, password):
        if UserRepository.get_by_name(name):
            return None
        user = User(name=name)
        user.set_password(password)
        return UserRepository.save(user)

    @staticmethod
    def update_user(user_id, data):
        user = UserRepository.get_by_id(user_id)
        if 'name' in data:
            user.name = data['name']
        if 'password' in data:
            user.set_password(data['password'])
        return UserRepository.save(user)

    @staticmethod
    def delete_user(user_id):
        user = UserRepository.get_by_id(user_id)
        UserRepository.delete(user)
