from repositories.user_repository import UserRepository

class AuthService:
    @staticmethod
    def authenticate(username, password):
        user = UserRepository.get_by_name(username)
        if user and user.check_password(password):
            return user
        return None
