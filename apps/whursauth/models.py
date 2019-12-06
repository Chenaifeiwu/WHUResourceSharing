from django.db import models
from django.contrib.auth.models import AbstractBaseUser,PermissionsMixin,BaseUserManager
from shortuuidfield import ShortUUIDField

class UserManager(BaseUserManager):
    def _create_user(self,std_id,username,password,**kwargs):
        if not std_id:
            raise ValueError('需要传入学号')
        if not username:
            raise ValueError('需要传入用户名')
        if not password:
            raise ValueError('需要传入密码')

        user = self.model(std_id=std_id,username=username,**kwargs)
        user.set_password(password)
        user.save()
        return user

    def create_user(self,std_id,username,password,**kwargs):
        # 创建普通用户
        kwargs['is_superuser'] = False
        return self._create_user(std_id,username,password,**kwargs)

    def create_superuser(self,std_id,username,password,**kwargs):
        kwargs['is_superuser'] = True
        return self._create_user(std_id,username,password,**kwargs)



class User(AbstractBaseUser,PermissionsMixin):
    # 不使用默认增长主键
    # 使用shortuuid
    uid = ShortUUIDField(primary_key=True)
    telephone = models.CharField(max_length=11,unique=True)
    # password = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    # is_staff表示是否是员工 是否能登陆到后台管理系统
    is_staff = models.BooleanField(default=False)
    # 什么时候加入
    date_joined = models.DateTimeField(auto_now_add=True)

    ## 本次项目独有的字段
    # 学号
    std_id = models.CharField(max_length=13,unique=True)
    # 学院
    school = models.CharField(max_length=15)
    # 积分
    points = models.IntegerField(default=0)
    ##
    # 作为唯一字段进行验证，不设置的话默认是username

    '''By DJC on 2019.12.3'''
    upload_history = models.CharField(max_length=1000)
    # History of files the user uploaded, identified by uuid and separated by a comma(or space)
    # As there is a 'is_valid' field in Source object, even if the file is not valid, we don't need to edit this history
    # What if it reached the max size?

    download_history = models.CharField(max_length=500)
    # History of files the user downloaded, the same as upload_history
    '''END'''

    USERNAME_FIELD = 'std_id'
    REQUIRED_FIELDS = ['username','telephone','email']
    EMAIL_FIELD = 'email'

    objects = UserManager()

    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username


class Resource(models.Model):
    """
    Fields:
    uid: primary key
    title: title of this resource
    abs_url: absolute url of this on server. Maybe we need to rename it to make it shorter
    upload_time:
    update_user: a foreign key referring to User.uid
    description: not necessary
    is_valid: Whether managers or the owner can set this field and if the file is broken ,we set it false.
    download_count:
    tag: I'm considering if this is necessary here, maybe another table is needed to create.
    """
    uid = ShortUUIDField(primary_key=True)
    title = models.CharField(max_length=40)  # I don't make it unique so we need to rename the real file on server
    abs_url = models.CharField(max_length=60, unique=True)
    upload_time = models.DateTimeField(auto_now_add=True)
    upload_user = models.ForeignKey('User', on_delete='CASCADE')

    description = models.CharField(max_length=140, default="")
    download_count = models.IntegerField()
    is_valid = models.BooleanField(default=True)

    tag = models.CharField(max_length=20)  # TBD


class TagList(models.Model):
    """
    At first some tags should be inserted by managers.
    Maybe users can add new tags.
    uuid is abandoned because there won't be two tags with the same name.

    Fields:
    tag_name: primary key
    link_count: Update this once any file is linked or unlinked.
    (link_count is useful when we do recommendation, the same as Resource.download_count)
    """
    tag_name = models.CharField(max_length=20, primary_key=True)
    link_count = models.IntegerField()


class TagResourceLink(models.Model):
    """
    When user is searching for files but not specifically, he can look into these tags.
    Although we don't have to make our directory tree like this:
    --root
      --tag1
        --file1
        --file2
      --tag2
        --file3
        --file4
        ...
    at the front, a structure like this might be displayed by this table.
    Fields:
    tag_name:
    resource:
    """
    tag_name = models.ForeignKey('TagList', on_delete='CASCADE')
    resource = models.ForeignKey("Resource", on_delete='CASCADE')

    class Meta:
        unique_together = ('tag_name', 'resource')


