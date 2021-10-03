from flask_login import current_user

ADMIN_ROLE_ID = 1

def is_admin():
    return current_user.role_id == ADMIN_ROLE_ID

class UsersPolicy:
    def __init__(self, record=None):
        self.record = record

    def edit(self):
        is_users_page = current_user.id == self.record.id
        return is_admin() or is_users_page

    def editgame(self):
        return is_admin()

    def show(self):
        try:
            is_users_page = current_user.id == self.record.id
            return is_admin() or is_users_page
        except AttributeError:
            return False     

    def new(self):
        return is_admin()

    def delete(self):
        return is_admin()
    
    def admin_rights(self):
        return is_admin()