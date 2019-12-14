from django.shortcuts import render,redirect,reverse
from django.http import HttpResponse

from django.contrib.auth import login,logout,authenticate
from django.views.decorators.http import require_POST
from .forms import LoginForm,RegisterForm,UserForm
from django.http import JsonResponse
from django.views import View
from apps.whursauth.models import User


rank_list = ['编译原理','算法','计算机组成原理','微机接口','模式识别','machine learning']
persons = {
    'hjw': {'image': 'image/hjw.jpg', 'text': '11111111'},
    'zyr': {'image': 'image/zyr.jpg', 'text': '22222222'},
    'djc': {'image': 'image/djc.jpg', 'text': '33333333'},
    'xzy': {'image': 'image/xzy.jpg', 'text': '44444444'},
}
context = {
    'rank_list': rank_list,
    'persons': persons
}
# login的视图类
class LoginView(View):
    # get方式访问直接返回渲染的模板
    def get(self,request):
        return render(request,'base/login.html')

    # post方法就是提交表单，对表单进行相应的处理
    def post(self,request):
        form = LoginForm(request.POST)
        if form.is_valid():
            std_id = form.cleaned_data.get('std_id')
            password = form.cleaned_data.get('password')
            # 这里可以添加remember，是否记住我
            remember = form.cleaned_data.get('remember')
            user = authenticate(request, username=std_id, password=password)
            if user:
                if user.is_active:
                    login(request, user)
                    request.session['std_id'] = std_id
                    if remember:
                        request.session.set_expiry(None)
                    else:
                        # 立刻过期
                        request.session.set_expiry(0)
                    # 关于返回值，和前端人员约定好，看p245
                    # return render(request,'base/index.html',context=context)
                    return redirect(reverse('base:base_index'))
                else:
                    # return JsonResponse({'code': 405, 'message': '账号不是active', 'data': {}})
                    return HttpResponse('账号未激活')
            else:
                # return JsonResponse({'code': 400, 'message': '学号或者密码错误', 'data': {}})
                return HttpResponse('学号密码错误')
        else:
            errors = form.get_errors()
            return JsonResponse({'code': 400, 'message': '', 'data': errors})


class RegisterView(View):
    def get(self,request):
        return render(request,'base/signup.html')

    def post(self,request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            std_id = form.cleaned_data.get('std_id')
            username = form.cleaned_data.get('username')
            telephone = form.cleaned_data.get('telephone')
            email = form.cleaned_data.get('email')
            print(email)
            password = form.cleaned_data.get('password')
            print(password)
            # 创建用户
            User.objects.create_user(std_id,username,password,telephone=telephone,email=email)
            return HttpResponse('创建成功')
        else:
            errors = form.get_errors()
            return JsonResponse({'code':499,'message':'','data':errors})



def index(request):
    return render(request,'base/index.html',context=context)


def user_page(request,user_id):
    return render(request,'base/user.html',context={'user_id':user_id})

def reveive_protrait(request):
    form = UserForm(request.POST,request.FILES)
    if form.is_valid():
        portrait = form.cleaned_data.get('portrait')
        std_id = request.session.get('std_id')
        user = User.objects.get(std_id=std_id)
        user.portrait = portrait
        user.save()
        return HttpResponse(str(user.portrait))
    else:
        return HttpResponse('不行')


def user_logout(request):
    logout(request)
    return redirect(reverse('base:base_index'))