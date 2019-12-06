from django.shortcuts import render,redirect,reverse
from django.http import HttpResponse

from django.contrib.auth import login,logout,authenticate
from django.views.decorators.http import require_POST
from .forms import LoginForm,RegisterForm
from django.http import JsonResponse
from django.views import View
from apps.whursauth.models import User


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
                    # return JsonResponse({'code': 200, 'message': '', 'data': {}})
                    rank_list = ['编译原理','算法','计算机组成原理','微机接口','模式识别']
                    return render(request,'base/index.html',context={'rank_list':rank_list})
                else:
                    return JsonResponse({'code': 405, 'message': '账号不是active', 'data': {}})
            else:
                return JsonResponse({'code': 400, 'message': '学号或者密码错误', 'data': {}})
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

    rank_list = ['编译原理', '算法', '计算机组成原理', '微机接口', '模式识别']

    persons = {
        'hjw' : {'image':'image/hjw.jpg','text':'11111111'},
        'zyr' : {'image':'image/zyr.jpg','text':'22222222'},
        'djc' : {'image':'image/djc.jpg','text':'33333333'},
        'xzy' : {'image':'image/xzy.jpg','text':'44444444'},
    }
    context = {
        'rank_list': rank_list,
        'persons': persons
    }
    return render(request,'base/index.html',context=context)


def user_page(request):
    return render(request,'base/user.html')